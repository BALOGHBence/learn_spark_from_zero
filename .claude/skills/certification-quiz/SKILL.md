---
name: certification-quiz
description: Quiz the user with multiple-choice questions written in the style of a real Databricks certification exam (default exam is the Databricks Certified Associate Developer for Apache Spark), withholding every answer until the user responds, then grading with explanations grounded in docs.databricks.com. Use whenever the user asks to be quizzed, tested, drilled or diagnosed on an exam section, objective or Spark topic — e.g. "quiz me on Section 3", "give me 10 practice questions on Structured Streaming", "test me on broadcast joins" — even if they don't mention the exam style or hiding the answers. For a full-length mock exam use the mock-exam skill instead.
---

# Certification Quiz

Run a practice quiz that feels like sitting the real Databricks certification
exam. This skill implements the "Diagnose" step of the Databricks AI Prep
Guide (`resources/ai-prep-guide-any-databricks-certification.pdf`):

> Quiz me with 10 multiple-choice questions on [SECTION], in the style of an
> actual Databricks certification exam. Don't show answers until I respond.

Two rules hold **on every quiz, whether or not the user states them**:

1. **Exam style, always.** Every question follows the format of the real exam
   (see "Writing the questions").
2. **No answers until the user responds.** Never reveal, hint at, or encode the
   correct option before the user has submitted their answers.

The project-wide rules in `AGENTS.md` also apply: current Databricks product
names only, no invented objectives, ground claims in docs.databricks.com and
Databricks Academy, and say so explicitly when a claim can't be confirmed.

## 1. Resolve the scope

Default exam: **Databricks Certified Associate Developer for Apache Spark**. Its
outline, verbatim, is in
[references/spark-developer-exam-outline.md](references/spark-developer-exam-outline.md)
(source: `resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`).
Read it before writing questions.

Map the user's `[SECTION]` to the outline:

- **A section number or name** ("Section 5", "Using Spark SQL") → spread the
  questions across *all* objectives in that section, roughly evenly.
- **A single objective** → every question targets that objective, from
  different angles (concept, code, scenario, troubleshooting).
- **A free-form topic** ("watermarks", "AQE") → find the objective(s) that
  cover it and quiz on those. If **no** objective covers it, tell the user the
  topic isn't in the exam guide and ask whether they still want a quiz on it —
  never present an off-outline topic as an exam objective.
- **"Full mock exam"**, "practice exam" or "the whole exam" → hand off to the
  `mock-exam` skill, which runs the full 45-question exam with its own
  blueprint and submission rules.
- **A different certification** → ask the user for that exam guide (PDF path
  or pasted "Sections and Objectives") instead of guessing its outline.

Other defaults, overridable by the user: **10 questions**, all presented at
once, Python (PySpark) for code.

## 2. Writing the questions

Match the sample questions in the official exam guide:

- Number each question and put the targeted objective, **copied verbatim from
  the outline**, in an italic line under the heading:
  `*Objective: Perform data deduplication and validation operations on DataFrames.*`
- Use a short, realistic **scenario stem** ("A data engineer needs to…",
  "A developer notices…") that ends in one direct question ("Which code block
  should the engineer use…?", "Why should the developer choose…?").
- Exactly **four options, A–D, exactly one correct**. No "all/none of the
  above", no multi-select.
- Mix question kinds the way the real exam does: "which code block", "what is
  the result/impact of", "why choose X over Y", and "how should the engineer
  diagnose" questions. At least a third should involve reading code.
- Put code options in fenced `python` (or `sql`) blocks so indentation and
  method chains are readable.
- **Distractors must be plausible.** Use the mistakes a real candidate makes:
  wrong save mode, a parameter that doesn't exist (`descending=True`), swapped
  argument order in `withColumnRenamed`, `na.drop("all")` vs `na.drop()`,
  confusing transformations with actions, client vs cluster mode. Each
  distractor should be wrong for a reason you can explain in one sentence.
- Spread the correct letter across A–D; don't let a pattern emerge.
- Target Apache Spark 4.x as shipped on Databricks. Use current Databricks
  names (Lakeflow Spark Declarative Pipelines, Lakeflow Jobs, Unity Catalog
  volumes, serverless compute) — never a retired name as if it were current.
- Don't reuse the ten sample questions from the exam guide verbatim; the user
  has likely seen them.

### Verify before presenting

Before showing the quiz, check every correct answer — and that every distractor
really is wrong — against official sources. If web tools are available, search
docs.databricks.com (and the Apache Spark API reference for exact PySpark
signatures) and note the URL you'll cite at grading time. If you can't confirm
a question, replace it with one you can confirm. If you cannot browse at all,
say so once at the top of the quiz and point to where in docs.databricks.com
the user should verify.

## 3. Presenting the quiz — answers stay hidden

Output only the questions, then stop and wait. Do **not**:

- print an answer key, "correct answer" marker, or explanations;
- bold, reorder, or otherwise style the correct option differently;
- hide answers in a collapsed block, footnote, spoiler, or encoded text;
- hint in the stem ("note that `na.drop()` defaults to `how='any'`…").

End the message with a single instruction such as:

> Reply with your answers (e.g. `1-B, 2-D, 3-A, …`). I'll grade them once you
> respond.

Keep track of the answer key yourself so grading is consistent with what you
verified.

**While the quiz is open:**

- If the user answers only some questions, ask for the rest — reveal nothing
  yet. If they say they're done, grade what they answered and mark the rest
  as skipped.
- If they ask for a **hint**, give one that narrows the concept without
  eliminating options down to one.
- If they explicitly ask to see an answer ("just tell me #4"), that is a
  response — reveal that one only, and keep the rest hidden.
- If they asked for **one question at a time**, show one, wait, grade it,
  then show the next.

## 4. Grading

Once the user responds:

1. **Score** first: `7 / 10 (70%)`. For context, Databricks does not publish
   the passing score in the exam guide — don't invent one.
2. A compact **results table**: question, your answer, correct answer, ✓/✗.
3. For **each question** (wrong ones first, in more depth):
   - why the correct option is right;
   - for a wrong pick, the specific misconception behind it and why that
     option fails;
   - the doc URL that confirms it (docs.databricks.com preferred). If you
     couldn't verify a point in official docs, say so instead of citing.
4. **Weak objectives**: list the objectives (verbatim) the user missed, and for
   each point to the matching course page — `grep -ril "<topic>" docs/source`
   and link the page you find. If none exists, say so.
5. **Next step** prompts from the AI Prep Guide the user can run next:
   - Deep dive: "Teach me [OBJECTIVE, verbatim], using only official Databricks
     documentation…"
   - Repair: "Here are the questions I got wrong: … For each: explain my
     misconception, explain why the right answer is right, and give me a
     related question that tests the same concept differently."

Offer to run a follow-up quiz focused on the missed objectives.
