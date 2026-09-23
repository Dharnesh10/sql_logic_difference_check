"""
migration_pipeline.py
======================

FastTrack -> Firebird migration: crosspollination analysis pipeline.

Runs top-to-bottom in ANY environment -- a plain IDE ("Run" button /
`python migration_pipeline.py`), a Jupyter kernel, or pasted into a
Databricks notebook cell and run. No CLI args, no widgets: every input
and output is a plain variable in the CONFIG block below.

WHAT IT DOES
------------
For every "rule" that appears across your clients, it determines whether
the Firebird logic is:

  - CROSSPOLLINATE : identical logic in every client that has it
                      -> migrate once, one RuleID, reused everywhere.
  - VERSION        : same underlying "shape" (same tables/join family)
                      but the filtering logic differs across clients
                      -> migrate as one base rule with N versions/RuleIDs.
  - STANDALONE     : only exists in one client
                      -> migrate directly with its own RuleID, no
                      crosspollination is possible.
  - NEEDS REVIEW   : same rule *name* across clients, but the logic is
                      structurally unrelated (different tables/joins
                      entirely) -> almost certainly a naming collision;
                      flagged for a human to resolve before assigning
                      RuleIDs, rather than silently guessing.

It also produces a migration-sequencing report: which rules to migrate
first (highest client coverage per unit of effort) and which client to
onboard first (highest overlap with already-common logic), so the
migration order minimizes rework and cost.

INPUT MODES (fill in exactly ONE, leave the other blank/empty)
----------------------------------------------------------------
MODE 1 - MASTER_INPUT: one wide table/file, already in the shape
    rule_name | firebird_logic_<client1> | firebird_logic_<client2> | ...
    (one row per rule, one column per client holding that client's
    Firebird SQL text, blank/NULL where the rule doesn't exist for that
    client). This mirrors your existing presence-matrix master sheet,
    except cells hold SQL text instead of 1/blank.

MODE 2 - CLIENT_INPUTS: a list of one table/file PER CLIENT, each in the
    long shape:  rule_name | client_name | firebird_logic
    (client_name is constant within each client's own table/file). The
    pipeline unions all of them and pivots to the same wide shape as
    Mode 1, then continues identically.

Each entry in MASTER_INPUT / CLIENT_INPUTS can be:
  - a Spark table name, e.g. "prod.client_a.rules"  (Databricks only --
    the script uses the notebook's existing `spark` session)
  - a file path ending in .xlsx / .xls / .csv        (works everywhere)

CLEANING RULES ALREADY HANDLED AUTOMATICALLY
----------------------------------------------
These are structural, not textual, comparisons (AST-based), so the
following are transparently ignored and need no manual cleanup:
  - trailing semicolon present on some queries, absent on others
  - extra / inconsistent whitespace and line breaks
  - SQL comments (-- line comments and /* block comments */)
  - predicate order (WHERE/ON/HAVING), column order in inner subqueries,
    GROUP BY column order, identifier case, and symmetric comparisons
    (a=b vs b=a)

REQUIRED PACKAGES
------------------
    pip install sqlglot pandas openpyxl
(pyspark is only needed if you point at Spark table names instead of
files; on Databricks it's already provided as `spark` / `pyspark`.)
The bootstrap block below will attempt to auto-install anything missing.
"""

# ======================================================================
# CONFIG -- edit this block, then run the whole script
# ======================================================================

# ---- INPUT MODE 1: single wide "master" table or file ----
# Leave as "" if you're using CLIENT_INPUTS (Mode 2) instead.
MASTER_INPUT = ""
# Examples:
# MASTER_INPUT = "prod.migration.rules_master"
# MASTER_INPUT = "/Volumes/main/migration/rules_master.xlsx"
# MASTER_INPUT = "/Volumes/main/migration/rules_master.csv"

# ---- INPUT MODE 2: one table/file per client ----
# Leave as [] if you're using MASTER_INPUT (Mode 1) instead.
CLIENT_INPUTS = []
# Example:
# CLIENT_INPUTS = [
#     "prod.client_a.rules",
#     "prod.client_b.rules",
#     "/Volumes/main/migration/client_c_rules.xlsx",
# ]

# ---- Column name conventions ----
# Case-insensitive, whitespace-tolerant matching is used, so these only
# need editing if your columns use genuinely different words.
RULE_NAME_COL = "rule_name"
CLIENT_NAME_COL = "client_name"                # used in CLIENT_INPUTS (Mode 2) tables
FIREBIRD_LOGIC_COL = "firebird_logic"          # used in CLIENT_INPUTS (Mode 2) tables
FIREBIRD_LOGIC_PREFIX = "firebird_logic_"      # used in MASTER_INPUT (Mode 1) wide columns
                                                # e.g. column "firebird_logic_clientA" -> client "clientA"

# ---- SQL parsing ----
# sqlglot has no dedicated Firebird dialect; its generic ANSI parser
# handles the great majority of Firebird SQL (SELECT/JOIN/WHERE/GROUP
# BY/HAVING/CAST/||/comments). Leave as "" unless you find a closer
# match (e.g. "postgres") for your specific queries.
SQL_DIALECT = ""

# ---- OUTPUT ----
OUTPUT_PATH = ""    # leave blank -> writes next to this script
OUTPUT_FILENAME = "migration_master_report.xlsx"

# ---- Tuning knobs (safe to leave as-is) ----
# When a rule has 2+ distinct logic variants across clients, this
# threshold (0-1, Jaccard similarity of tables used) decides whether
# they're close enough to be the "same rule, different filters"
# (-> VERSION) or unrelated logic that happens to share a rule name
# (-> NEEDS REVIEW).
FAMILY_SIMILARITY_THRESHOLD = 0.5

# Include the detailed predicate-level diff sheet for CROSSPOLLINATE
# rules too (they have no differences by definition, so this mostly
# just bulks up the file). Default: only Version + Needs Review rules
# get a detailed diff section.
INCLUDE_DIFF_FOR_CROSSPOLLINATED = False

