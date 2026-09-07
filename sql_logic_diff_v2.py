# Databricks notebook source
# MAGIC %md
# MAGIC # SQL Logic Diff -- TSQL -> Firebird migration helper
# MAGIC
# MAGIC Compares a batch of "same-purpose" legacy T-SQL queries and tells you
# MAGIC which ones are **logically identical** (so you can push a single
# MAGIC Firebird rule id) vs which ones have a **real logic difference**
# MAGIC (so you know to push a new rule/version), even when the SQL text
# MAGIC differs only in predicate order, column order, whitespace, or case.
# MAGIC
# MAGIC **How to use this notebook:**
# MAGIC 1. Run the "Install dependencies" cell, then run the
# MAGIC    `dbutils.library.restartPython()` cell so the newly installed
# MAGIC    package is picked up.
# MAGIC 2. Run the "Library code" cell (defines all the comparison logic).
# MAGIC 3. In the last section, edit the `SQL_FILE_PATH` variable to point at
# MAGIC    your `.sql` file, then run that cell (and the ones after it) to
# MAGIC    get the report.

# COMMAND ----------

# MAGIC %md ## 1. Install dependencies

# COMMAND ----------

# MAGIC %pip install sqlglot --quiet

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md ## 2. Library code
# MAGIC Run this cell once per session. It defines everything the comparison
# MAGIC needs; nothing here needs editing.

# COMMAND ----------

#!/usr/bin/env python3
"""
sql_logic_diff.py
==================

Compares a batch of "same-purpose" legacy T-SQL queries to determine whether
their LOGIC is identical, even if their textual structure differs (predicate
order, column order in an inner SELECT, whitespace/case, etc.).

Use case: TSQL -> Firebird migration. You have ~12 legacy queries that are
supposed to implement the same rule. This script:

  1. Parses each query into an AST (sqlglot).
  2. Normalizes away order-only / cosmetic differences:
       - identifier case (table/column/alias names)
       - order of AND/OR-connected predicates (WHERE, ON, HAVING, JOIN ON)
       - order of columns in inner SELECT lists (only where output ordering
         doesn't matter -- see CAVEATS below)
       - whitespace/formatting
  3. Hashes the normalized AST -> queries with the same hash have IDENTICAL
     logic and can share a single Firebird rule id.
  4. For queries that do NOT hash the same, runs a structural diff
     (sqlglot.diff) on the normalized ASTs and produces a human-readable
     report of exactly which literals / columns / operators / joins differ.
  5. Emits a CSV/markdown report:  query_name | group_id | verdict | details.

CAVEATS (read before trusting the output blindly):
  - Reordering columns in an OUTER-most SELECT changes result-set column
    order. This script does NOT normalize order in the outermost SELECT's
    projection list, only in nested subqueries' SELECT lists (since those
    are only consumed by name via an alias, not by position) and in
    AND/OR predicate chains. If you also use SELECT * anywhere, be careful:
    the script does not attempt to resolve * against a real schema.
  - This is a static/textual-logic equivalence check. It cannot tell you
    two DIFFERENT-looking predicates are mathematically equivalent
    (e.g. `a > 5` vs `NOT (a <= 5)`, or `a IN (1,2)` vs `a=1 OR a=2`).
    It DOES normalize away: predicate/column reordering, identifier case,
    whitespace, comments, GROUP BY order, and symmetric comparisons
    (a=b vs b=a).
  - It does not execute the queries or compare against real data. For a
    final sign-off you should still run both queries against a
    representative dataset and diff the result sets.

USAGE:
    Simplest case -- just point it at a .sql file with your queries,
    each ending in a semicolon:

        python3 sql_logic_diff.py my_queries.sql

    If the file has no query names, queries are auto-named query1,
    query2, ... in the order they appear in the file. To control the
    names (recommended), add a "-- name: <query_name>" comment line
    right before each query:

        -- name: high_value_customer_discount
        SELECT ...
        ;
        -- name: overdue_invoice_flag
        SELECT ...
        ;

    A results markdown report is written to sql_logic_report.md by
    default (override with --out report.md).

    You can also point it at a folder with one .sql file per query
    (filename becomes the query name):

        python3 sql_logic_diff.py queries/

    Optional flags:
        --dialect tsql      Source SQL dialect for parsing (default: tsql)
        --out report.md     Where to write the markdown report
"""

