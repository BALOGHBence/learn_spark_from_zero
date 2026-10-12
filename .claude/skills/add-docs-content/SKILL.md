---
name: add-docs-content
description: Guidelines for adding new teaching content to the course's Sphinx documentation (docs/source — Markdown pages and Jupyter notebooks). Enforces official-only Databricks sources, a cited docs.databricks.com URL next to each claim, an admonition for anything that can't be verified, and a fixed teaching structure — core concept, how it works on Databricks, when to use it vs. alternatives, common mistakes — illustrated with runnable code. Use whenever the user asks to add, write, draft or extend a page, section, notebook or chapter in the docs, e.g. "add a page on broadcast joins", "write a section about Auto Loader", "extend the streaming chapter with stateful operations", even if they don't mention sources or structure.
argument-hint: "<topic> [target chapter or path under docs/source]"
---

# Add Content to the Documentation

Write new teaching material for `docs/source/`. This skill governs **what goes
into the page and where it comes from**. The formatting mechanics (cross-references,
dropdown shape, admonition titles, notebook editing, registering the page in a
toctree) come from `sphinx-docs:myst-house-style`. Load that skill too and
follow both.

The project-wide rules in `AGENTS.md` apply throughout:

- **Current names and behaviours only.** Describe Databricks as it is today.
  Don't invent features, options or exam objectives.
- **Official sources only.** Every factual claim comes from
  **docs.databricks.com** or **Databricks Academy**. Third-party blogs,
  tutorials, Medium posts, Stack Overflow and community forum threads are never
  sources, not even to "confirm" something.
- **Never guess.** If you can't confirm a claim in the official docs, say so
  on the page with an admonition (see step 3). Don't write it as fact.

## 1. Pin down the scope

From `$ARGUMENTS` and the conversation, settle:

- **The topic** and the one question the page answers for the reader.
- **Where it goes.** A new page in an existing chapter, a new section on an
  existing page, or a new chapter. Read the chapter's `index.md` and its
  neighbouring pages so the new material builds on what's already taught and
  doesn't repeat it. If the placement isn't obvious, propose one and ask.
- **Format.** Prefer a Jupyter notebook (`.ipynb`) whenever the page has code,
  which is almost always. Use plain `.md` only for pages without runnable code.

Before writing, show the user a short outline: the page title, the headings
from step 4, the official pages you plan to cite, and where the page sits in
the toctree. Wait for approval if the user asked to review first; otherwise
continue.

## 2. Research in official sources first

Gather the facts before writing any prose.

1. If the `databricks-docs` skill is available, use its llms.txt index to find
   candidate pages.
2. Otherwise use `WebSearch` with `site:docs.databricks.com <terms>`, and
   `WebFetch` to read each page you intend to cite. Batch independent searches
   into one turn. Don't cite a page you haven't opened in this session.
3. For Databricks Academy, search `site:databricks.com/learn` or
   `site:customer-academy.databricks.com`. Academy pages usually only confirm
   *that* a topic is taught. Use docs pages for technical detail.
4. **Exact PySpark API signatures** (parameter names, defaults) may cite the
   Apache Spark API reference at `spark.apache.org/docs`. That's the project's
   own official documentation, not a third-party source. Prefer a
   docs.databricks.com page whenever one covers the point.

Use the AWS docs (`docs.databricks.com/aws/en/...`) unless the page targets
another cloud, and say so in the text when a behaviour differs between clouds.

**Check product names during this run.** Databricks renames products often.
Confirm every product name on docs.databricks.com before using it. The table of
known renames in `.claude/skills/fact-check-docs/SKILL.md` lists names that
must not appear as current (for example "Delta Live Tables" is now Lakeflow
Spark Declarative Pipelines).

**If you can't browse at all** (web tools unavailable or denied), tell the user
before writing anything. Offer to draft the page with every factual claim
wrapped in an "Unverified" admonition (step 3) and a list of the
docs.databricks.com sections to check by hand. Don't write facts from memory
as if they were verified.

## 3. Cite every claim, flag what you can't verify

### Cite next to the claim

Every checkable claim gets the URL of the specific doc page that supports it,
placed **in the same sentence or immediately after it**. A checkable claim is a
product or feature name, a default, a limit, a version requirement, which
compute types support something, preview/GA status, or a statement about how
Databricks or Spark behaves. Use a Markdown link whose text names the doc page:

```markdown
New Delta tables should use liquid clustering instead of partitioning or
`ZORDER` ([Use liquid clustering for tables](https://docs.databricks.com/aws/en/delta/clustering)).
```

Rules:

- Link the **specific page**, with an anchor when it helps
  (`.../clustering#enable-liquid-clustering`). The docs homepage or a section
  landing page doesn't count.
- One citation can cover a short run of sentences that all come from the same
  page. Start a new citation when the source changes.
- Pure pedagogy, analogies and the course's own structure need no citation.
- Mark a `spark.apache.org` citation as such in the link text, e.g.
  `([Apache Spark API reference: DataFrame.join](https://spark.apache.org/docs/...))`.

### Flag what you can't verify

If no official page settles a claim, and the page still needs it, put it in an
admonition instead of the running text:

```markdown
:::{admonition} Unverified: <What the Claim Is About>
:class: warning

<The claim, worded as unconfirmed.> This couldn't be confirmed in the official
Databricks documentation when this page was written. Check
<docs.databricks.com section or search terms> before relying on it.
:::
```