# ======================================================================
# END CONFIG -- everything below this line just needs to run
# ======================================================================


# --------------------------------------------------------------------
# 0. Bootstrap: make sure required packages are available
# --------------------------------------------------------------------
import importlib
import subprocess
import sys


def _ensure(pkg_import_name: str, pip_name: str = None):
    try:
        return importlib.import_module(pkg_import_name)
    except ImportError:
        pip_name = pip_name or pkg_import_name
        print(f"[setup] Installing missing package: {pip_name} ...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", pip_name],
            check=True,
        )
        return importlib.import_module(pkg_import_name)


sqlglot = _ensure("sqlglot")
pd = _ensure("pandas")
_ensure("openpyxl")

from sqlglot import exp
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

import hashlib
import itertools
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# --------------------------------------------------------------------
# 1. Environment / input loading
# --------------------------------------------------------------------

def _get_spark():
    """Return the active Spark session if one exists (Databricks provides
    `spark` as a global automatically); otherwise return None."""
    try:
        g = globals()
        if "spark" in g and g["spark"] is not None:
            return g["spark"]
    except Exception:
        pass
    try:
        from pyspark.sql import SparkSession
        active = SparkSession.getActiveSession()
        return active
    except Exception:
        return None


def _looks_like_file(identifier: str) -> bool:
    return identifier.lower().endswith((".xlsx", ".xls", ".csv"))


def load_input(identifier: str) -> "pd.DataFrame":
    """Load one input (table name or file path) into a pandas DataFrame."""
    if not identifier:
        raise ValueError("Empty input identifier passed to load_input().")

    if _looks_like_file(identifier):
        if identifier.lower().endswith(".csv"):
            return pd.read_csv(identifier)
        return pd.read_excel(identifier)

    # Otherwise treat it as a table name (Spark).
    spark = _get_spark()
    if spark is None:
        raise RuntimeError(
            f"'{identifier}' doesn't look like a file (.xlsx/.xls/.csv) and "
            "no active Spark session was found, so it can't be read as a "
            "table. If you're not running this in Databricks, point "
            "MASTER_INPUT / CLIENT_INPUTS at file paths instead."
        )
    return spark.table(identifier).toPandas()


def _find_col(df: "pd.DataFrame", wanted: str) -> Optional[str]:
    """Case/whitespace-insensitive column lookup."""
    norm = lambda s: str(s).strip().lower().replace(" ", "_")
    target = norm(wanted)
    for col in df.columns:
        if norm(col) == target:
            return col
    return None


# --------------------------------------------------------------------
# 2. Build the wide "master" table (rule_name x client -> firebird_logic)
# --------------------------------------------------------------------

def build_master_from_wide(df: "pd.DataFrame") -> Tuple["pd.DataFrame", List[str]]:
    """MODE 1: df is already rule_name | firebird_logic_<client> | ...
    Returns (master_df indexed by rule_name with one column per client,
    list of client names in column order)."""
    rule_col = _find_col(df, RULE_NAME_COL)
    if rule_col is None:
        raise ValueError(
            f"Could not find a '{RULE_NAME_COL}' column in MASTER_INPUT. "
            f"Columns found: {list(df.columns)}"
        )
    client_name_col = _find_col(df, CLIENT_NAME_COL)  # may legitimately be None

    prefix_norm = FIREBIRD_LOGIC_PREFIX.strip().lower()
    client_cols = {}  # client_name -> source column
    for col in df.columns:
        col_norm = str(col).strip().lower()
        if col == rule_col or (client_name_col is not None and col == client_name_col):
            continue
        if col_norm.startswith(prefix_norm):
            client_name = str(col)[len(FIREBIRD_LOGIC_PREFIX):].strip()
            client_cols[client_name] = col

    if not client_cols:
        # Fallback: no column matched the expected prefix -- treat every
        # remaining column as its own client, named after the column itself.
        for col in df.columns:
            if col == rule_col or (client_name_col is not None and col == client_name_col):
                continue
            client_cols[str(col)] = col

    if not client_cols:
        raise ValueError(
            "Could not identify any per-client Firebird-logic columns in "
            f"MASTER_INPUT. Columns found: {list(df.columns)}"
        )

    client_names = list(client_cols.keys())
    out = pd.DataFrame({"rule_name": df[rule_col].astype(str).str.strip()})
    for client_name, src_col in client_cols.items():
        out[client_name] = df[src_col]

    out = out.groupby("rule_name", as_index=False).first()
    out = out.set_index("rule_name")
    return out, client_names


def build_master_from_long_tables(identifiers: List[str]) -> Tuple["pd.DataFrame", List[str]]:
    """MODE 2: each identifier is a per-client table/file in the long
    shape rule_name | client_name | firebird_logic. Unions them all and
    pivots to the same wide shape build_master_from_wide() produces."""
    frames = []
    for ident in identifiers:
        df = load_input(ident)
        rule_col = _find_col(df, RULE_NAME_COL)
        client_col = _find_col(df, CLIENT_NAME_COL)
        logic_col = _find_col(df, FIREBIRD_LOGIC_COL)
        missing = [n for n, c in
                   [(RULE_NAME_COL, rule_col), (CLIENT_NAME_COL, client_col),
                    (FIREBIRD_LOGIC_COL, logic_col)] if c is None]
        if missing:
            raise ValueError(
                f"Input '{ident}' is missing expected column(s) {missing}. "
                f"Columns found: {list(df.columns)}"
            )
        sub = df[[rule_col, client_col, logic_col]].copy()
        sub.columns = ["rule_name", "client_name", "firebird_logic"]
        frames.append(sub)

    long_df = pd.concat(frames, ignore_index=True)
    long_df["rule_name"] = long_df["rule_name"].astype(str).str.strip()
    long_df["client_name"] = long_df["client_name"].astype(str).str.strip()

    # union -> pivot to wide (rule_name rows, client_name columns)
    wide = long_df.pivot_table(
        index="rule_name", columns="client_name", values="firebird_logic",
        aggfunc="first",
    )
    client_names = list(wide.columns)
    return wide, client_names


