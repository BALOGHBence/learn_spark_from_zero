---
name: mock-exam
description: Run a full-length mock exam for the Databricks Certified Associate Developer for Apache Spark — 45 exam-style multiple-choice questions drawn from the course's question bank in fixtures/questions, the number of scored questions in the official exam guide, spread over every objective in proportion to the outline — and reveal no answer, hint or score until the user has submitted all responses, then grade with a per-section breakdown, the bank's justifications and cited sources. Use whenever the user asks for a mock exam, practice exam, full exam, full-length test, exam simulation or "the whole exam", even if they don't mention the question count or hidden answers. For shorter quizzes on one section, objective or topic use certification-quiz instead.
argument-hint: "[optional: 'timed', or a different exam guide path]"
---

# Mock Exam

Simulate one sitting of the real exam: the same number of scored questions,
spread over the whole outline, with every answer withheld until the user
submits. This is the full-length counterpart of the `certification-quiz`
skill, which covers short quizzes on a section, objective or topic.

The questions come from the course's **question bank** in
`fixtures/questions/` (about 30 per objective, validated by
`src/project/questions/schema.py`), picked by the script the
`certification-quiz` skill also uses. Don't write your own questions.

Two rules hold **on every mock exam, whether or not the user states them**:

1. **Full length, full coverage.** 45 questions, distributed by the blueprint
   below, with every objective in the outline tested at least once.
2. **No answers until everything is submitted.** No answer key, score,
   per-question feedback, hint or "you're doing well" until the user submits
   all responses. This is stricter than `certification-quiz`, see step 4.

The project-wide rules in `AGENTS.md` also apply: current Databricks product
names only, no invented objectives, ground every answer in docs.databricks.com
or Databricks Academy, and say so explicitly when a claim can't be confirmed.

## 1. The exam and its blueprint

The exam is the **Databricks Certified Associate Developer for Apache Spark**.
Its outline, verbatim, is in
[../certification-quiz/references/spark-developer-exam-outline.md](../certification-quiz/references/spark-developer-exam-outline.md)
(source: `resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`).
Read it before picking questions.

The guide states **45 scored multiple-choice questions** and **90 minutes**.
It does **not** publish section weights. The only proportion it implies is how
many objectives each section lists, so the blueprint gives every objective an
equal share of the 45 questions (45 / 32 ≈ 1.4 per objective), rounds the
section totals with the largest-remainder method, and breaks the one tie
(Sections 2 and 5) in favour of the earlier section:

| Section | Objectives | Questions | Share |
|---|---:|---:|---:|
| 1: Apache Spark Architecture and Components | 7 | 10 | 22% |
| 2: Using Spark SQL | 4 | 6 | 13% |
| 3: Developing Apache Spark™ DataFrame/DataSet API Applications | 10 | 14 | 31% |
| 4: Troubleshooting and Tuning Apache Spark DataFrame API Applications | 3 | 4 | 9% |
| 5: Structured Streaming | 4 | 5 | 11% |
| 6: Using Spark Connect to deploy applications | 2 | 3 | 7% |
| 7: Using Pandas API on Spark | 2 | 3 | 7% |
| **Total** | **32** | **45** | **100%** |

Within a section, every objective gets one question, and the section's
remaining questions go to different objectives, one extra each. The objectives
that get the extra question are chosen at random on each run, so repeated mock
exams don't all lean the same way. The picker script implements this table in
`MOCK_BLUEPRINT`.

Never tell the user this blueprint is Databricks' official weighting. If they
ask, explain that it's derived from the objective count because the guide
gives no weights.

**If the outline changes** (a newer guide in `resources/`, or a different
exam): take the number of scored questions from the guide and recompute the
table the same way. If the guide does publish section percentages, use those
instead and say so. Either way, update `MOCK_BLUEPRINT` in the picker script to
match. The question bank only covers this exam. If the user names a different
certification, say there's no bank for it and ask for its exam guide (PDF path
or pasted "Sections and Objectives") instead of guessing.

## 2. Pick the questions

Run the picker in mock mode from the repository root:

```bash
uv run python .claude/skills/certification-quiz/scripts/pick_questions.py --mock
```

It applies the blueprint above, with every objective at least once and the
extra questions on randomly chosen objectives. It then:

- **shuffles the order** so sections are mixed, as an exam form would be;
- **leaves the objective out of each question**, because the objective narrows
  the answer and so acts as a hint. The question → objective mapping is in
  the answer key, for grading;
- **balances the answer key**: each letter A–D is correct on 11–12 questions,
  with no runs of three or more of the same letter in a row.

The output has two parts: **QUESTIONS**, numbered 1–45 and formatted for
display, and **ANSWER KEY**, with each question's bank id, objective, correct
letter, every option's verdict and justification, and the `source_url`.

