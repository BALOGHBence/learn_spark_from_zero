---
name: fact-check-docs
description: Fact-check the course's Sphinx documentation (docs/source — Markdown pages and Jupyter notebooks) against official Databricks sources, flagging incorrect claims, retired or renamed Databricks product names, outdated behaviours and wrong code, each with a cited docs.databricks.com URL and a suggested fix. Use when the user asks to fact-check, verify, audit, review for accuracy or "check if the docs are correct" for a section, chapter, page or the whole documentation.
argument-hint: "[all | chapter number | path under docs/source | changed]"
---

# Fact-Check the Documentation

Go through pages of the Sphinx documentation in `docs/source/` and check that
every factual claim is correct, current and grounded in official Databricks
sources. The output is a report. Edit files only once the user approves the
fixes.

The project-wide rules in `AGENTS.md` apply throughout, and are the reason this
skill exists:

- **Current names and behaviours only.** The docs must use current Databricks
  product names and describe how the product behaves today.
- **Official sources only.** Ground every verdict in **docs.databricks.com**
  or **Databricks Academy**. Third-party blogs, tutorials, Medium posts, Stack
  Overflow and community forum threads are **never** evidence, even when they
  agree with the doc.
- **Cite a URL for each claim** you verify or refute.
- **Never guess.** If you can't confirm or refute a claim in the official docs,
  mark it **Unverified** and say where in docs.databricks.com the user should
  check it. "I couldn't confirm this" is an acceptable result. A guessed verdict
  is not.

## 1. Resolve the scope

Interpret `$ARGUMENTS`:

| Argument | Pages to check |
|---|---|
| *(empty)* | Ask which scope the user wants. Don't default to `all` without asking. |
| `all` | Every `.md` and `.ipynb` under `docs/source/` |
| A chapter number, e.g. `2` or `02` | Everything in `docs/source/02_*/` |
| A path or glob | Those files (relative to the repo root or to `docs/source/`) |
| `changed` | Files under `docs/source/` that differ from `main`: `git diff --name-only main -- docs/source` plus untracked files from `git status --porcelain docs/source` |

Always exclude `docs/source/conf.py`, `_static/`, `_build/`, and
`docs/jupyter_execute/`, which is generated output.

List the resolved files to the user before starting. If there are more than
about 8 pages, propose checking them chapter by chapter, finishing and
reporting on each chapter before moving to the next. Context fills up fast
with this many pages.

## 2. Extract the claims (one page at a time)

Read the page in full. Use the Read tool for notebooks; it renders cells. Then
list every **checkable claim**:

- **Product and feature names.** For example: Unity Catalog, Lakeflow Spark
  Declarative Pipelines, Lakeflow Jobs, serverless compute, Databricks Connect,
  Photon, Auto Loader, Delta Lake, Liquid clustering, predictive optimization.
- **Behavioural statements.** Defaults, limits, what a setting does, which
  compute types support a feature, version requirements (Databricks Runtime,
  Apache Spark, Databricks Connect, Python), and statements like "X is
  deprecated" or "X is in Public Preview / GA".
- **Code in code cells and fenced blocks.** Method and parameter names,
  defaults, configuration keys (`spark.sql.*`, `spark.databricks.*`), options
  for `readStream`/`writeStream`/Auto Loader, SQL syntax, `dbutils` and CLI
  commands. Check that the code would run on current Databricks compute. For
  example, if the page targets serverless or Databricks Connect, flag APIs that
  aren't supported there, such as the RDD API, `sparkContext`, or some
  `spark.conf` keys.
- **Executed notebook outputs.** Note when the text claims something that the
  cell's own output contradicts.
- **Links.** Any link to Databricks docs should point to a page that exists
  and covers what the text says it does.

Skip pure pedagogy and opinion ("this is a good habit"), and the course's own
structure and navigation.

Record a location for every claim: `path:line` for Markdown, and
`path (cell N)` for notebooks, counting cells from 1.

## 3. Verify each claim

For each claim, find the official page that settles it:

1. If the `databricks-docs` skill is available, use its llms.txt index to find
   candidate pages quickly.
