---
name: certification-quiz
description: Quiz the user with multiple-choice questions drawn from the course's question bank in fixtures/questions (written in the style of the Databricks Certified Associate Developer for Apache Spark exam), withholding every answer until the user responds, then grading with the bank's justifications and cited sources. Use whenever the user asks to be quizzed, tested, drilled or diagnosed on an exam section, objective or Spark topic — e.g. "quiz me on Section 3", "give me 10 practice questions on Structured Streaming", "test me on broadcast joins" — even if they don't mention the exam style or hiding the answers. For a full-length mock exam use the mock-exam skill instead.
---

# Certification Quiz

Run a practice quiz that feels like sitting the real Databricks certification
exam. This skill implements the "Diagnose" step of the Databricks AI Prep
Guide (`resources/ai-prep-guide-any-databricks-certification.pdf`):

> Quiz me with 10 multiple-choice questions on [SECTION], in the style of an
> actual Databricks certification exam. Don't show answers until I respond.

The questions come from the course's **question bank** in
`fixtures/questions/` (about 30 per objective, one YAML file per objective,
validated by `src/project/questions/schema.py`). Each question has exactly
four options, one with verdict `correct`, and every option carries a
`justification`. Each question also has a `source_url` on docs.databricks.com
or spark.apache.org. Don't write your own questions while the bank covers the
scope.

Two rules hold **on every quiz, whether or not the user states them**:

1. **Questions from the bank.** Pick them with the script below. Don't
   paraphrase them or invent new ones.
2. **No answers until the user responds.** Never reveal, hint at, or encode the
   correct option before the user has submitted their answers.

The project-wide rules in `AGENTS.md` also apply: current Databricks product
names only, no invented objectives, ground claims in docs.databricks.com and
Databricks Academy, and say so explicitly when a claim can't be confirmed.

## 1. Resolve the scope

The exam is the **Databricks Certified Associate Developer for Apache Spark**.
Its outline, verbatim, is in
[references/spark-developer-exam-outline.md](references/spark-developer-exam-outline.md)
(source: `resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`).
Objective ids are `<section>.<position in section>`. For example, `3.5` is the
fifth objective of Section 3 (joins and unions).

Map the user's `[SECTION]` to picker flags:

- **A section number or name** ("Section 5", "Using Spark SQL") →
  `--section 5`. The picker spreads the questions evenly over the section's
  objectives.
- **A single objective** → `--objective 3.2`.
- **A free-form topic** ("watermarks", "AQE") → find the objective(s) that
  cover it, then pass them with `--objective`, adding `--grep <keyword>` when
  the topic is narrower than the objective (e.g. `--objective 5.4 --grep
  watermark`). Pass several `--grep` values for synonyms. If **no** objective
  covers the topic, tell the user the topic isn't in the exam guide and ask
  whether they still want a quiz on it. Never present an off-outline topic as
  an exam objective. See "When the bank can't cover the request" below.
- **"Full mock exam"**, "practice exam" or "the whole exam" → hand off to the
  `mock-exam` skill.
- **A different certification** → the bank only covers the Spark Developer
  exam. Ask the user for that exam guide (PDF path or pasted "Sections and
  Objectives") and see "When the bank can't cover the request".

Other defaults, overridable by the user: **10 questions** (`--count`), all
presented at once.

## 2. Pick the questions

Run the picker from the repository root:

```bash
uv run python .claude/skills/certification-quiz/scripts/pick_questions.py --section 3 --count 10
```

Useful flags: `--objective` and `--section` (repeatable, combinable), `--grep`,
`--count`, `--exclude <id>` (repeatable) and `--seed`. The script picks at
random, shuffles the options and balances the correct letters over A–D.

The output has two parts:

- **QUESTIONS**: the quiz, already formatted with a heading per question, the
  verbatim objective in italics, the stem, and options **A–D**.
- **ANSWER KEY**: for each question, the bank id, the correct letter, every
  option's verdict and justification, and the `source_url`. This is for you
  only.

**Follow-up quizzes**: pass every id already asked in this conversation with
`--exclude`, so the user gets fresh questions.

If the picker warns that fewer questions matched than requested (common with
a narrow `--grep`), tell the user how many the bank has and offer either that
smaller quiz or a broader scope.

### Sanity check before presenting

The bank is curated, but read each picked question and its key before showing
it. If a stem or option is broken (garbled formatting, leftover YAML
characters, a missing code block) or the keyed answer looks wrong to you:

- swap it out by re-running the picker with that id in `--exclude`;
- if you believe the answer is wrong, check it against the `source_url`. If
  it is wrong, tell the user the bank id and what needs fixing, after the quiz
  so you don't give anything away.

### When the bank can't cover the request

Only for a topic outside the exam guide that the user still wants to be
quizzed on, or for a different certification, write the questions yourself in
the bank's style: a short scenario stem ending in one direct question, exactly
four options A–D with exactly one correct, plausible distractors that are each
wrong for a reason you can explain in one sentence, PySpark in fenced code
blocks, and current Databricks names. Verify every answer against
docs.databricks.com (or the Apache Spark API reference for exact signatures)
and keep the URL for grading. If you can't browse, say so once at the top of
the quiz. Tell the user that these questions are not from the bank.

## 3. Presenting the quiz — answers stay hidden

Show only the **QUESTIONS** part, then stop and wait. Do **not**:

- print or paraphrase anything from the answer key, including the bank ids;
- bold, reorder, or otherwise style the correct option differently;
- hide answers in a collapsed block, footnote, spoiler, or encoded text;
- hint in the stem.

End the message with a single instruction such as:

> Reply with your answers (e.g. `1-B, 2-D, 3-A, …`). I'll grade them once you
> respond.

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

Grade against the answer key. Once the user responds:

1. **Score** first: `7 / 10 (70%)`. For context, Databricks does not publish
   the passing score in the exam guide — don't invent one.
2. A compact **results table**: question, your answer, correct answer, ✓/✗.
3. For **each question** (wrong ones first, in more depth):
   - why the correct option is right, based on its justification;
   - for a wrong pick, the misconception behind it, based on that option's
     verdict and justification. A `partially_correct` pick is right in part
     but incomplete. A `true_but_irrelevant` pick states something true that
     doesn't answer the question. Say which applies;
   - the question's `source_url`.
4. **Weak objectives**: list the objectives (verbatim) the user missed, and for
   each point to the matching course page — `grep -ril "<topic>" docs/source`
   and link the page you find. If none exists, say so.
5. **Next step** prompts from the AI Prep Guide the user can run next:
   - Deep dive: "Teach me [OBJECTIVE, verbatim], using only official Databricks
     documentation…"
   - Repair: "Here are the questions I got wrong: … For each: explain my
     misconception, explain why the right answer is right, and give me a
     related question that tests the same concept differently."

Offer a follow-up quiz on the missed objectives (`--objective` for each,
`--exclude` for the ids already asked).