Use `:class: warning` with a title starting `Unverified:` so these stand out
and can be found later with
`grep -rn "Unverified:" docs/source`. Never resolve an unverified claim with a
blog post or a forum answer. If the claim isn't needed, leave it out.

Code output you've actually run counts as evidence for what the code does on
the course's compute. It doesn't count as evidence for documented behaviour,
defaults or guarantees. Those still need a doc page.

## 4. Structure the material

Every page (or every major topic on a page that covers several) covers these
five elements, in this order. Headings may be phrased for the topic, but each
element must be recognisable from its heading.

1. **Core concept.** What it is and what problem it solves, in plain words,
   before any Databricks-specific detail. Link back with `{doc}`/`{ref}` to the
   earlier pages it builds on. Introduce each new term where it's first used.
2. **How it works on Databricks.** The mechanism, and what's specific to
   Databricks: serverless compute, Unity Catalog, Delta Lake, Photon, Databricks
   Runtime versions, defaults that differ from open-source Spark. This is where
   most citations land. Show it with runnable code, and point at the output
   (a plan line, a row count, a metric) that proves the mechanism.
3. **When to use it, and the alternatives.** Name the realistic alternatives
   and the trade-off that decides between them (data size, latency, cost,
   compute type, maintenance). A short comparison table works well when there
   are three or more options. Cite Databricks recommendations where they exist.
4. **Common mistakes.** Under a heading such as `## Common Mistakes`, list the
   errors a learner is likely to make. For each one: what the mistake looks
   like, why it's wrong or slow, and the fix. Ground each mistake in a cited doc
   page (best-practice pages, limitations, "considerations" sections) or in code
   you ran on this page that demonstrates it. Don't invent pitfalls.
5. **Runnable code throughout.** Code isn't a separate section. It illustrates
   elements 2–4. See step 5.

Close the page with a short paragraph that links forward to what comes next,
per `myst-house-style`'s typical page shape. Worked questions with numbers go in
`Example:` dropdowns; side remarks go in `Note:` admonitions.

## 5. Write code the reader can run

The course runs everything through Databricks Connect on serverless compute
(see `docs/source/00_getting_started/01_setting_up_databricks_connect.ipynb`).
Code examples must run as written in that setup.

- **Start the notebook with the course's session setup:**

  ```python
  from pyspark.sql import functions as F

  from project.utils.sparksession import get_spark_session

  spark = get_spark_session(profile="free-edition")
  ```

- **Use data the reader already has:** the `samples` catalog (for example
  `samples.tpch.*`, `samples.nyctaxi.trips`) or small DataFrames built inline
  with `spark.createDataFrame`. No local files and no data that needs
  credentials.
- **Write only to `workspace.default`**, with table names prefixed by the
  chapter and page, e.g. `optimize03_lineitem`. Drop those tables at the top of
  the notebook so it can be re-run.
- **Serverless and Spark Connect compatible.** No RDD API, no `sparkContext`,
  no `spark.conf` keys that serverless doesn't allow, no caching APIs that
  serverless doesn't support. Check the serverless limitations page
  (https://docs.databricks.com/aws/en/compute/serverless/limitations) when
  unsure. If a concept can only be shown on classic compute, say so in a
  `Note:` admonition and show the code as a non-executed fenced block.
- **Small and focused.** One idea per cell, with a sentence before the cell
  saying what to look for in the output.
- **Demonstrating a mistake** with a cell that raises an error: tag that cell
  `raises-exception` in its metadata so the notebook still executes end to end,
  and explain the error message in the next markdown cell.

Execute the notebook and commit it with real outputs. `conf.py` sets
`nb_execution_mode = "off"`, so Sphinx shows whatever outputs are saved in the
file. Ask the user before executing, because it runs on their Databricks
workspace with their `free-edition` profile:

```bash
uv run jupyter execute --inplace docs/source/<chapter>/<page>.ipynb
```

Then read the outputs back, check for `error` outputs in cells not tagged
`raises-exception`, and make every number in the prose match the executed
output. If you can't execute the notebook, tell the user and leave it without
outputs rather than inventing them.

## 6. Final checklist

Before you report back, go through this list and fix anything that fails:

- [ ] Every checkable claim has a specific docs.databricks.com (or labelled
      spark.apache.org) URL next to it, and you opened each page this session.
- [ ] No third-party source is cited or relied on.
- [ ] Every claim you couldn't verify is in an `Unverified:` warning
      admonition, or has been removed.
- [ ] Product names are current and confirmed this session.
- [ ] The page covers core concept, how it works on Databricks, when to use it
      vs. alternatives, and common mistakes, in that order.
- [ ] Code runs on serverless through Databricks Connect, uses the course's
      session setup and data conventions, and the notebook has real outputs
      (or the user knows it hasn't been executed).
- [ ] `myst-house-style` rules are met, and the page is in its chapter's
      `index.md` summary list and toctree.
- [ ] The docs build without new warnings for the page:
      `uv run sphinx-build -b html docs/source docs/_build_test 2>&1 | grep -iE "warning|error"`,
      then `rm -rf docs/_build_test`.

Finish with a short summary for the user: the files added or changed, the
official pages cited, any `Unverified:` admonitions and what would settle them,
and whether the notebook was executed. Suggest running
`/fact-check-docs <path>` on the new page as an independent second check.

Don't commit unless the user asks. If they do, follow `AGENTS.md`: no ownership
or AI co-author lines in the commit message.