**Fresh questions on a later mock exam**: pass every bank id already asked in
this conversation with `--exclude` (repeatable). With about 30 questions per
objective, the bank supports many sittings.

### Sanity check before presenting

The bank is curated, but read the picked questions and their key before
showing anything:

- **Broken question** (garbled formatting, leftover YAML characters, a missing
  code block) or **a keyed answer that looks wrong**: re-run the picker with
  that id in `--exclude`. Nothing has been shown yet, so a fresh draw is fine.
  If you believe the bank's answer is wrong, check it against its
  `source_url`, and after grading tell the user the bank id and what needs
  fixing.
- **Near-duplicates**: if two questions on the same objective test the same
  fact, exclude one of them and re-run.

Don't write questions of your own to fill gaps. If the picker reports that an
objective has run out of questions, tell the user and offer a mock exam
without the `--exclude` list.

## 3. Present the exam

Present the questions in **three parts of 15** (Questions 1–15, 16–30, 31–45)
so each message stays readable. Open Part 1 with a short header:

> **Mock exam: Databricks Certified Associate Developer for Apache Spark**
> 45 questions · suggested time 90 minutes · no documentation allowed.
> Answer each part as you go. Nothing is graded until you submit all 45.

If the user asked for a **timed** exam, run `date` when you present Part 1 and
again at submission, and report the elapsed time in the results. Don't enforce
the limit. Just report whether they went over.

After each part, end with one instruction:

> Reply with your answers for this part (e.g. `1-B, 2-D, 3-A, …`) to get the
> next part.

When the user answers a part, reply only with "Recorded N of 45 answers" and
the next part. **Give no feedback on the answers.** After Part 3, list any
unanswered question numbers and ask the user to answer them or confirm
submission ("submit").

Show the questions exactly as the picker formatted them, split into the three
parts. Keep the answer key only in your own working context. Don't write it to
a file, print or paraphrase it (bank ids included), or encode it anywhere the
user could see before submitting. Don't bold, reorder or otherwise mark the
correct option.

## 4. While the exam is open

The user hasn't submitted until they say so after seeing all 45 questions.
Until then:

- **Changing answers** is allowed ("change 7 to C"). Confirm the change only.
- **Hints, single answers, "am I right so far?"**: decline politely. On the
  real exam you can't get feedback mid-exam. Offer two options: carry on, or
  **end the exam now** and have it graded as it stands, with unanswered
  questions scored wrong. Only a clear choice to end the exam counts as
  submitting.
- **Questions about wording** (an ambiguous stem or a typo): clarify the
  wording without hinting at the answer. If the question really is
  ambiguous, say so, mark it to be dropped from scoring, and say that at
  grading.
- **Skipping ahead**: the user may ask for the next part before answering the
  current one. Note which questions are still open and list them before
  submission.

## 5. Grade after submission

1. **Score**: `34 / 45 (76%)`, plus the elapsed time if timed. Databricks
   doesn't publish the passing score in the exam guide, so don't state or
   invent a pass/fail line.
2. **Section breakdown**: a table with section, questions, correct and
   percentage. Sort by percentage, weakest first.
3. **Results table**: question number, the objective (verbatim), the user's
   answer, the correct answer, ✓/✗.
4. **Explanations**, built from the answer key:
   - For each **wrong or skipped** question: why the correct option is right
     (its justification), the misconception behind the user's pick and why it
     fails (that option's verdict and justification), and the question's
     `source_url`. A `partially_correct` pick is right in part but incomplete.
     A `true_but_irrelevant` pick states something true that doesn't answer
     the question. Say which applies.
   - For each **correct** question: one line on why it's right, plus the URL.
     Keep these short. The detail goes to the misses.
   - If the sanity check flagged a bank answer as doubtful, say so here and
     give the bank id.
5. **Weak objectives**: list each missed objective verbatim, and point to the
   matching course page (`grep -ril "<topic>" docs/source`, then link the page
   you find). Say so if there isn't one.
6. **Next steps** from the AI Prep Guide
   (`resources/ai-prep-guide-any-databricks-certification.pdf`):
   - Deep dive: "Teach me [OBJECTIVE, verbatim], using only official Databricks
     documentation…"
   - Repair: "Here are the questions I got wrong: … For each: explain my
     misconception, explain why the right answer is right, and give me a
     related question that tests the same concept differently."
   - A targeted quiz on the weakest section with the `certification-quiz`
     skill, e.g. "Quiz me with 10 questions on Section 4."

Offer a fresh mock exam later. Run the picker again with every id from this
exam in `--exclude`, so it uses new questions and a different random choice of
extra objectives.
