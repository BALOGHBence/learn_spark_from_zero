# Fact-Checking the Documentation

Databricks renames products, changes defaults and moves features from preview
to general availability all the time. A page that was correct when it was
written can go out of date without anyone touching it. This repository ships a
[Claude Code](https://claude.com/claude-code) skill, `fact-check-docs`, that
goes through the pages in `docs/source/` and checks them against official
Databricks sources.

Run it from time to time, not just once. See
{ref}`when to run it <when-to-run-fact-check>` below.

## What the Skill Checks

The skill lives in `.claude/skills/fact-check-docs/`. It reads each Markdown
page and notebook and pulls out every checkable claim:

- **Product and feature names.** It flags retired names that are presented as
  current, for example "Delta Live Tables" instead of Lakeflow pipelines,
  which extend Apache Spark Declarative Pipelines
  ([Spark Declarative Pipelines](https://docs.databricks.com/aws/en/ldp/)).
- **Behaviour.** Defaults, limits, version requirements, which compute types
  support a feature, and preview or GA status.
- **Code.** Method and parameter names, configuration keys, and whether the
  code runs on serverless compute and Databricks Connect, which is the setup
  this course targets.
- **Links and notebook outputs.** Links to Databricks docs must point to pages
  that exist, and the text must not contradict a cell's own output.

The skill follows the rules in `AGENTS.md`. Evidence must come from
[docs.databricks.com](https://docs.databricks.com) or Databricks Academy, and
every verdict cites a doc page URL. Blogs, tutorials and forum posts are never
accepted as evidence. The one exception is exact PySpark signatures, which may
cite the Apache Spark API reference, and the report labels those citations. If
the skill can't confirm a claim in the official docs, it says so rather than
guessing.

Each claim gets one verdict:

| Verdict | Meaning |
|---|---|
| ✅ Correct | An official page confirms the claim. |
| ❌ Incorrect | An official page contradicts the claim. |
| ⚠️ Outdated | The claim was once true, but the name, default or behaviour has changed. |
| ❓ Unverified | No official page settles the claim. The report says where in the docs to check it by hand. |

The result is a report with one section per page. Problems are listed first,
each with its location (line number, or cell number for notebooks), the
evidence URL and a suggested fix. The skill doesn't edit any file until you
approve the fixes, and it doesn't commit unless you ask.

## Running It

Open Claude Code at the root of the repository and run the command with a
scope:

```text
/fact-check-docs changed
```

checks only the pages that differ from `main`. Use this before you open a pull
request.

```text
/fact-check-docs 3
```

checks one chapter, here everything in `03_stream_processing_and_analysis/`.

```text
/fact-check-docs docs/source/00_getting_started/01_setting_up_databricks_connect.ipynb
```

checks a single page.

```text
/fact-check-docs all
```

checks the whole course. The skill goes through it chapter by chapter and
reports on each chapter before moving to the next.

If you run `/fact-check-docs` without a scope, it asks you for one.

Once the report is in, reply with the fixes to apply, for example "apply 1, 3
and 4" or "apply all". Then review the diff as you would any other change. If a
fix changes a code cell, re-execute that notebook so its outputs match the new
code.

(when-to-run-fact-check)=
## When to Run It

Make the skill a routine part of maintenance:

- **Before merging changes to the docs.** Run `/fact-check-docs changed` on
  your branch.
- **On a regular schedule.** Run one chapter at a time, rotating through the
  course, so every chapter gets checked every few months. A page goes out of
  date because Databricks changed, not because someone edited it, so the
  `changed` scope alone isn't enough.
- **After a significant Databricks release.** For example, a new Databricks
  Runtime or serverless environment version, a product rename, or a change to
  a feature the course teaches. Check the chapters that cover it.
- **Before announcing the course or a new chapter** to learners, run
  `/fact-check-docs all`.

:::{admonition} Note: The Report Supports Your Review, It Doesn't Replace It
:class: note

The report is produced by an AI model. Open the cited page for every ❌ and ⚠️
verdict before you accept a fix, and handle ❓ items by hand. When the skill
finds a renamed product that isn't in its list of known renames, it adds the
new name to the list in `.claude/skills/fact-check-docs/SKILL.md`. Review that
change in the diff as well.
:::