# --------------------------------------------------------------------
# 3. SQL cleaning / formatting / normalization
#    (mostly ported from the earlier single-batch comparison tool)
# --------------------------------------------------------------------

# A handful of Firebird-only keywords sqlglot's generic parser doesn't
# know. Best-effort rewrite for PARSING/COMPARISON purposes only -- the
# original text is always preserved for display.
_FIREBIRD_SHIM_RE = re.compile(r"\bFIRST\s+(\d+)\b", re.IGNORECASE)


def _clean_text(s: Optional[str]) -> Optional[str]:
    """Strip characters openpyxl refuses to write to a cell (control
    characters that can show up in raw parser error messages, e.g. the
    caret/underline markers sqlglot uses to point at a bad token)."""
    if s is None:
        return s
    return ILLEGAL_CHARACTERS_RE.sub("", str(s))


def _shim_for_parsing(sql: str) -> str:
    # "SELECT FIRST 10 ..." -> "SELECT ... LIMIT 10" is not a pure regex
    # rewrite (LIMIT goes at the end), so we simply strip the FIRST n
    # clause before parsing when present -- row-limiting doesn't affect
    # the filtering LOGIC we're comparing anyway.
    return _FIREBIRD_SHIM_RE.sub("", sql)


def clean_and_parse(raw_sql: str) -> Tuple[Optional["exp.Expression"], Optional[str], str]:
    """Returns (parsed_ast_or_None, error_or_None, pretty_display_sql).
    pretty_display_sql preserves the query's original predicate order --
    it's for human eyeballing, not for logic comparison."""
    if raw_sql is None or (isinstance(raw_sql, float) and pd.isna(raw_sql)):
        return None, None, ""

    text = str(raw_sql).strip()
    if not text:
        return None, None, ""
    if text.endswith(";"):
        text = text[:-1].strip()

    dialect = SQL_DIALECT or None
    try:
        tree = sqlglot.parse_one(text, read=dialect)
    except Exception:
        try:
            tree = sqlglot.parse_one(_shim_for_parsing(text), read=dialect)
        except Exception as e:
            return None, _clean_text(str(e)), _clean_text(text)

    try:
        pretty = tree.sql(dialect=dialect, pretty=True)
    except Exception:
        pretty = text

    return tree, None, _clean_text(pretty)


def _is_named_subquery_select(select_node: "exp.Select") -> bool:
    parent = select_node.parent
    if isinstance(parent, exp.Subquery) and parent.alias:
        return True
    if isinstance(parent, exp.CTE):
        return True
    return False


def _sort_key(node: "exp.Expression") -> str:
    return node.sql(normalize=True).lower()


def _flatten_and_sort_connector(node: "exp.Connector") -> "exp.Expression":
    cls = type(node)
    parts = list(node.flatten())
    parts_sorted = sorted(parts, key=_sort_key)
    result = parts_sorted[0]
    for p in parts_sorted[1:]:
        result = cls(this=result, expression=p)
    return result


def _canonicalize_node(node: "exp.Expression") -> "exp.Expression":
    if isinstance(node, exp.Connector):
        return _flatten_and_sort_connector(node)
    if isinstance(node, (exp.EQ, exp.NEQ)):
        left, right = node.this, node.expression
        if _sort_key(left) > _sort_key(right):
            node.set("this", right)
            node.set("expression", left)
        return node
    return node


def _normalize_recursive(node: "exp.Expression") -> "exp.Expression":
    """Explicit post-order recursion. Do NOT use Expression.transform():
    it prunes descent into a subtree once a node is replaced, which would
    silently skip normalizing anything nested under a rebuilt AND/OR
    chain (e.g. inside an EXISTS(...) subquery one level below a
    top-level AND)."""
    for key, value in list(node.args.items()):
        if isinstance(value, exp.Expression):
            new_child = _normalize_recursive(value)
            if new_child is not value:
                node.set(key, new_child)
        elif isinstance(value, list):
            new_list = []
            changed = False
            for item in value:
                if isinstance(item, exp.Expression):
                    new_item = _normalize_recursive(item)
                    if new_item is not item:
                        changed = True
                    new_list.append(new_item)
                else:
                    new_list.append(item)
            if changed:
                node.set(key, new_list)
    return _canonicalize_node(node)


def normalize(expression: "exp.Expression") -> "exp.Expression":
    tree = expression.copy()

    for node in tree.walk():
        if node.comments:
            node.comments = None

    for node in tree.walk():
        if isinstance(node, exp.Identifier) and not node.args.get("quoted"):
            node.set("this", node.this.lower())

    tree = _normalize_recursive(tree)

    for select_node in list(tree.find_all(exp.Select)):
        if _is_named_subquery_select(select_node):
            exprs = select_node.expressions
            if exprs:
                select_node.set("expressions", sorted(exprs, key=_sort_key))

    for group_node in tree.find_all(exp.Group):
        exprs = group_node.expressions
        if exprs:
            group_node.set("expressions", sorted(exprs, key=_sort_key))

    return tree


def canonical_sql(tree: "exp.Expression") -> str:
    return tree.sql(dialect=(SQL_DIALECT or None), normalize=True).strip()


def logic_hash(tree: "exp.Expression") -> str:
    return hashlib.sha256(canonical_sql(tree).encode("utf-8")).hexdigest()[:16]


