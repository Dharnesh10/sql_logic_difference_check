# SQL Logic Equivalence Report

## Summary

- Total queries compared: 12
- Distinct logic groups found: 7

| Query | Logic Group | Members in group | Action |
|---|---|---|---|
| q01 | RULE_1 | q01, q02, q03 | Push as new Firebird rule **RULE_1** |
| q02 | RULE_1 | q01, q02, q03 | Reuse **RULE_1** (same logic as `q01`) - do NOT duplicate |
| q03 | RULE_1 | q01, q02, q03 | Reuse **RULE_1** (same logic as `q01`) - do NOT duplicate |
| q04 | RULE_2 | q04 | Push as new Firebird rule **RULE_2** (unique logic) |
| q05 | RULE_3 | q05, q06 | Push as new Firebird rule **RULE_3** |
| q06 | RULE_3 | q05, q06 | Reuse **RULE_3** (same logic as `q05`) - do NOT duplicate |
| q07 | RULE_4 | q07 | Push as new Firebird rule **RULE_4** (unique logic) |
| q08 | RULE_5 | q08, q09, q10 | Push as new Firebird rule **RULE_5** |
| q09 | RULE_5 | q08, q09, q10 | Reuse **RULE_5** (same logic as `q08`) - do NOT duplicate |
| q10 | RULE_5 | q08, q09, q10 | Reuse **RULE_5** (same logic as `q08`) - do NOT duplicate |
| q11 | RULE_6 | q11 | Push as new Firebird rule **RULE_6** (unique logic) |
| q12 | RULE_7 | q12 | Push as new Firebird rule **RULE_7** (unique logic) |

## Groups

### RULE_1  (hash `c703efd69dc2fc97`)
Members: q01, q02, q03

These queries are **logically identical** (structure/order differences only). Push once, reuse one rule id for all of them.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000
```
</details>

### RULE_2  (hash `4288e70ee7493bb3`)
Members: q04

No other query shares this logic.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000
```
</details>

### RULE_3  (hash `97048fb39e0f2c95`)
Members: q05, q06

These queries are **logically identical** (structure/order differences only). Push once, reuse one rule id for all of them.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)
```
</details>

### RULE_4  (hash `606fc55c1c81202f`)
Members: q07

No other query shares this logic.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)
```
</details>

### RULE_5  (hash `c4aae28ab593651d`)
Members: q08, q09, q10

These queries are **logically identical** (structure/order differences only). Push once, reuse one rule id for all of them.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())
```
</details>

### RULE_6  (hash `d574776ba6662b90`)
Members: q11

No other query shares this logic.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())
```
</details>

### RULE_7  (hash `fdee832d03adfa54`)
Members: q12

No other query shares this logic.

<details><summary>Canonical normalized SQL</summary>

```sql
SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())
```
</details>

## Where logic differs (pairwise diff)

This section compares every pair of queries that do **not** share a logic group, to show exactly what changed. If your 12 queries are meant to be independent rules to begin with, only pay attention to pairs you actually expected to match.

### `q01` vs `q04`

- CHANGED: `50000`  -->  `75000`

### `q01` vs `q05`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `0`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `MONTH`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE' = c.account_status`
- ONLY IN q05: `c.account_status`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE'`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q01` vs `q06`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `0`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `MONTH`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q06: `c.account_status`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `'ACTIVE'`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'ACTIVE' = c.account_status`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q01` vs `q07`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `0`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `MONTH`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `'ACTIVE' = c.account_status`
- ONLY IN q07: `c.account_status`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`
- CHANGED: `c.customer_id`  -->  `i.customer_id`

### `q01` vs `q08`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID'`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE'`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- ONLY IN q08: `c.account_status`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q01` vs `q09`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID'`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `c.account_status`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status`
- ONLY IN q09: `b`
- ONLY IN q09: `'ACTIVE'`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q01` vs `q10`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID'`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `'ACTIVE' = c.account_status`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `'ACTIVE'`
- ONLY IN q10: `c.account_status`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q01` vs `q11`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID'`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q11: `'ACTIVE'`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `'ACTIVE' = c.account_status`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `c.account_status`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q01` vs `q12`

- ONLY IN q01: `SUM(o.order_amount)`
- ONLY IN q01: `0 = c.is_blacklisted`
- ONLY IN q01: `o.order_amount`
- ONLY IN q01: `c.is_blacklisted`
- ONLY IN q01: `o.order_status`
- ONLY IN q01: `orders AS o`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q01: `'PAID'`
- ONLY IN q01: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `c.customer_id`
- ONLY IN q01: `c.customer_name`
- ONLY IN q01: `'PAID' = o.order_status`
- ONLY IN q01: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `SUM(o.order_amount) AS total_spent`
- ONLY IN q01: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q01: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q01: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q01: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q01: `o.order_date`
- ONLY IN q01: `12`
- ONLY IN q01: `-12`
- ONLY IN q01: `SUM(o.order_amount) > 50000`
- ONLY IN q01: `o`
- ONLY IN q01: `50000`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `'SUSPENDED' = c.account_status`
- ONLY IN q12: `c.account_status`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q02` vs `q04`

