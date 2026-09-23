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
onboard first (highest overlap with already-common logic).

INPUT MODES (fill in exactly ONE, leave the other blank/empty)
----------------------------------------------------------------
MODE 1 - MASTER_INPUT: one wide table/file, already in the shape
    rule_name | firebird_logic_<client1> | firebird_logic_<client2> | ...
    (one row per rule, one column per client holding that client's
    Firebird SQL text, blank/NULL where the rule doesn't exist for that
    client).

MODE 2 - CLIENT_INPUTS: a list of one table/file PER CLIENT, each in the
    long shape:  rule_name | client_name | firebird_logic
    (client_name is constant within each client's own table/file). The
    pipeline unions all of them and pivots to the same wide shape as
    Mode 1, then continues identically.

Each entry in MASTER_INPUT / CLIENT_INPUTS can be:
  - a Spark table name, e.g. "prod.client_a.rules"  (Databricks only --
    the script uses the notebook's existing `spark` session)
  - a file path ending in .xlsx / .xls / .csv        (works everywhere)

CLEANING / NORMALIZATION ALREADY HANDLED AUTOMATICALLY
--------------------------------------------------------
Every firebird_logic cell is parsed into a SQL syntax tree (not compared
as text), so all of the following are ignored automatically -- no manual
cleanup needed, and none of it requires the two queries to be
byte-identical:
  - trailing semicolon present on some queries, absent on others
  - extra / inconsistent whitespace and line breaks
  - SQL comments (-- line comments and /* block comments */)
  - CASE differences in identifiers: table names, column names, and
    aliases are compared case-insensitively, e.g.
    "FROM table1 C1 LEFT JOIN table2 C2" and
    "from table1 c1 left join table2 c2" are treated as identical.
    (String literal VALUES such as 'PAID' vs 'Paid' are deliberately
    left case-sensitive, since that can be a real data-filtering
    difference, not cosmetic noise.)
  - predicate order (WHERE/ON/HAVING), column order in inner subqueries,
    GROUP BY column order, and symmetric comparisons (a=b vs b=a)
Every query is also pretty-printed (reformatted) before any comparison
happens, purely for human readability in the report.

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
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

import hashlib
import itertools
import os
import re
from collections import Counter
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
        return SparkSession.getActiveSession()
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
    rule_col = _find_col(df, RULE_NAME_COL)
    if rule_col is None:
        raise ValueError(
            f"Could not find a '{RULE_NAME_COL}' column in MASTER_INPUT. "
            f"Columns found: {list(df.columns)}"
        )
    client_name_col = _find_col(df, CLIENT_NAME_COL)  # may legitimately be None

    prefix_norm = FIREBIRD_LOGIC_PREFIX.strip().lower()
    client_cols = {}
    for col in df.columns:
        col_norm = str(col).strip().lower()
        if col == rule_col or (client_name_col is not None and col == client_name_col):
            continue
        if col_norm.startswith(prefix_norm):
            client_name = str(col)[len(FIREBIRD_LOGIC_PREFIX):].strip()
            client_cols[client_name] = col

    if not client_cols:
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

    wide = long_df.pivot_table(
        index="rule_name", columns="client_name", values="firebird_logic",
        aggfunc="first",
    )
    client_names = list(wide.columns)
    return wide, client_names


# --------------------------------------------------------------------
# 3. SQL cleaning / formatting / normalization
# --------------------------------------------------------------------

_FIREBIRD_SHIM_RE = re.compile(r"\bFIRST\s+(\d+)\b", re.IGNORECASE)


def _clean_text(s: Optional[str]) -> Optional[str]:
    """Strip characters openpyxl refuses to write to a cell (control
    characters that can show up in raw parser error messages)."""
    if s is None:
        return s
    return ILLEGAL_CHARACTERS_RE.sub("", str(s))


def _shim_for_parsing(sql: str) -> str:
    # Firebird's "FIRST n" row-limit clause isn't understood by sqlglot's
    # generic parser and doesn't affect filtering LOGIC, so it's safe to
    # drop purely for parsing/comparison purposes.
    return _FIREBIRD_SHIM_RE.sub("", sql)


def clean_and_parse(raw_sql) -> Tuple[Optional["exp.Expression"], Optional[str], str]:
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
            new_list, changed = [], False
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
    """Produce a canonical AST for comparison: strips comments, lower-
    cases every unquoted identifier (table/column/alias names -- this is
    what makes 'C1' and 'c1' compare equal, while leaving string literal
    VALUES like 'PAID' case-sensitive since that can be real filtering
    logic), sorts AND/OR chains, canonicalizes symmetric comparisons
    (a=b <=> b=a), and sorts GROUP BY / named-subquery column order."""
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
    """Extracted from the NORMALIZED (already lower-cased, order-sorted)
    tree, so everything here is directly comparable/displayable
    case-insensitively without any extra work at display time."""
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
    profile["predicates_display"] = ", ".join(preds) if preds else "(none)"

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
    present: bool = True          # False = cell was blank/NULL in the input
    tree: Optional["exp.Expression"] = None
    norm_tree: Optional["exp.Expression"] = None
    hash_: Optional[str] = None
    pretty_sql: str = ""
    error: Optional[str] = None
    profile: Optional[Dict] = None


@dataclass
class RuleResult:
    rule_name: str
    clients: Dict[str, ClientQuery] = field(default_factory=dict)   # client -> ClientQuery (ALL clients, incl. absent)
    classification: str = ""     # CROSSPOLLINATE / VERSION / STANDALONE / NEEDS REVIEW / PARSE ERROR / EMPTY
    hash_groups: Dict[str, List[str]] = field(default_factory=dict)   # hash -> [client names]
    rule_id: str = ""
    version_map: Dict[str, str] = field(default_factory=dict)         # client -> version label
    notes: str = ""


def parse_client_cell(client: str, raw_sql) -> ClientQuery:
    is_blank = raw_sql is None or (isinstance(raw_sql, float) and pd.isna(raw_sql)) or str(raw_sql).strip() == ""
    cq = ClientQuery(client=client, raw_sql="" if is_blank else str(raw_sql), present=not is_blank)
    if is_blank:
        return cq

    tree, error, pretty = clean_and_parse(raw_sql)
    cq.pretty_sql = pretty
    if error:
        cq.error = error
        return cq
    if tree is None:
        cq.present = False
        return cq
    cq.tree = tree
    cq.norm_tree = normalize(tree)
    cq.hash_ = logic_hash(cq.norm_tree)
    cq.profile = extract_logic_profile(cq.norm_tree)
    return cq


def classify_rule(rule_name: str, row: "pd.Series", client_names: List[str]) -> RuleResult:
    result = RuleResult(rule_name=rule_name)
    for client in client_names:
        result.clients[client] = parse_client_cell(client, row.get(client))

    present = [cq for cq in result.clients.values() if cq.present]
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

    groups: Dict[str, List[str]] = {}
    for cq in usable:
        groups.setdefault(cq.hash_, []).append(cq.client)
    result.hash_groups = groups

    if len(usable) == 1:
        result.classification = "STANDALONE"
        return result

    if len(groups) == 1:
        result.classification = "CROSSPOLLINATE"
        return result

    reps = {h: next(cq for cq in usable if cq.hash_ == h).profile for h in groups}
    hashes = list(groups.keys())
    all_similar = True
    for h1, h2 in itertools.combinations(hashes, 2):
        if table_similarity(reps[h1], reps[h2]) < FAMILY_SIMILARITY_THRESHOLD:
            all_similar = False
            break

    result.classification = "VERSION" if all_similar else "NEEDS REVIEW"

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
        n_clients = len([cq for cq in r.clients.values() if cq.tree is not None])
        if r.classification == "CROSSPOLLINATE":
            wave, effort = 1, 1
        elif r.classification == "STANDALONE":
            wave, effort = 3, 1
        elif r.classification == "VERSION":
            wave, effort = 2, len(r.hash_groups)
        else:
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
            cq = r.clients.get(client)
            if cq is None or not (cq.tree is not None or cq.error):
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
#    Mild, low-contrast Excel-standard palette (Good/Bad/Neutral/Info)
#    plus consistent thin borders on every table.
# --------------------------------------------------------------------

FONT_NAME = "Arial"

GOOD_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")     # crosspollinate
NEUTRAL_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")  # version
INFO_FILL = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")     # standalone
BAD_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")      # needs review
WARN_FILL = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")     # parse error
GREY_FILL = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")     # empty / null
HEADER_FILL = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")   # header banner
BAND_FILL = PatternFill(start_color="F7F9FC", end_color="F7F9FC", fill_type="solid")     # subtle row banding

GOOD_FONT = Font(name=FONT_NAME, color="375623")
NEUTRAL_FONT = Font(name=FONT_NAME, color="7F6000")
INFO_FONT = Font(name=FONT_NAME, color="1F4E78")
BAD_FONT = Font(name=FONT_NAME, color="9C0006")
WARN_FONT = Font(name=FONT_NAME, color="974706")
NORMAL_FONT = Font(name=FONT_NAME)
BOLD_FONT = Font(name=FONT_NAME, bold=True)
WHITE_BOLD = Font(name=FONT_NAME, color="FFFFFF", bold=True)
ITALIC_FONT = Font(name=FONT_NAME, italic=True, color="595959")

CLASS_FILL = {
    "CROSSPOLLINATE": GOOD_FILL,
    "VERSION": NEUTRAL_FILL,
    "STANDALONE": INFO_FILL,
    "NEEDS REVIEW": BAD_FILL,
    "PARSE ERROR": WARN_FILL,
    "EMPTY": GREY_FILL,
}
CLASS_FONT = {
    "CROSSPOLLINATE": GOOD_FONT,
    "VERSION": NEUTRAL_FONT,
    "STANDALONE": INFO_FONT,
    "NEEDS REVIEW": BAD_FONT,
    "PARSE ERROR": WARN_FONT,
    "EMPTY": NORMAL_FONT,
}

THIN_SIDE = Side(style="thin", color="B7B7B7")
THIN_BORDER = Border(left=THIN_SIDE, right=THIN_SIDE, top=THIN_SIDE, bottom=THIN_SIDE)
BOLD_LABEL_FONT = InlineFont(b=True, rFont=FONT_NAME, sz=10)
NORMAL_INLINE_FONT = InlineFont(rFont=FONT_NAME, sz=10)


def _border_range(ws, min_row, max_row, min_col, max_col):
    """Apply a clean thin border grid over a data range (Excel's
    Home > Borders > All Borders, i.e. Alt+H,B,A)."""
    if max_row < min_row or max_col < min_col:
        return
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        for cell in row:
            cell.border = THIN_BORDER


def _autosize(ws, widths: Dict[int, int]):
    for col_idx, width in widths.items():
        ws.column_dimensions[get_column_letter(col_idx)].width = width


def _write_header(ws, headers: List[str], row: int = 1):
    for col_idx, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=col_idx, value=h)
        c.font = WHITE_BOLD
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _classification_row_style(ws, row_idx: int, n_cols: int, classification: str):
    fill = CLASS_FILL.get(classification, GREY_FILL)
    font = CLASS_FONT.get(classification, NORMAL_FONT)
    for col_idx in range(1, n_cols + 1):
        c = ws.cell(row=row_idx, column=col_idx)
        c.fill = fill
        c.font = Font(name=FONT_NAME, bold=True, color=font.color) if col_idx == 1 else font


def sheet_legend_summary(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.active
    ws.title = "Legend & Summary"
    ws.sheet_view.showGridLines = False
    ws.cell(row=1, column=1, value="FastTrack -> Firebird Migration: Crosspollination Report").font = \
        Font(name=FONT_NAME, bold=True, size=14, color="1F4E78")

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
    _border_range(ws, 4, r - 1, 1, 2)

    r += 1
    ws.cell(row=r, column=1, value="Classification counts").font = BOLD_FONT
    r += 1
    counts_start = r
    counts = Counter(res.classification for res in results)
    for label in ["CROSSPOLLINATE", "VERSION", "STANDALONE", "NEEDS REVIEW", "PARSE ERROR", "EMPTY"]:
        c1 = ws.cell(row=r, column=1, value=label)
        c1.font = CLASS_FONT.get(label, NORMAL_FONT)
        c1.fill = CLASS_FILL.get(label, GREY_FILL)
        ws.cell(row=r, column=2, value=counts.get(label, 0)).font = NORMAL_FONT
        r += 1
    _border_range(ws, counts_start, r - 1, 1, 2)

    r += 1
    ws.cell(row=r, column=1, value="Color legend").font = BOLD_FONT
    r += 1
    legend_start = r
    legend = [
        ("CROSSPOLLINATE", "Identical logic across every client that has this rule -- migrate once."),
        ("VERSION", "Same rule family, filtering logic differs by client -- one base rule, multiple versions."),
        ("STANDALONE", "Only exists in one client -- migrate directly, no crosspollination possible."),
        ("NEEDS REVIEW", "Same rule name, unrelated logic -- likely a naming collision. Resolve manually."),
        ("PARSE ERROR", "Could not parse this SQL text -- excluded from comparison, fix and re-run."),
    ]
    for label, desc in legend:
        c1 = ws.cell(row=r, column=1, value=label)
        c1.fill = CLASS_FILL.get(label, GREY_FILL)
        c1.font = CLASS_FONT.get(label, NORMAL_FONT)
        ws.cell(row=r, column=2, value=desc).font = NORMAL_FONT
        r += 1
    _border_range(ws, legend_start, r - 1, 1, 2)

    r += 1
    ws.cell(row=r, column=1, value="Already handled automatically (no manual cleanup needed):").font = BOLD_FONT
    r += 1
    for note in [
        "- Trailing semicolon present on some queries, absent on others",
        "- Extra/inconsistent whitespace and line breaks",
        "- SQL comments (-- line and /* block */)",
        "- Identifier CASE differences: table/column/alias names compared case-insensitively "
        "(string literal values stay case-sensitive)",
        "- Predicate order (WHERE/ON/HAVING), GROUP BY column order, a=b vs b=a",
    ]:
        ws.cell(row=r, column=1, value=note).font = ITALIC_FONT
        r += 1

    ws.column_dimensions["A"].width = 48
    ws.column_dimensions["B"].width = 75


def sheet_master_classification(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Master Classification")
    ws.sheet_view.showGridLines = False
    headers = ["rule_name", "classification", "clients_present", "clients_covered",
               "num_logic_variants", "rule_id_suggestion", "notes"]
    _write_header(ws, headers)

    row_idx = 2
    for r in results:
        present_clients = sorted([c for c, cq in r.clients.items() if cq.tree is not None])
        n_variants = len(r.hash_groups) if r.hash_groups else (1 if present_clients else 0)
        rule_id = f"RULE_{row_idx-1:04d}"
        r.rule_id = rule_id

        values = [r.rule_name, r.classification, ", ".join(present_clients),
                  len(present_clients), n_variants, rule_id, r.notes]
        for col_idx, v in enumerate(values, start=1):
            ws.cell(row=row_idx, column=col_idx, value=v)
        _classification_row_style(ws, row_idx, len(headers), r.classification)
        row_idx += 1

    _autosize(ws, {1: 24, 2: 18, 3: 45, 4: 14, 5: 16, 6: 18, 7: 55})
    ws.freeze_panes = "A2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))


def _filtered_sheet(wb, title: str, results: List[RuleResult], classification: str, client_names: List[str]):
    ws = wb.create_sheet(title)
    ws.sheet_view.showGridLines = False
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
        _autosize(ws, {1: 24, 2: 18, 3: 10, 4: 40, 5: 16, 6: 45})
    else:
        headers = ["rule_name", "rule_id", "clients_present", "notes"]
        _write_header(ws, headers)
        row_idx = 2
        for r in subset:
            present_clients = sorted([c for c, cq in r.clients.items() if cq.tree is not None])
            ws.cell(row=row_idx, column=1, value=r.rule_name)
            ws.cell(row=row_idx, column=2, value=r.rule_id)
            ws.cell(row=row_idx, column=3, value=", ".join(present_clients))
            ws.cell(row=row_idx, column=4, value=r.notes)
            _classification_row_style(ws, row_idx, len(headers), classification)
            row_idx += 1
        _autosize(ws, {1: 24, 2: 18, 3: 45, 4: 55})

    ws.freeze_panes = "A2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))


def _rich_cell(*label_text_pairs: Tuple[str, str]) -> CellRichText:
    """Build a multi-line cell with bold labels followed by normal text,
    e.g. _rich_cell(('Tables used: ', 'table1, table2'),
                     ('Logic differences: ', 'c1.code > 300')).
    """
    blocks = []
    for i, (label, text) in enumerate(label_text_pairs):
        if i > 0:
            blocks.append(TextBlock(NORMAL_INLINE_FONT, "\n"))
        blocks.append(TextBlock(BOLD_LABEL_FONT, label))
        blocks.append(TextBlock(NORMAL_INLINE_FONT, text))
    return CellRichText(*blocks)


def sheet_detailed_diff(wb, results: List[RuleResult], client_names: List[str]):
    """One row per rule, one column per client (matching the master
    input's own shape), plus a final 'Matches' column. Each client cell
    shows that client's own tables-used + logic differences (its actual
    filtering conditions, not a comparison marker); a client with no
    firebird_logic for this rule simply gets the literal text 'null'.
    The Matches column groups clients into identical-logic clusters."""
    ws = wb.create_sheet("Detailed Logic Diff")
    ws.sheet_view.showGridLines = False
    headers = ["rule_name"] + client_names + ["Matches"]
    _write_header(ws, headers)

    row_idx = 2
    for r in results:
        band = (row_idx % 2 == 0)
        row_fill = BAND_FILL if band else None

        name_cell = ws.cell(row=row_idx, column=1, value=r.rule_name)
        name_cell.font = BOLD_FONT
        name_cell.alignment = Alignment(vertical="top", wrap_text=True)
        if row_fill:
            name_cell.fill = row_fill

        for col_idx, client in enumerate(client_names, start=2):
            cq = r.clients.get(client)
            cell = ws.cell(row=row_idx, column=col_idx)
            if cq is None or not cq.present:
                # rule doesn't exist for this client at all
                cell.value = "null"
                cell.font = ITALIC_FONT
                cell.fill = GREY_FILL
            elif cq.error:
                cell.value = f"PARSE ERROR: {cq.error}"
                cell.font = WARN_FONT
                cell.fill = WARN_FILL
            else:
                cell.value = _rich_cell(
                    ("Tables used: ", cq.profile["tables_display"]),
                    ("Logic differences: ", cq.profile["predicates_display"]),
                )
                if row_fill:
                    cell.fill = row_fill
            cell.alignment = Alignment(vertical="top", wrap_text=True)

        # ---- Matches column ----
        null_clients = [c for c in client_names if not r.clients.get(c) or not r.clients[c].present]
        error_clients = [c for c in client_names if r.clients.get(c) and r.clients[c].error]
        ordered_groups = sorted(r.hash_groups.items(), key=lambda kv: -len(kv[1]))

        match_pairs = []
        for i, (h, members) in enumerate(ordered_groups, start=1):
            match_pairs.append((f"Match{i}: ", ", ".join(sorted(members))))
        if error_clients:
            match_pairs.append(("Parse errors: ", ", ".join(sorted(error_clients))))
        if null_clients:
            match_pairs.append(("Nulls: ", ", ".join(sorted(null_clients))))

        matches_cell = ws.cell(row=row_idx, column=len(headers))
        if match_pairs:
            matches_cell.value = _rich_cell(*match_pairs)
        else:
            matches_cell.value = ""
        matches_cell.alignment = Alignment(vertical="top", wrap_text=True)
        if row_fill:
            matches_cell.fill = row_fill

        row_idx += 1

    ws.column_dimensions["A"].width = 26
    for i in range(2, len(client_names) + 2):
        ws.column_dimensions[get_column_letter(i)].width = 34
    ws.column_dimensions[get_column_letter(len(headers))].width = 34
    ws.freeze_panes = "B2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))


def sheet_presence_matrix(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Presence Matrix")
    ws.sheet_view.showGridLines = False
    headers = ["rule_name"] + client_names + ["TOTAL"]
    _write_header(ws, headers)
    row_idx = 2
    for r in results:
        present = {c for c, cq in r.clients.items() if cq.tree is not None or cq.error}
        ws.cell(row=row_idx, column=1, value=r.rule_name)
        total = 0
        for col_idx, c in enumerate(client_names, start=2):
            if c in present:
                ws.cell(row=row_idx, column=col_idx, value=1)
                total += 1
        ws.cell(row=row_idx, column=len(client_names) + 2, value=total)
        row_idx += 1
    _autosize(ws, {1: 24, **{i: 12 for i in range(2, len(client_names) + 3)}})
    ws.freeze_panes = "B2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))


def sheet_wave_plan(wb, wave_df: "pd.DataFrame"):
    ws = wb.create_sheet("Migration Wave Plan")
    ws.sheet_view.showGridLines = False
    if wave_df.empty:
        ws.cell(row=1, column=1, value="No data.")
        return
    headers = list(wave_df.columns)
    _write_header(ws, headers)
    wave_fill = {1: GOOD_FILL, 2: NEUTRAL_FILL, 3: INFO_FILL, 4: BAD_FILL}
    wave_font = {1: GOOD_FONT, 2: NEUTRAL_FONT, 3: INFO_FONT, 4: BAD_FONT}
    row_idx = 2
    for _, row in wave_df.iterrows():
        for col_idx, col in enumerate(headers, start=1):
            val = row[col]
            c = ws.cell(row=row_idx, column=col_idx, value=(None if pd.isna(val) else val))
            c.fill = wave_fill.get(row.get("migration_wave"), GREY_FILL)
            c.font = wave_font.get(row.get("migration_wave"), NORMAL_FONT)
        row_idx += 1
    _autosize(ws, {i: 20 for i in range(1, len(headers) + 1)})
    ws.freeze_panes = "A2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))

    note_row = row_idx + 1
    ws.cell(row=note_row, column=1,
            value="Wave 1 = Crosspollinate (highest coverage first) -> Wave 2 = Version "
                  "(fewest versions first) -> Wave 3 = Standalone -> Wave 4 = Needs Review "
                  "(resolve before migrating).").font = ITALIC_FONT


def sheet_client_readiness(wb, readiness_df: "pd.DataFrame"):
    ws = wb.create_sheet("Client Readiness Score")
    ws.sheet_view.showGridLines = False
    if readiness_df.empty:
        ws.cell(row=1, column=1, value="No data.")
        return
    headers = list(readiness_df.columns)
    _write_header(ws, headers)
    row_idx = 2
    for _, row in readiness_df.iterrows():
        pct = row["readiness_pct_shared_logic"]
        fill = GOOD_FILL if pct >= 66 else (NEUTRAL_FILL if pct >= 33 else BAD_FILL)
        font = GOOD_FONT if pct >= 66 else (NEUTRAL_FONT if pct >= 33 else BAD_FONT)
        for col_idx, col in enumerate(headers, start=1):
            c = ws.cell(row=row_idx, column=col_idx, value=row[col])
            c.fill = fill
            c.font = font
        row_idx += 1
    _autosize(ws, {i: 24 for i in range(1, len(headers) + 1)})
    ws.freeze_panes = "A2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))

    note_row = row_idx + 1
    ws.cell(row=note_row, column=1,
            value="Higher readiness % = more of this client's rules are already shared/"
                  "common logic -- cheaper to onboard. Recommended pilot client is the "
                  "top row.").font = ITALIC_FONT


def sheet_formatted_queries(wb, results: List[RuleResult], client_names: List[str]):
    ws = wb.create_sheet("Formatted Queries (Reference)")
    ws.sheet_view.showGridLines = False
    headers = ["rule_name"] + client_names
    _write_header(ws, headers)
    row_idx = 2
    for r in results:
        ws.cell(row=row_idx, column=1, value=r.rule_name).font = BOLD_FONT
        for col_idx, c in enumerate(client_names, start=2):
            cq = r.clients.get(c)
            cell = ws.cell(row=row_idx, column=col_idx)
            if cq is None or not cq.present:
                cell.value = "null"
                cell.font = ITALIC_FONT
                cell.fill = GREY_FILL
            else:
                cell.value = cq.pretty_sql if cq.pretty_sql else (cq.error or "")
                cell.font = NORMAL_FONT
            cell.alignment = Alignment(wrap_text=True, vertical="top")
        row_idx += 1
    ws.column_dimensions["A"].width = 24
    for i in range(2, len(client_names) + 2):
        ws.column_dimensions[get_column_letter(i)].width = 55
    ws.freeze_panes = "B2"
    _border_range(ws, 1, row_idx - 1, 1, len(headers))


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

    print("[2/5] Formatting and parsing SQL for every rule x client cell "
          "(case-insensitive on identifiers, whitespace/comments/semicolons ignored)...")
    results: List[RuleResult] = []
    for rule_name, row in master_df.iterrows():
        results.append(classify_rule(rule_name, row, client_names))

    print("[3/5] Classifying rules (crosspollinate / version / standalone / needs review)...")
    counts = Counter(r.classification for r in results)
    for label in ["CROSSPOLLINATE", "VERSION", "STANDALONE", "NEEDS REVIEW", "PARSE ERROR"]:
        print(f"      {label}: {counts.get(label, 0)}")

    print("[4/5] Building migration wave plan and client readiness scores...")
    wave_df = build_wave_plan(results)
    readiness_df = build_client_readiness(results, client_names)

    print("[5/5] Writing Excel report...")
    wb = build_workbook(results, client_names, wave_df, readiness_df)

    out_dir = OUTPUT_PATH.strip() if OUTPUT_PATH and OUTPUT_PATH.strip() else (
        os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd())
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