import argparse
import hashlib
import itertools
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import sqlglot
from sqlglot import exp


# --------------------------------------------------------------------------
# 1. Loading queries
# --------------------------------------------------------------------------

NAME_MARKER_RE = re.compile(r"--\s*name:\s*(.+)", re.IGNORECASE)


def _has_name_markers(content: str) -> bool:
    return bool(NAME_MARKER_RE.search(content))


def load_from_marked_content(content: str) -> Dict[str, str]:
    """Split a file that uses '-- name: <query_name>' comment markers."""
    queries: Dict[str, str] = {}
    current_name: Optional[str] = None
    buf: List[str] = []

    def flush():
        if current_name is not None:
            sql = "\n".join(buf).strip()
            if sql:
                queries[current_name] = sql

    for line in content.splitlines():
        m = NAME_MARKER_RE.match(line.strip())
        if m:
            flush()
            current_name = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    flush()
    return queries


def load_from_unmarked_content(content: str, dialect: str) -> Dict[str, str]:
    """No '-- name:' markers found: split the file into individual
    statements (on semicolons, dialect-aware) and auto-name them
    query1, query2, ... in file order."""
    statements = sqlglot.parse(content, read=dialect)
    queries: Dict[str, str] = {}
    idx = 0
    for stmt in statements:
        if stmt is None:
            continue
        idx += 1
        queries[f"query{idx}"] = stmt.sql(dialect=dialect)
    return queries


def load_from_dir(path: str) -> Dict[str, str]:
    queries = {}
    for fname in sorted(os.listdir(path)):
        if fname.lower().endswith(".sql"):
            name = os.path.splitext(fname)[0]
            with open(os.path.join(path, fname), "r", encoding="utf-8") as f:
                queries[name] = f.read()
    if not queries:
        raise SystemExit(f"No .sql files found in {path}")
    return queries


def load_queries(path: str, dialect: str) -> Dict[str, str]:
    """Main entry point: read one .sql file and return {query_name: sql}.

    - If the file contains '-- name: <query_name>' markers, split on those.
    - Otherwise, auto-split on statement boundaries and name them
      query1, query2, ... in the order they appear in the file.
    """
    if os.path.isdir(path):
        return load_from_dir(path)

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if _has_name_markers(content):
        queries = load_from_marked_content(content)
        if queries:
            return queries
        # fall through to auto-split if markers existed but nothing parsed

    queries = load_from_unmarked_content(content, dialect)
    if not queries:
        raise SystemExit(f"Could not find any SQL statements in {path}")
    return queries


# --------------------------------------------------------------------------
# 2. Normalization
# --------------------------------------------------------------------------

# Node types whose SELECT projection order is safe to normalize because the
# result is only ever consumed by column NAME (an aliased subquery / CTE),
# never by position. The outermost query is deliberately excluded because
# its column order is part of the observable output contract.
def _is_named_subquery_select(select_node: exp.Select) -> bool:
    parent = select_node.parent
    # Subquery( Select ) with an alias -> derived table, referenced by name
    if isinstance(parent, exp.Subquery) and parent.alias:
        return True
    # CTE( Select ) -> referenced by name
    if isinstance(parent, exp.CTE):
        return True
    return False


def _sort_key(node: exp.Expression) -> str:
    """Stable sort key for otherwise-order-independent siblings."""
    return node.sql(normalize=True).lower()


def _flatten_and_sort_connector(node: exp.Connector) -> exp.Expression:
    """Turn a (possibly nested) AND/OR chain into a canonical, sorted,
    left-deep chain of the same connector type. Mixed AND/OR nesting is
    preserved (we only reorder within a single connector's own flatten())."""
    cls = type(node)
    parts = list(node.flatten())
    parts_sql_sorted = sorted(parts, key=_sort_key)
    # rebuild left-deep: (((p0 OP p1) OP p2) OP p3) ...
    result = parts_sql_sorted[0]
    for p in parts_sql_sorted[1:]:
        result = cls(this=result, expression=p)
    return result


def _normalize_recursive(node: exp.Expression) -> exp.Expression:
    """True post-order (children-first) traversal that applies
    _canonicalize_node to every node after its children have already been
    fully normalized. We do NOT use Expression.transform() here: sqlglot's
    transform() uses a pruning DFS that stops descending into a subtree
    once a node is replaced with a new object -- which would silently skip
    normalizing anything nested under a WHERE/AND chain that itself got
    rebuilt (e.g. an AND inside an EXISTS(...) subquery one level below a
    top-level AND). Explicit recursion avoids that trap.
    """
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