- CHANGED: `50000`  -->  `75000`

### `q02` vs `q05`

- ONLY IN q02: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `MONTH`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `0`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE' = c.account_status`
- ONLY IN q05: `c.account_status`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE'`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q02` vs `q06`

- ONLY IN q02: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `MONTH`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `0`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q06: `c.account_status`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `'ACTIVE'`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'ACTIVE' = c.account_status`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q02` vs `q07`

- ONLY IN q02: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `MONTH`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `0`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `'ACTIVE' = c.account_status`
- ONLY IN q07: `c.account_status`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q02` vs `q08`

- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `'PAID'`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE'`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- ONLY IN q08: `c.account_status`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q02` vs `q09`

- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `'PAID'`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `c.account_status`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status`
- ONLY IN q09: `b`
- ONLY IN q09: `'ACTIVE'`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q02` vs `q10`

- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `'PAID'`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `'ACTIVE' = c.account_status`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `'ACTIVE'`
- ONLY IN q10: `c.account_status`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q02` vs `q11`

- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `'PAID'`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q11: `'ACTIVE'`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `'ACTIVE' = c.account_status`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `c.account_status`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q02` vs `q12`

- ONLY IN q02: `SUM(o.order_amount)`
- ONLY IN q02: `-12`
- ONLY IN q02: `o.order_date`
- ONLY IN q02: `12`
- ONLY IN q02: `SUM(o.order_amount) > 50000`
- ONLY IN q02: `o.order_amount`
- ONLY IN q02: `50000`
- ONLY IN q02: `'PAID' = o.order_status`
- ONLY IN q02: `o.order_status`
- ONLY IN q02: `'PAID'`
- ONLY IN q02: `c.is_blacklisted`
- ONLY IN q02: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `c.customer_name`
- ONLY IN q02: `SUM(o.order_amount) AS total_spent`
- ONLY IN q02: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q02: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q02: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q02: `o`
- ONLY IN q02: `c.customer_id`
- ONLY IN q02: `0 = c.is_blacklisted`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q02: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q02: `orders AS o`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `'SUSPENDED' = c.account_status`
- ONLY IN q12: `c.account_status`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q03` vs `q04`

- CHANGED: `50000`  -->  `75000`

### `q03` vs `q05`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `MONTH`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `0`
- ONLY IN q03: `o`
- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE' = c.account_status`
- ONLY IN q05: `c.account_status`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE'`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q03` vs `q06`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `MONTH`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `0`
- ONLY IN q03: `o`
- ONLY IN q06: `c.account_status`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `'ACTIVE'`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'ACTIVE' = c.account_status`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q03` vs `q07`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `MONTH`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `0`
- ONLY IN q03: `o`
- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `'ACTIVE' = c.account_status`
- ONLY IN q07: `c.account_status`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`
- CHANGED: `c.customer_id`  -->  `i.customer_id`

### `q03` vs `q08`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `'PAID'`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `o`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE'`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- ONLY IN q08: `c.account_status`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q03` vs `q09`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `'PAID'`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `o`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `c.account_status`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status`
- ONLY IN q09: `b`
- ONLY IN q09: `'ACTIVE'`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q03` vs `q10`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `'PAID'`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `o`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `'ACTIVE' = c.account_status`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `'ACTIVE'`
- ONLY IN q10: `c.account_status`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q03` vs `q11`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `'PAID'`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `o`
- ONLY IN q11: `'ACTIVE'`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `'ACTIVE' = c.account_status`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `c.account_status`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q03` vs `q12`

- ONLY IN q03: `SUM(o.order_amount) > 50000`
- ONLY IN q03: `o.order_date`
- ONLY IN q03: `SUM(o.order_amount)`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `50000`
- ONLY IN q03: `'PAID' = o.order_status`
- ONLY IN q03: `o.order_status`
- ONLY IN q03: `-12`
- ONLY IN q03: `o.order_amount`
- ONLY IN q03: `'PAID'`
- ONLY IN q03: `12`
- ONLY IN q03: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q03: `c.customer_name`
- ONLY IN q03: `c.customer_id`
- ONLY IN q03: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `SUM(o.order_amount) AS total_spent`
- ONLY IN q03: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q03: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q03: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q03: `HAVING SUM(o.order_amount) > 50000`
- ONLY IN q03: `0 = c.is_blacklisted`
- ONLY IN q03: `orders AS o`
- ONLY IN q03: `c.is_blacklisted`
- ONLY IN q03: `o`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `'SUSPENDED' = c.account_status`
- ONLY IN q12: `c.account_status`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q04` vs `q05`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `MONTH`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `0`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE' = c.account_status`
- ONLY IN q05: `c.account_status`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE'`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- CHANGED: `o.customer_id`  -->  `i.customer_id`
- CHANGED: `c.customer_id`  -->  `i.customer_id`