2. Otherwise use `WebSearch` with `site:docs.databricks.com <terms>`, and
   `WebFetch` to read the page. Batch independent searches into one turn.
3. For Databricks Academy, search `site:databricks.com/learn` or
   `site:customer-academy.databricks.com`. Academy course pages often confirm
   only *that* a topic is taught, not the technical detail. Prefer docs pages
   for technical claims.
4. **Exact Apache Spark API signatures** (PySpark parameter names, defaults)
   are often documented only in the Apache Spark API reference. You may use
   `spark.apache.org/docs` for these. It is the project's official
   documentation, not a third-party source. Prefer a docs.databricks.com page
   whenever one covers the point, and label any `spark.apache.org` citation as
   such in the report.

Use the Databricks docs for the cloud the course targets. If the page doesn't
say, prefer the AWS docs (`docs.databricks.com/aws/en/...`). Note when a
behaviour differs between AWS, Azure and GCP.

### Watch for retired and renamed names

Databricks renames products often. Before you call any name current, confirm
it on docs.databricks.com during this run. Don't trust memory or this list.
Known renames to check for:

| Retired or old name | Current name |
|---|---|
| Delta Live Tables (DLT) | Lakeflow Spark Declarative Pipelines |
| Databricks Workflows / Databricks Jobs | Lakeflow Jobs |
| Databricks Asset Bundles (DABs) | Declarative Automation Bundles |
| Genie spaces | Genie Agents |
| UniForm | External Iceberg Reads |
| DBFS mounts / DBFS root for data | Unity Catalog volumes and external locations (DBFS mounts are deprecated) |
| Hive metastore as the default catalog | Unity Catalog |

If you find another old name, verify it and add it to this table at the end of
the run so the next run catches it.

### Verdicts

Give each claim one verdict:

- ✅ **Correct.** An official page confirms it. Cite it.
- ❌ **Incorrect.** An official page contradicts it. Cite it, and quote the
  relevant sentence briefly.
- ⚠️ **Outdated.** It was true once, but the name, default or behaviour has
  changed. Cite the current page.
- ❓ **Unverified.** You found no official page that settles it. Name the
  docs.databricks.com section where the user should look. Never upgrade a claim
  to Correct based on a non-official source.

## 4. Report

For each page, write one section:

```markdown
### docs/source/03_stream_processing_and_analysis/02_spark_structured_streaming.ipynb

**Summary:** 14 claims: 10 ✅ · 1 ❌ · 2 ⚠️ · 1 ❓

| # | Location | Claim (short) | Verdict | Evidence | Suggested fix |
|---|---|---|---|---|---|
| 1 | cell 4 | `trigger(once=True)` is the recommended way to … | ⚠️ Outdated | https://docs.databricks.com/aws/en/structured-streaming/triggers | Use `trigger(availableNow=True)` |
```

Rules for the report:

- List ❌, ⚠️ and ❓ rows first. Collapse the ✅ rows into a short list at the
  end of the page section. They still need URLs, but they don't need a fix
  column.
- Every ✅/❌/⚠️ row has a full URL to the specific page. A link to the docs
  homepage doesn't count.
- A suggested fix is a concrete replacement sentence or code line that matches
  the page's existing tone and the `sphinx-docs:myst-house-style` conventions.
- End the report with a **totals line** across all pages checked, plus a list
  of any pages you didn't get to.

If you couldn't browse at all (web tools unavailable or denied), say so at the
very top. Mark every claim ❓ unless it's checkable from files in the repo, and
give the doc sections to check by hand. Don't produce verdicts from memory.

## 5. Apply fixes, only after approval

Ask the user which fixes to apply: all, by number, or none. Then:

- Edit Markdown pages with the Edit tool. Edit notebooks with NotebookEdit, or
  carefully with Edit on the JSON source. Change only the cell `source`. Leave
  outputs and metadata alone unless the fix changes the code. In that case,
  tell the user the notebook needs re-executing.
- Where it helps the reader, add the official doc link to the page as a normal
  Markdown link.
- Don't fix ❓ items by guessing. Leave them, or reword them as clearly hedged
  only if the user asks.
- Don't commit unless the user asks. If they do, follow `AGENTS.md`: no
  ownership or AI co-author lines in the commit message.