def _canonicalize_node(node: exp.Expression) -> exp.Expression:
    """Canonicalize a single node whose children are already normalized:
    sort AND/OR chains, and canonicalize symmetric comparisons (a=b <=> b=a,
    a<>b <=> b<>a) by sorting their operands -- a very common source of
    cosmetic diffs in hand-written legacy SQL (e.g. join conditions written
    "t1.id = t2.id" in one query and "t2.id = t1.id" in another)."""
    if isinstance(node, exp.Connector):
        return _flatten_and_sort_connector(node)
    if isinstance(node, (exp.EQ, exp.NEQ)):
        left, right = node.this, node.expression
        if _sort_key(left) > _sort_key(right):
            node.set("this", right)
            node.set("expression", left)
        return node
    return node


def normalize(expression: exp.Expression) -> exp.Expression:
    """Return a *new* normalized copy of the AST suitable for hashing /
    equality comparison. Cosmetic-only differences are erased:
      - identifier case
      - AND/OR predicate order (WHERE / ON / HAVING, recursively)
      - column order inside named (aliased) derived-table / CTE SELECTs
      - literal string quoting style (handled by sqlglot's own renderer)
    """
    tree = expression.copy()

    # a0) strip SQL comments -- they're documentation, not logic, and
    #     sqlglot attaches them to nodes which would otherwise pollute
    #     both the canonical SQL/hash and the diff output.
    for node in tree.walk():
        if node.comments:
            node.comments = None

    # a) lower-case all identifiers (tables, columns, aliases) -- SQL
    #    identifiers are case-insensitive in both TSQL and Firebird
    #    (unless quoted, which we conservatively leave untouched).
    for node in tree.walk():
        if isinstance(node, exp.Identifier) and not node.args.get("quoted"):
            node.set("this", node.this.lower())

    # b) normalize AND/OR chains everywhere (WHERE, ON, HAVING, CASE, etc.),
    #    and canonicalize symmetric comparisons (a=b <=> b=a). Done via
    #    explicit post-order recursion -- see _normalize_recursive docstring
    #    for why Expression.transform() is unsafe here.
    tree = _normalize_recursive(tree)

    # c) sort projection order inside named derived tables / CTEs (NOT the
    #    outermost SELECT -- see _is_named_subquery_select docstring).
    for select_node in list(tree.find_all(exp.Select)):
        if _is_named_subquery_select(select_node):
            exprs = select_node.expressions
            if exprs:
                sorted_exprs = sorted(exprs, key=_sort_key)
                select_node.set("expressions", sorted_exprs)

    # d) sort GROUP BY columns -- their order doesn't affect the logic or
    #    the result rows/values, only an internal grouping detail.
    for group_node in tree.find_all(exp.Group):
        exprs = group_node.expressions
        if exprs:
            group_node.set("expressions", sorted(exprs, key=_sort_key))

    return tree


def canonical_sql(tree: exp.Expression) -> str:
    return tree.sql(dialect="tsql", normalize=True).strip()


def logic_hash(tree: exp.Expression) -> str:
    return hashlib.sha256(canonical_sql(tree).encode("utf-8")).hexdigest()[:16]


# --------------------------------------------------------------------------
# 3. Diffing two non-identical queries
# --------------------------------------------------------------------------

def summarize_diff(name_a: str, tree_a: exp.Expression,
                    name_b: str, tree_b: exp.Expression) -> List[str]:
    """Human-readable list of real (non-cosmetic) differences between two
    already-normalized ASTs."""
    edits = sqlglot.diff(tree_a, tree_b, delta_only=True)
    findings: List[str] = []

    for edit in edits:
        kind = type(edit).__name__  # Insert / Remove / Update / Move / Keep
        if kind == "Keep":
            continue

        if kind == "Update":
            src, tgt = edit.source, edit.target
            findings.append(
                f"CHANGED: `{src.sql(dialect='tsql')}`  -->  `{tgt.sql(dialect='tsql')}`"
            )
        elif kind == "Insert":
            node = edit.expression
            findings.append(f"ONLY IN {name_b}: `{node.sql(dialect='tsql')}`")
        elif kind == "Remove":
            node = edit.expression
            findings.append(f"ONLY IN {name_a}: `{node.sql(dialect='tsql')}`")
        elif kind == "Move":
            # After our normalization pass, pure reordering shouldn't
            # produce Move edits anymore -- but if the moved subtree's
            # rendered SQL is identical, it truly is just noise, so skip it.
            src_sql = edit.source.sql(dialect="tsql")
            tgt_sql = edit.target.sql(dialect="tsql")
            if src_sql != tgt_sql:
                findings.append(f"MOVED/CHANGED: `{src_sql}`  -->  `{tgt_sql}`")

    # De-duplicate while preserving order
    seen = set()
    deduped = []
    for f_ in findings:
        if f_ not in seen:
            seen.add(f_)
            deduped.append(f_)
    return deduped