### `q04` vs `q06`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `MONTH`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `0`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q06: `c.account_status`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `'ACTIVE'`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'ACTIVE' = c.account_status`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- CHANGED: `o.customer_id`  -->  `i.customer_id`
- CHANGED: `c.customer_id`  -->  `i.customer_id`

### `q04` vs `q07`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `MONTH`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `0`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `'ACTIVE' = c.account_status`
- ONLY IN q07: `c.account_status`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- CHANGED: `c.customer_id`  -->  `i.customer_id`
- CHANGED: `o.customer_id`  -->  `i.customer_id`

### `q04` vs `q08`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `'PAID'`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE'`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- ONLY IN q08: `c.account_status`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q04` vs `q09`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `'PAID'`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `c.account_status`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status`
- ONLY IN q09: `b`
- ONLY IN q09: `'ACTIVE'`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q04` vs `q10`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `'PAID'`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `'ACTIVE' = c.account_status`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `'ACTIVE'`
- ONLY IN q10: `c.account_status`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q04` vs `q11`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `'PAID'`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q11: `'ACTIVE'`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `'ACTIVE' = c.account_status`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `c.account_status`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q04` vs `q12`

- ONLY IN q04: `c.is_blacklisted`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `o.order_date`
- ONLY IN q04: `'PAID' = o.order_status AND 0 = c.is_blacklisted`
- ONLY IN q04: `orders AS o`
- ONLY IN q04: `-12`
- ONLY IN q04: `SUM(o.order_amount) > 75000`
- ONLY IN q04: `SUM(o.order_amount)`
- ONLY IN q04: `12`
- ONLY IN q04: `75000`
- ONLY IN q04: `0 = c.is_blacklisted`
- ONLY IN q04: `'PAID'`
- ONLY IN q04: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.customer_name, SUM(o.order_amount) AS total_spent FROM customers AS c INNER JOIN orders AS o ON c.customer_id = o.customer_id WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE()) GROUP BY c.customer_id, c.customer_name HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `c.customer_name`
- ONLY IN q04: `SUM(o.order_amount) AS total_spent`
- ONLY IN q04: `INNER JOIN orders AS o ON c.customer_id = o.customer_id`
- ONLY IN q04: `WHERE 'PAID' = o.order_status AND 0 = c.is_blacklisted AND o.order_date >= DATEADD(MONTH, -12, GETDATE())`
- ONLY IN q04: `GROUP BY c.customer_id, c.customer_name`
- ONLY IN q04: `HAVING SUM(o.order_amount) > 75000`
- ONLY IN q04: `o.order_amount`
- ONLY IN q04: `o.order_status`
- ONLY IN q04: `'PAID' = o.order_status`
- ONLY IN q04: `o`
- ONLY IN q04: `c.customer_id`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `'SUSPENDED' = c.account_status`
- ONLY IN q12: `c.account_status`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- CHANGED: `o.customer_id`  -->  `b.customer_id`

### `q05` vs `q07`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`

### `q05` vs `q08`

- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID'`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `MONTH`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `0`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- CHANGED: `i.customer_id`  -->  `c.customer_id`
- CHANGED: `i.customer_id`  -->  `b.customer_id`

### `q05` vs `q09`

- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID'`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `0`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `b`
- ONLY IN q09: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `MONTH`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `i.customer_id`  -->  `c.customer_id`
- CHANGED: `i.customer_id`  -->  `b.customer_id`

### `q05` vs `q10`

- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID'`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- ONLY IN q10: `MONTH`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- ONLY IN q10: `0`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q05` vs `q11`

- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID'`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `MONTH`
- ONLY IN q11: `0`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `i.customer_id`  -->  `c.customer_id`
- CHANGED: `i.customer_id`  -->  `b.customer_id`

### `q05` vs `q12`

- ONLY IN q05: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q05: `i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q05: `1`
- ONLY IN q05: `DAY`
- ONLY IN q05: `i.due_date`
- ONLY IN q05: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `GETDATE()`
- ONLY IN q05: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q05: `'ACTIVE'`
- ONLY IN q05: `30`
- ONLY IN q05: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `i.invoice_id`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q05: `FROM invoices AS i`
- ONLY IN q05: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q05: `invoices AS i`
- ONLY IN q05: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q05: `'PAID'`
- ONLY IN q05: `'PAID' <> i.payment_status`
- ONLY IN q05: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q05: `i.payment_status`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `MONTH`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- ONLY IN q12: `0`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q06` vs `q07`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`

### `q06` vs `q08`

- ONLY IN q06: `'PAID'`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `MONTH`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `0`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q06` vs `q09`

- ONLY IN q06: `'PAID'`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `0`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `b`
- ONLY IN q09: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `MONTH`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q06` vs `q10`

- ONLY IN q06: `'PAID'`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- ONLY IN q10: `MONTH`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- ONLY IN q10: `0`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q06` vs `q11`

- ONLY IN q06: `'PAID'`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `MONTH`
- ONLY IN q11: `0`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q06` vs `q12`

- ONLY IN q06: `'PAID'`
- ONLY IN q06: `i`
- ONLY IN q06: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `'ACTIVE'`
- ONLY IN q06: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `1`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q06: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q06: `30`
- ONLY IN q06: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `GETDATE()`
- ONLY IN q06: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q06: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `i.invoice_id`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q06: `FROM invoices AS i`
- ONLY IN q06: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q06: `invoices AS i`
- ONLY IN q06: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q06: `DAY`
- ONLY IN q06: `i.due_date`
- ONLY IN q06: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q06: `'PAID' <> i.payment_status`
- ONLY IN q06: `i.payment_status`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `MONTH`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- ONLY IN q12: `0`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q07` vs `q08`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID'`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q08: `c.last_login_date`
- ONLY IN q08: `MONTH`
- ONLY IN q08: `b`
- ONLY IN q08: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `0 = b.open_balance`
- ONLY IN q08: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `-24`
- ONLY IN q08: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q08: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q08: `account_balances AS b`
- ONLY IN q08: `b.open_balance IS NULL`
- ONLY IN q08: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q08: `0`
- ONLY IN q08: `b.open_balance`
- ONLY IN q08: `NULL`
- ONLY IN q08: `24`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q07` vs `q09`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID'`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q09: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `b.open_balance IS NULL`
- ONLY IN q09: `0 = b.open_balance`
- ONLY IN q09: `b.open_balance`
- ONLY IN q09: `c.last_login_date`
- ONLY IN q09: `0`
- ONLY IN q09: `-24`
- ONLY IN q09: `NULL`
- ONLY IN q09: `b`
- ONLY IN q09: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q09: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q09: `account_balances AS b`
- ONLY IN q09: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `MONTH`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q09: `24`
- ONLY IN q09: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q07` vs `q10`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID'`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q10: `MONTH`
- ONLY IN q10: `0 = b.open_balance`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q10: `24`
- ONLY IN q10: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `c.last_login_date`
- ONLY IN q10: `b`
- ONLY IN q10: `-24`
- ONLY IN q10: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q10: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q10: `account_balances AS b`
- ONLY IN q10: `b.open_balance IS NULL`
- ONLY IN q10: `b.open_balance`
- ONLY IN q10: `NULL`
- ONLY IN q10: `0`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q07` vs `q11`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID'`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `c.last_login_date`
- ONLY IN q11: `b`
- ONLY IN q11: `-24`
- ONLY IN q11: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `b.open_balance`
- ONLY IN q11: `b.open_balance IS NULL`
- ONLY IN q11: `24`
- ONLY IN q11: `MONTH`
- ONLY IN q11: `0`
- ONLY IN q11: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c INNER JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q11: `WHERE 'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q11: `account_balances AS b`
- ONLY IN q11: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q11: `0 = b.open_balance`
- ONLY IN q11: `NULL`
- ONLY IN q11: `'ACTIVE' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- CHANGED: `i.customer_id`  -->  `b.customer_id`
- CHANGED: `i.customer_id`  -->  `c.customer_id`