def summarize_diff(tree_a: "exp.Expression", tree_b: "exp.Expression") -> List[str]:
    edits = sqlglot.diff(tree_a, tree_b, delta_only=True)
    findings = []
    for edit in edits:
        kind = type(edit).__name__
        if kind == "Keep":
            continue
        if kind == "Update":
            findings.append(f"CHANGED: `{edit.source.sql()}` --> `{edit.target.sql()}`")
        elif kind == "Insert":
            findings.append(f"ADDED: `{edit.expression.sql()}`")
        elif kind == "Remove":
            findings.append(f"REMOVED: `{edit.expression.sql()}`")
        elif kind == "Move":
            src_sql, tgt_sql = edit.source.sql(), edit.target.sql()
            if src_sql != tgt_sql:
                findings.append(f"MOVED/CHANGED: `{src_sql}` --> `{tgt_sql}`")
    seen, out = set(), []
    for f_ in findings:
        if f_ not in seen:
            seen.add(f_)
            out.append(f_)
    return out


# --------------------------------------------------------------------
# 4. Logic-component extraction (for the detailed diff sheet)
# --------------------------------------------------------------------

_COMPARISON_PREDICATE_KINDS = (
    exp.EQ, exp.NEQ, exp.GT, exp.GTE, exp.LT, exp.LTE,
    exp.Like, exp.ILike, exp.In, exp.Is, exp.Between,
)


def _outer_select(tree: "exp.Expression") -> Optional["exp.Select"]:
    if isinstance(tree, exp.Select):
        return tree
    if isinstance(tree, exp.With):
        inner = tree.this
        return inner if isinstance(inner, exp.Select) else None
    return tree.find(exp.Select)


def extract_logic_profile(tree: "exp.Expression") -> Dict[str, object]:
    profile: Dict[str, object] = {}

    tables = sorted({t.name.lower() for t in tree.find_all(exp.Table)})
    profile["tables"] = tables
    profile["tables_display"] = ", ".join(tables) if tables else "(none)"

    joins = list(tree.find_all(exp.Join))
    join_types, join_conditions = [], []
    for j in joins:
        kind = (j.args.get("kind") or "").upper()
        side = (j.args.get("side") or "").upper()
        label = " ".join(p for p in (side, kind, "JOIN") if p).strip()
        join_types.append(label if label else "JOIN")
        on = j.args.get("on")
        if on is not None:
            join_conditions.append(on.sql())
    profile["join_types"] = ", ".join(sorted(join_types)) if join_types else "(none)"
    profile["join_conditions"] = "; ".join(sorted(join_conditions)) if join_conditions else "(none)"

    outer = _outer_select(tree)
    group_node = outer.args.get("group") if outer else None
    if group_node and group_node.expressions:
        profile["group_by"] = ", ".join(sorted(e.sql() for e in group_node.expressions))
    else:
        profile["group_by"] = "(none)"

    having_node = outer.args.get("having") if outer else None
    profile["having"] = having_node.this.sql() if having_node else "(none)"

    agg_names = sorted({type(n).__name__.upper() for n in tree.find_all(exp.AggFunc)})
    profile["aggregates"] = ", ".join(agg_names) if agg_names else "(none)"

    if outer is not None and outer.expressions:
        profile["output_columns"] = ", ".join(e.sql() for e in outer.expressions)
    else:
        profile["output_columns"] = "(none)"

    predicate_strs = [n.sql() for n in tree.find_all(*_COMPARISON_PREDICATE_KINDS)]
    seen, preds = set(), []
    for p in predicate_strs:
        if p not in seen:
            seen.add(p)
            preds.append(p)
    profile["predicates"] = preds

    return profile


def table_similarity(profile_a: Dict, profile_b: Dict) -> float:
    """Jaccard similarity of the table sets used by two query profiles.
    Used to tell 'same rule, different filters' (VERSION) apart from
    'unrelated logic sharing a rule name' (NEEDS REVIEW)."""
    a, b = set(profile_a["tables"]), set(profile_b["tables"])
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# --------------------------------------------------------------------
# 5. Per-rule classification
# --------------------------------------------------------------------

@dataclass
class ClientQuery:
    client: str
    raw_sql: str
    tree: Optional["exp.Expression"] = None
    norm_tree: Optional["exp.Expression"] = None
    hash_: Optional[str] = None
    pretty_sql: str = ""
    error: Optional[str] = None
    profile: Optional[Dict] = None


@dataclass
class RuleResult:
    rule_name: str
    clients: List[ClientQuery] = field(default_factory=list)
    classification: str = ""     # CROSSPOLLINATE / VERSION / STANDALONE / NEEDS REVIEW / PARSE ERROR
    hash_groups: Dict[str, List[str]] = field(default_factory=dict)   # hash -> [client names]
    rule_id: str = ""
    version_map: Dict[str, str] = field(default_factory=dict)         # client -> version label
    notes: str = ""


def parse_client_cell(client: str, raw_sql) -> ClientQuery:
    cq = ClientQuery(client=client, raw_sql="" if raw_sql is None else str(raw_sql))
    tree, error, pretty = clean_and_parse(raw_sql)
    cq.pretty_sql = pretty
    if error:
        cq.error = error
        return cq
    if tree is None:
        # blank/NULL cell -- rule not present for this client
        return cq
    cq.tree = tree
    cq.norm_tree = normalize(tree)
    cq.hash_ = logic_hash(cq.norm_tree)
    cq.profile = extract_logic_profile(cq.norm_tree)
    return cq