# --------------------------------------------------------------------------
# 4. Orchestration
# --------------------------------------------------------------------------

@dataclass
class ParsedQuery:
    name: str
    raw_sql: str
    tree: Optional[exp.Expression] = None
    norm_tree: Optional[exp.Expression] = None
    hash_: Optional[str] = None
    error: Optional[str] = None


def parse_all(queries: Dict[str, str], dialect: str) -> List[ParsedQuery]:
    parsed = []
    for name, sql in queries.items():
        pq = ParsedQuery(name=name, raw_sql=sql)
        try:
            tree = sqlglot.parse_one(sql, read=dialect)
            pq.tree = tree
            pq.norm_tree = normalize(tree)
            pq.hash_ = logic_hash(pq.norm_tree)
        except Exception as e:  # noqa: BLE001
            pq.error = str(e)
        parsed.append(pq)
    return parsed


def group_by_logic(parsed: List[ParsedQuery]) -> Dict[str, List[ParsedQuery]]:
    groups: Dict[str, List[ParsedQuery]] = {}
    for pq in parsed:
        if pq.error:
            continue
        groups.setdefault(pq.hash_, []).append(pq)
    return groups


def build_report(parsed: List[ParsedQuery]) -> str:
    lines = []
    lines.append("# SQL Logic Equivalence Report\n")

    errored = [pq for pq in parsed if pq.error]
    if errored:
        lines.append("## Parse errors (excluded from comparison)\n")
        for pq in errored:
            lines.append(f"- **{pq.name}**: {pq.error}")
        lines.append("")

    ok = [pq for pq in parsed if not pq.error]
    groups = group_by_logic(ok)

    # Stable group ordering: order of first appearance
    ordered_hashes = []
    for pq in ok:
        if pq.hash_ not in ordered_hashes:
            ordered_hashes.append(pq.hash_)

    lines.append("## Summary\n")
    lines.append(f"- Total queries compared: {len(ok)}")
    lines.append(f"- Distinct logic groups found: {len(groups)}")
    lines.append("")

    lines.append("| Query | Logic Group | Members in group | Action |")
    lines.append("|---|---|---|---|")
    group_id_map = {h: f"RULE_{i+1}" for i, h in enumerate(ordered_hashes)}
    for pq in ok:
        gid = group_id_map[pq.hash_]
        members = [m.name for m in groups[pq.hash_]]
        if len(members) > 1:
            canonical_member = members[0]
            if pq.name == canonical_member:
                action = f"Push as new Firebird rule **{gid}**"
            else:
                action = f"Reuse **{gid}** (same logic as `{canonical_member}`) - do NOT duplicate"
        else:
            action = f"Push as new Firebird rule **{gid}** (unique logic)"
        lines.append(f"| {pq.name} | {gid} | {', '.join(members)} | {action} |")
    lines.append("")

    lines.append("## Groups\n")
    for h in ordered_hashes:
        members = groups[h]
        gid = group_id_map[h]
        lines.append(f"### {gid}  (hash `{h}`)")
        lines.append(f"Members: {', '.join(m.name for m in members)}\n")
        if len(members) > 1:
            lines.append("These queries are **logically identical** "
                          "(structure/order differences only). "
                          "Push once, reuse one rule id for all of them.\n")
        else:
            lines.append("No other query shares this logic.\n")
        lines.append("<details><summary>Canonical normalized SQL</summary>\n")
        lines.append("```sql")
        lines.append(canonical_sql(members[0].norm_tree))
        lines.append("```")
        lines.append("</details>\n")

    # Pairwise diff report: for queries that are believed to represent the
    # "same rule" but landed in DIFFERENT groups, show exactly what changed.
    # We pair every query against every other query that is NOT in its own
    # group, so you can see, e.g., "query1 vs query1_v2: filter changed".
    lines.append("## Where logic differs (pairwise diff)\n")
    lines.append(
        "This section compares every pair of queries that do **not** share "
        "a logic group, to show exactly what changed. If your 12 queries "
        "are meant to be independent rules to begin with, only pay "
        "attention to pairs you actually expected to match.\n"
    )

    any_diff_printed = False
    for pq_a, pq_b in itertools.combinations(ok, 2):
        if pq_a.hash_ == pq_b.hash_:
            continue
        diffs = summarize_diff(pq_a.name, pq_a.norm_tree, pq_b.name, pq_b.norm_tree)
        if not diffs:
            continue
        any_diff_printed = True
        lines.append(f"### `{pq_a.name}` vs `{pq_b.name}`\n")
        for d in diffs:
            lines.append(f"- {d}")
        lines.append("")

    if not any_diff_printed:
        lines.append("_No cross-group pairs to diff (either all queries "
                      "match, or every query is already unique)._\n")

    return "\n".join(lines)