### `q07` vs `q12`

- ONLY IN q07: `i.invoice_id`
- ONLY IN q07: `1`
- ONLY IN q07: `DAY`
- ONLY IN q07: `WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `CAST(GETDATE() AS DATETIME2)`
- ONLY IN q07: `NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `i.payment_status`
- ONLY IN q07: `EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q07: `i.due_date`
- ONLY IN q07: `GETDATE()`
- ONLY IN q07: `FROM payment_plans AS pp`
- ONLY IN q07: `'ACTIVE'`
- ONLY IN q07: `WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id`
- ONLY IN q07: `payment_plans AS pp`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID'`
- ONLY IN q07: `i.invoice_id = pp.invoice_id`
- ONLY IN q07: `'ACTIVE' = pp.plan_status`
- ONLY IN q07: `pp.invoice_id`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30`
- ONLY IN q07: `'PAID' <> i.payment_status`
- ONLY IN q07: `pp`
- ONLY IN q07: `pp.plan_status`
- ONLY IN q07: `SELECT 'rule_name' AS selectionreason, i.invoice_id, i.customer_id, DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue FROM invoices AS i WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) AS days_overdue`
- ONLY IN q07: `FROM invoices AS i`
- ONLY IN q07: `WHERE 'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2))`
- ONLY IN q07: `invoices AS i`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id) AND NOT EXISTS(SELECT 1 FROM payment_plans AS pp WHERE 'ACTIVE' = pp.plan_status AND i.invoice_id = pp.invoice_id)`
- ONLY IN q07: `'PAID' <> i.payment_status AND DATEDIFF(DAY, CAST(i.due_date AS DATETIME2), CAST(GETDATE() AS DATETIME2)) > 30 AND EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `i`
- ONLY IN q07: `30`
- ONLY IN q07: `CAST(i.due_date AS DATETIME2)`
- ONLY IN q07: `EXISTS(SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id)`
- ONLY IN q07: `SELECT 1 FROM customers AS c WHERE 'ACTIVE' = c.account_status AND c.customer_id = i.customer_id`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `b.open_balance`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `NULL`
- ONLY IN q12: `'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `c.last_login_date`
- ONLY IN q12: `SELECT 'rule_name' AS selectionreason, c.customer_id, c.last_login_date FROM customers AS c LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `WHERE 'SUSPENDED' = c.account_status AND 0 = b.open_balance OR b.open_balance IS NULL AND c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `account_balances AS b`
- ONLY IN q12: `c.last_login_date < DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `DATEADD(MONTH, -24, GETDATE())`
- ONLY IN q12: `0 = b.open_balance OR b.open_balance IS NULL`
- ONLY IN q12: `-24`
- ONLY IN q12: `b.open_balance IS NULL`
- ONLY IN q12: `MONTH`
- ONLY IN q12: `24`
- ONLY IN q12: `0 = b.open_balance`
- ONLY IN q12: `b`
- ONLY IN q12: `0`
- CHANGED: `i.customer_id`  -->  `c.customer_id`
- CHANGED: `i.customer_id`  -->  `b.customer_id`

### `q08` vs `q11`

- ONLY IN q08: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`

### `q08` vs `q12`

- ONLY IN q08: `'ACTIVE'`
- ONLY IN q12: `'SUSPENDED'`

### `q09` vs `q11`

- ONLY IN q09: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`

### `q09` vs `q12`

- ONLY IN q09: `'ACTIVE'`
- ONLY IN q12: `'SUSPENDED'`

### `q10` vs `q11`

- ONLY IN q10: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`

### `q10` vs `q12`

- ONLY IN q10: `'ACTIVE'`
- ONLY IN q12: `'SUSPENDED'`

### `q11` vs `q12`

- ONLY IN q11: `'ACTIVE'`
- ONLY IN q11: `INNER JOIN account_balances AS b ON b.customer_id = c.customer_id`
- ONLY IN q12: `'SUSPENDED'`
- ONLY IN q12: `LEFT JOIN account_balances AS b ON b.customer_id = c.customer_id`