def classify_rule(rule_name: str, row: "pd.Series", client_names: List[str]) -> RuleResult:
    result = RuleResult(rule_name=rule_name)
    present = []
    for client in client_names:
        raw = row.get(client)
        if raw is None or (isinstance(raw, float) and pd.isna(raw)) or str(raw).strip() == "":
            continue
        cq = parse_client_cell(client, raw)
        result.clients.append(cq)
        present.append(cq)

    parse_errors = [cq for cq in present if cq.error]
    usable = [cq for cq in present if cq.tree is not None]

    if not present:
        result.classification = "EMPTY"
        return result

    if parse_errors:
        result.notes = "Parse error(s), excluded from comparison: " + \
                        "; ".join(f"{cq.client}: {cq.error}" for cq in parse_errors)

    if not usable:
        result.classification = "PARSE ERROR"
        return result

    # group usable clients by hash
    groups: Dict[str, List[str]] = {}
    for cq in usable:
        groups.setdefault(cq.hash_, []).append(cq.client)
    result.hash_groups = groups

    if len(usable) == 1:
        # Only one client's logic could actually be compared -- whether
        # or not OTHER clients had a parse error, there's nothing to
        # crosspollinate against, so this is Standalone (with the parse
        # error noted separately for follow-up).
        result.classification = "STANDALONE"
        result.rule_id = f"{rule_name}"
        return result

    if len(groups) == 1:
        result.classification = "CROSSPOLLINATE"
        return result

    # 2+ distinct logic variants -- decide VERSION vs NEEDS REVIEW using
    # table-overlap similarity between every pair of distinct variants.
    reps = {h: next(cq for cq in usable if cq.hash_ == h).profile for h in groups}
    hashes = list(groups.keys())
    all_similar = True
    for h1, h2 in itertools.combinations(hashes, 2):
        if table_similarity(reps[h1], reps[h2]) < FAMILY_SIMILARITY_THRESHOLD:
            all_similar = False
            break

    result.classification = "VERSION" if all_similar else "NEEDS REVIEW"

    # assign version labels in order of how many clients use each variant
    # (most common variant = Version 1)
    ordered = sorted(groups.items(), key=lambda kv: -len(kv[1]))
    for i, (h, clients) in enumerate(ordered, start=1):
        label = f"V{i}"
        for c in clients:
            result.version_map[c] = label

    return result


# --------------------------------------------------------------------
# 6. Migration sequencing analysis
# --------------------------------------------------------------------