# COMMAND ----------

# MAGIC %md ## 3. Set your SQL file path here and run
# MAGIC
# MAGIC Just edit the `SQL_FILE_PATH` variable below to point at your file,
# MAGIC then run this cell. `SQL_FILE_PATH` can be:
# MAGIC - a Unity Catalog Volume path, e.g. `/Volumes/my_catalog/my_schema/my_volume/queries.sql`
# MAGIC - a DBFS path, e.g. `/dbfs/FileStore/queries.sql`
# MAGIC - a workspace file path, e.g. `/Workspace/Users/you@company.com/queries.sql`
# MAGIC
# MAGIC Your file can either use `-- name: <query_name>` markers before each
# MAGIC query, or just be plain queries separated by semicolons (they'll be
# MAGIC auto-named query1, query2, ...).

# COMMAND ----------

# ===== EDIT THIS =====
SQL_FILE_PATH = "/Volumes/main/default/queries/queries.sql"
DIALECT = "tsql"
# ======================

queries = load_queries(SQL_FILE_PATH, DIALECT)
print(f"Loaded {len(queries)} queries: {', '.join(queries.keys())}")

parsed = parse_all(queries, DIALECT)
report_md = build_report(parsed)

# COMMAND ----------

# MAGIC %md ## 4. View the report
# MAGIC Rendered inline below.

# COMMAND ----------

displayHTML(f"<pre style='white-space:pre-wrap;font-family:monospace'>{report_md}</pre>")

# COMMAND ----------

# MAGIC %md ## 5. (Optional) Save the report to a file
# MAGIC Edit `OUTPUT_PATH` below if you want to save/share the report.

# COMMAND ----------

# ===== EDIT THIS =====
OUTPUT_PATH = "/Volumes/main/default/queries/sql_logic_report.md"
# ======================

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(report_md)

print(f"Report written to: {OUTPUT_PATH}")

# COMMAND ----------

# MAGIC %md ## 6. (Optional) See the grouping as a table
# MAGIC Handy if you want to filter/sort/export the summary rather than read
# MAGIC the markdown.

# COMMAND ----------

import pandas as pd

ok = [pq for pq in parsed if not pq.error]
groups = group_by_logic(ok)
ordered_hashes = []
for pq in ok:
    if pq.hash_ not in ordered_hashes:
        ordered_hashes.append(pq.hash_)
group_id_map = {h: f"RULE_{i+1}" for i, h in enumerate(ordered_hashes)}

rows = []
for pq in ok:
    gid = group_id_map[pq.hash_]
    members = [m.name for m in groups[pq.hash_]]
    canonical_member = members[0]
    is_canonical = pq.name == canonical_member
    rows.append({
        "query_name": pq.name,
        "logic_group": gid,
        "group_members": ", ".join(members),
        "is_unique_logic": len(members) == 1,
        "action": ("Push as new Firebird rule" if is_canonical or len(members) == 1
                   else f"Reuse {gid} (same logic as {canonical_member})"),
    })

summary_df = pd.DataFrame(rows)
display(spark.createDataFrame(summary_df))