def build_wave_plan(results: List[RuleResult]) -> "pd.DataFrame":
    rows = []
    for r in results:
        n_clients = len({cq.client for cq in r.clients if cq.tree is not None})
        if r.classification == "CROSSPOLLINATE":
            wave, effort = 1, 1
        elif r.classification == "STANDALONE":
            wave, effort = 3, 1
        elif r.classification == "VERSION":
            n_versions = len(r.hash_groups)
            wave, effort = 2, n_versions
        else:  # NEEDS REVIEW / PARSE ERROR / EMPTY
            wave, effort = 4, None
        rows.append({
            "rule_name": r.rule_name,
            "classification": r.classification,
            "clients_covered": n_clients,
            "effort_units": effort,
            "migration_wave": wave,
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values(
        by=["migration_wave", "clients_covered", "effort_units"],
        ascending=[True, False, True],
        na_position="last",
    ).reset_index(drop=True)
    df.insert(0, "priority_order", range(1, len(df) + 1))
    return df


def build_client_readiness(results: List[RuleResult], client_names: List[str]) -> "pd.DataFrame":
    rows = []
    for client in client_names:
        counts = {"CROSSPOLLINATE": 0, "VERSION": 0, "STANDALONE": 0,
                  "NEEDS REVIEW": 0, "PARSE ERROR": 0}
        total = 0
        for r in results:
            client_present = any(
                cq.client == client and (cq.tree is not None or cq.error)
                for cq in r.clients
            )
            if not client_present:
                continue
            total += 1
            if r.classification in counts:
                counts[r.classification] += 1
        shared_ready = counts["CROSSPOLLINATE"] + counts["VERSION"]
        readiness_pct = round(100 * shared_ready / total, 1) if total else 0.0
        rows.append({
            "client_name": client,
            "total_rules": total,
            "crosspollinate_rules": counts["CROSSPOLLINATE"],
            "version_rules": counts["VERSION"],
            "standalone_rules": counts["STANDALONE"],
            "needs_review_rules": counts["NEEDS REVIEW"],
            "readiness_pct_shared_logic": readiness_pct,
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values(by="readiness_pct_shared_logic", ascending=False).reset_index(drop=True)
    df.insert(0, "recommended_onboarding_order",
              ["Pilot / start here" if i == 0 else str(i + 1) for i in range(len(df))])
    return df


# --------------------------------------------------------------------
# 7. Excel report generation
# --------------------------------------------------------------------

BLUE_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
RED_FILL = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
GREY_FILL = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
GREEN_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
YELLOW_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
ORANGE_FILL = PatternFill(start_color="FCD5B4", end_color="FCD5B4", fill_type="solid")
HEADER_FILL = PatternFill(start_color="404040", end_color="404040", fill_type="solid")

WHITE_BOLD = Font(name="Arial", color="FFFFFF", bold=True)
NORMAL_FONT = Font(name="Arial")
RED_ROW_FONT = Font(name="Arial", color="FFFFFF")
BOLD_FONT = Font(name="Arial", bold=True)

CLASS_FILL = {
    "CROSSPOLLINATE": GREEN_FILL,
    "VERSION": YELLOW_FILL,
    "STANDALONE": BLUE_FILL,
    "NEEDS REVIEW": RED_FILL,
    "PARSE ERROR": ORANGE_FILL,
    "EMPTY": GREY_FILL,
}


def _autosize(ws, widths: Dict[int, int]):
    for col_idx, width in widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width


def _write_header(ws, headers: List[str], row: int = 1):
    for col_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=col_idx, value=h)
        c.font = WHITE_BOLD
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", wrap_text=True)


def _classification_row_style(ws, row_idx: int, n_cols: int, classification: str):
    fill = CLASS_FILL.get(classification, GREY_FILL)
    font = RED_ROW_FONT if classification == "NEEDS REVIEW" else NORMAL_FONT
    for col_idx in range(1, n_cols + 1):
        c = ws.cell(row=row_idx, column=col_idx)
        c.fill = fill
        if col_idx == 1:
            c.font = Font(name="Arial", bold=True, color=font.color)
        else:
            c.font = font


def sheet_legend_summary(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.active
    ws.title = "Legend & Summary"
    ws.cell(row=1, column=1, value="FastTrack -> Firebird Migration: Crosspollination Report").font = \
        Font(name="Arial", bold=True, size=14)

    ws.cell(row=3, column=1, value="Run parameters").font = BOLD_FONT
    params = [
        ("Total clients", len(client_names)),
        ("Client names", ", ".join(client_names)),
        ("Total rules analyzed", len(results)),
        ("Family similarity threshold", FAMILY_SIMILARITY_THRESHOLD),
        ("SQL parse dialect", SQL_DIALECT or "(generic ANSI)"),
    ]
    r = 4
    for label, val in params:
        ws.cell(row=r, column=1, value=label).font = NORMAL_FONT
        ws.cell(row=r, column=2, value=val).font = NORMAL_FONT
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="Classification counts").font = BOLD_FONT
    r += 1
    from collections import Counter
    counts = Counter(res.classification for res in results)
    for label in ["CROSSPOLLINATE", "VERSION", "STANDALONE", "NEEDS REVIEW", "PARSE ERROR", "EMPTY"]:
        ws.cell(row=r, column=1, value=label).font = NORMAL_FONT
        ws.cell(row=r, column=1).fill = CLASS_FILL.get(label, GREY_FILL)
        ws.cell(row=r, column=2, value=counts.get(label, 0)).font = NORMAL_FONT
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="Color legend").font = BOLD_FONT
    r += 1
    legend = [
        ("CROSSPOLLINATE", "Identical logic across every client that has this rule -- migrate once."),
        ("VERSION", "Same rule family, filtering logic differs by client -- one base rule, multiple versions."),
        ("STANDALONE", "Only exists in one client -- migrate directly, no crosspollination possible."),
        ("NEEDS REVIEW", "Same rule name, unrelated logic -- likely a naming collision. Resolve manually."),
        ("PARSE ERROR", "Could not parse this SQL text -- excluded from comparison, fix and re-run."),
    ]
    for label, desc in legend:
        ws.cell(row=r, column=1, value=label).fill = CLASS_FILL.get(label, GREY_FILL)
        ws.cell(row=r, column=1).font = NORMAL_FONT
        ws.cell(row=r, column=2, value=desc).font = NORMAL_FONT
        r += 1

    r += 1
    ws.cell(row=r, column=1, value="Already handled automatically (no manual cleanup needed):").font = BOLD_FONT
    r += 1
    for note in [
        "- Trailing semicolon present on some queries, absent on others",
        "- Extra/inconsistent whitespace and line breaks",
        "- SQL comments (-- line and /* block */)",
        "- Predicate order (WHERE/ON/HAVING), GROUP BY column order, identifier case, a=b vs b=a",
    ]:
        ws.cell(row=r, column=1, value=note).font = NORMAL_FONT
        r += 1

    ws.column_dimensions["A"].width = 45
    ws.column_dimensions["B"].width = 70


def sheet_master_classification(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Master Classification")
    headers = ["rule_name", "classification", "clients_present", "clients_covered",
               "num_logic_variants", "rule_id_suggestion", "notes"]
    _write_header(ws, headers)

    row_idx = 2
    for r in results:
        present_clients = sorted({cq.client for cq in r.clients if cq.tree is not None})
        n_variants = len(r.hash_groups) if r.hash_groups else (1 if present_clients else 0)
        rule_id = f"RULE_{row_idx-1:04d}"
        r.rule_id = rule_id

        values = [r.rule_name, r.classification, ", ".join(present_clients),
                  len(present_clients), n_variants, rule_id, r.notes]
        for col_idx, v in enumerate(values, start=1):
            ws.cell(row=row_idx, column=col_idx, value=v)
        _classification_row_style(ws, row_idx, len(headers), r.classification)
        row_idx += 1

    _autosize(ws, {1: 22, 2: 18, 3: 45, 4: 14, 5: 16, 6: 18, 7: 55})
    ws.freeze_panes = "A2"


def _filtered_sheet(wb, title: str, results: List[RuleResult], classification: str, client_names: List[str]):
    ws = wb.create_sheet(title)
    subset = [r for r in results if r.classification == classification]

    if classification == "VERSION":
        headers = ["rule_name", "rule_id", "version", "clients_using_this_version",
                   "num_versions_total", "notes"]
        _write_header(ws, headers)
        row_idx = 2
        for r in subset:
            ordered = sorted(r.hash_groups.items(), key=lambda kv: -len(kv[1]))
            for i, (h, clients) in enumerate(ordered, start=1):
                ws.cell(row=row_idx, column=1, value=r.rule_name)
                ws.cell(row=row_idx, column=2, value=f"{r.rule_id}_V{i}")
                ws.cell(row=row_idx, column=3, value=f"V{i}")
                ws.cell(row=row_idx, column=4, value=", ".join(sorted(clients)))
                ws.cell(row=row_idx, column=5, value=len(ordered))
                ws.cell(row=row_idx, column=6, value=r.notes)
                _classification_row_style(ws, row_idx, len(headers), classification)
                row_idx += 1
        _autosize(ws, {1: 22, 2: 18, 3: 10, 4: 40, 5: 16, 6: 45})
    else:
        headers = ["rule_name", "rule_id", "clients_present", "notes"]
        _write_header(ws, headers)
        row_idx = 2
        for r in subset:
            present_clients = sorted({cq.client for cq in r.clients if cq.tree is not None})
            ws.cell(row=row_idx, column=1, value=r.rule_name)
            ws.cell(row=row_idx, column=2, value=r.rule_id)
            ws.cell(row=row_idx, column=3, value=", ".join(present_clients))
            ws.cell(row=row_idx, column=4, value=r.notes)
            _classification_row_style(ws, row_idx, len(headers), classification)
            row_idx += 1
        _autosize(ws, {1: 22, 2: 18, 3: 45, 4: 55})

    ws.freeze_panes = "A2"


def sheet_detailed_diff(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Detailed Logic Diff")
    headers = ["Rule / Logic Component"] + client_names
    _write_header(ws, headers)
    row_idx = 2

    targets = [r for r in results if r.classification in ("VERSION", "NEEDS REVIEW")
               or (INCLUDE_DIFF_FOR_CROSSPOLLINATED and r.classification == "CROSSPOLLINATE")]

    fixed_rows = [
        ("Tables Used", "tables_display"),
        ("Join Type(s)", "join_types"),
        ("Join Condition(s)", "join_conditions"),
        ("GROUP BY Columns", "group_by"),
        ("HAVING Clause", "having"),
        ("Aggregate Functions", "aggregates"),
        ("Output Columns", "output_columns"),
    ]

    by_client = {cq.client: cq for r in results for cq in r.clients}

    for r in targets:
        # section header row
        header_cell = ws.cell(row=row_idx, column=1,
                               value=f"=== {r.rule_name}  ({r.classification}) ===")
        header_cell.font = Font(name="Arial", bold=True)
        header_cell.fill = CLASS_FILL.get(r.classification, GREY_FILL)
        for col_idx in range(2, len(client_names) + 2):
            ws.cell(row=row_idx, column=col_idx).fill = CLASS_FILL.get(r.classification, GREY_FILL)
        row_idx += 1

        client_map = {cq.client: cq for cq in r.clients}

        for label, key in fixed_rows:
            values, presence = [], []
            for c in client_names:
                cq = client_map.get(c)
                if cq is None or cq.tree is None:
                    values.append(None)
                    presence.append(False)
                else:
                    values.append(cq.profile.get(key, ""))
                    presence.append(True)

            present_vals = {str(v).strip().lower() for v, p in zip(values, presence) if p}
            all_match = len(present_vals) <= 1

            ws.cell(row=row_idx, column=1, value=label).font = BOLD_FONT
            for col_idx, (v, p) in enumerate(zip(values, presence), start=2):
                c = ws.cell(row=row_idx, column=col_idx, value=(v if p else "(n/a)"))
                if not p:
                    c.fill = GREY_FILL
                    c.font = NORMAL_FONT
                else:
                    c.fill = BLUE_FILL if all_match else RED_FILL
                    c.font = RED_ROW_FONT if not all_match else NORMAL_FONT
                c.alignment = Alignment(wrap_text=True, vertical="top")
            label_cell = ws.cell(row=row_idx, column=1)
            label_cell.fill = BLUE_FILL if all_match else RED_FILL
            label_cell.font = Font(name="Arial", bold=True,
                                    color=("FFFFFF" if not all_match else "000000"))
            row_idx += 1

        # predicate presence rows
        all_predicates = sorted({p for cq in client_map.values() if cq.tree is not None
                                  for p in cq.profile["predicates"]})
        for pred in all_predicates:
            presence_map = {c: (client_map.get(c) is not None and client_map[c].tree is not None
                                 and pred in client_map[c].profile["predicates"])
                             for c in client_names}
            participating = [c for c in client_names if client_map.get(c) is not None
                              and client_map[c].tree is not None]
            all_present = all(presence_map[c] for c in participating) if participating else False

            label_cell = ws.cell(row=row_idx, column=1, value=pred)
            fill = BLUE_FILL if all_present else RED_FILL
            font = RED_ROW_FONT if not all_present else NORMAL_FONT
            label_cell.fill = fill
            label_cell.font = font
            label_cell.alignment = Alignment(wrap_text=True, vertical="top")
            for col_idx, c in enumerate(client_names, start=2):
                if client_map.get(c) is None or client_map[c].tree is None:
                    cell = ws.cell(row=row_idx, column=col_idx, value="(n/a)")
                    cell.fill = GREY_FILL
                    cell.font = NORMAL_FONT
                else:
                    cell = ws.cell(row=row_idx, column=col_idx,
                                    value="\u2713" if presence_map[c] else "")
                    cell.fill = fill
                    cell.font = font
                cell.alignment = Alignment(horizontal="center")
            row_idx += 1

        row_idx += 1  # blank separator row between rules

    ws.column_dimensions["A"].width = 50
    for i in range(2, len(client_names) + 2):
        ws.column_dimensions[get_column_letter(i)].width = 28
    ws.freeze_panes = "B2"


def sheet_presence_matrix(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Presence Matrix")
    headers = ["rule_name"] + client_names + ["TOTAL"]
    _write_header(ws, headers)
    row_idx = 2
    for r in results:
        present = {cq.client for cq in r.clients if cq.tree is not None or cq.error}
        ws.cell(row=row_idx, column=1, value=r.rule_name)
        total = 0
        for col_idx, c in enumerate(client_names, start=2):
            if c in present:
                ws.cell(row=row_idx, column=col_idx, value=1)
                total += 1
        ws.cell(row=row_idx, column=len(client_names) + 2, value=total)
        row_idx += 1
    _autosize(ws, {1: 22, **{i: 12 for i in range(2, len(client_names) + 3)}})
    ws.freeze_panes = "B2"


def sheet_wave_plan(wb, wave_df: "pd.DataFrame"):
    ws = wb.create_sheet("Migration Wave Plan")
    if wave_df.empty:
        ws.cell(row=1, column=1, value="No data.")
        return
    headers = list(wave_df.columns)
    _write_header(ws, headers)
    wave_fill = {1: GREEN_FILL, 2: YELLOW_FILL, 3: BLUE_FILL, 4: RED_FILL}
    for row_idx, (_, row) in enumerate(wave_df.iterrows(), start=2):
        for col_idx, col in enumerate(headers, start=1):
            val = row[col]
            c = ws.cell(row=row_idx, column=col_idx,
                        value=(None if pd.isna(val) else val))
            c.fill = wave_fill.get(row.get("migration_wave"), GREY_FILL)
            c.font = NORMAL_FONT
    _autosize(ws, {i: 20 for i in range(1, len(headers) + 1)})
    ws.freeze_panes = "A2"

    ws2 = ws
    note_row = len(wave_df) + 3
    ws2.cell(row=note_row, column=1,
             value="Wave 1 = Crosspollinate (highest coverage first) -> Wave 2 = Version "
                   "(fewest versions first) -> Wave 3 = Standalone -> Wave 4 = Needs Review "
                   "(resolve before migrating).").font = Font(name="Arial", italic=True)


def sheet_client_readiness(wb, readiness_df: "pd.DataFrame"):
    ws = wb.create_sheet("Client Readiness Score")
    if readiness_df.empty:
        ws.cell(row=1, column=1, value="No data.")
        return
    headers = list(readiness_df.columns)
    _write_header(ws, headers)
    for row_idx, (_, row) in enumerate(readiness_df.iterrows(), start=2):
        for col_idx, col in enumerate(headers, start=1):
            ws.cell(row=row_idx, column=col_idx, value=row[col])
        pct = row["readiness_pct_shared_logic"]
        fill = GREEN_FILL if pct >= 66 else (YELLOW_FILL if pct >= 33 else RED_FILL)
        for col_idx in range(1, len(headers) + 1):
            ws.cell(row=row_idx, column=col_idx).fill = fill
            ws.cell(row=row_idx, column=col_idx).font = NORMAL_FONT
    _autosize(ws, {i: 22 for i in range(1, len(headers) + 1)})
    ws.freeze_panes = "A2"

    note_row = len(readiness_df) + 3
    ws.cell(row=note_row, column=1,
            value="Higher readiness % = more of this client's rules are already shared/"
                  "common logic -- cheaper to onboard. Recommended pilot client is the "
                  "top row.").font = Font(name="Arial", italic=True)


def sheet_formatted_queries(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Formatted Queries (Reference)")
    headers = ["rule_name"] + client_names
    _write_header(ws, headers)
    row_idx = 2
    for r in results:
        client_map = {cq.client: cq for cq in r.clients}
        ws.cell(row=row_idx, column=1, value=r.rule_name).font = BOLD_FONT
        for col_idx, c in enumerate(client_names, start=2):
            cq = client_map.get(c)
            text = ""
            if cq is not None:
                text = cq.pretty_sql if cq.pretty_sql else (cq.error or "")
            cell = ws.cell(row=row_idx, column=col_idx, value=text)
            cell.font = NORMAL_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        row_idx += 1
    ws.column_dimensions["A"].width = 22
    for i in range(2, len(client_names) + 2):
        ws.column_dimensions[get_column_letter(i)].width = 55
    ws.freeze_panes = "B2"


def build_workbook(results: List[RuleResult], client_names: List[str],
                    wave_df: "pd.DataFrame", readiness_df: "pd.DataFrame") -> "Workbook":
    wb = Workbook()
    sheet_legend_summary(wb, results, client_names)
    sheet_master_classification(wb, results, client_names)
    _filtered_sheet(wb, "Crosspollination Candidates", results, "CROSSPOLLINATE", client_names)
    _filtered_sheet(wb, "Versioned Rules", results, "VERSION", client_names)
    _filtered_sheet(wb, "Standalone Rules", results, "STANDALONE", client_names)
    _filtered_sheet(wb, "Needs Review", results, "NEEDS REVIEW", client_names)
    sheet_detailed_diff(wb, results, client_names)
    sheet_wave_plan(wb, wave_df)
    sheet_client_readiness(wb, readiness_df)
    sheet_presence_matrix(wb, results, client_names)
    sheet_formatted_queries(wb, results, client_names)
    return wb


# --------------------------------------------------------------------
# 8. RUN PIPELINE
# --------------------------------------------------------------------

def run():
    if bool(MASTER_INPUT) == bool(CLIENT_INPUTS):
        raise ValueError(
            "Fill in exactly one of MASTER_INPUT or CLIENT_INPUTS, and "
            "leave the other blank/empty. "
            f"Got MASTER_INPUT={MASTER_INPUT!r}, CLIENT_INPUTS={CLIENT_INPUTS!r}"
        )

    print("[1/5] Loading input...")
    if MASTER_INPUT:
        raw_df = load_input(MASTER_INPUT)
        master_df, client_names = build_master_from_wide(raw_df)
    else:
        master_df, client_names = build_master_from_long_tables(CLIENT_INPUTS)

    print(f"      Loaded {len(master_df)} rules across {len(client_names)} "
          f"client(s): {', '.join(client_names)}")

    print("[2/5] Parsing, formatting, and normalizing SQL for every rule x client cell...")
    results: List[RuleResult] = []
    for rule_name, row in master_df.iterrows():
        results.append(classify_rule(rule_name, row, client_names))

    print("[3/5] Classifying rules (crosspollinate / version / standalone / needs review)...")
    from collections import Counter
    counts = Counter(r.classification for r in results)
    for label in ["CROSSPOLLINATE", "VERSION", "STANDALONE", "NEEDS REVIEW", "PARSE ERROR"]:
        print(f"      {label}: {counts.get(label, 0)}")

    print("[4/5] Building migration wave plan and client readiness scores...")
    wave_df = build_wave_plan(results)
    readiness_df = build_client_readiness(results, client_names)

    print("[5/5] Writing Excel report...")
    wb = build_workbook(results, client_names, wave_df, readiness_df)

    out_dir = OUTPUT_PATH.strip() if OUTPUT_PATH and OUTPUT_PATH.strip() else os.path.dirname(
        os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_FILENAME)
    wb.save(out_path)

    print(f"\nDone. Report written to: {out_path}")
    return out_path, results, wave_df, readiness_df


if __name__ == "__main__":
    run()
else:
    # Also runs automatically when pasted into a Databricks / Jupyter cell
    # and executed, since __name__ won't be "__main__" there.
    run()