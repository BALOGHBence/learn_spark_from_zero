---
name: mock-exam
description: Run a full-length mock exam for the Databricks Certified Associate Developer for Apache Spark — 45 exam-style multiple-choice questions, the number of scored questions in the official exam guide, spread over every objective in proportion to the outline — and reveal no answer, hint or score until the user has submitted all responses, then grade with a per-section breakdown and docs.databricks.com citations. Use whenever the user asks for a mock exam, practice exam, full exam, full-length test, exam simulation or "the whole exam", even if they don't mention the question count or hidden answers. For shorter quizzes on one section, objective or topic use certification-quiz instead.
argument-hint: "[optional: 'timed', or a different exam guide path]"
---

# Mock Exam

Simulate one sitting of the real exam: the same number of scored questions,
spread over the whole outline, with every answer withheld until the user
submits. This is the full-length counterpart of the `certification-quiz`
skill, which covers short quizzes on a section, objective or topic.

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
Read it before writing questions.

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
remaining questions go to different objectives, one extra each. **Choose which
objectives get the extra question at random on each run**, so repeated mock
exams don't all lean the same way.

Never tell the user this blueprint is Databricks' official weighting. If they
ask, explain that it's derived from the objective count because the guide
gives no weights.

**If the outline changes** (a newer guide in `resources/`, or a different
exam): take the number of scored questions from the guide and recompute the
table the same way. If the user names a different certification, ask for its
exam guide (PDF path or pasted "Sections and Objectives") instead of guessing.
If the guide does publish section percentages, use those instead and say so.

## 2. Write the questions

Follow "Writing the questions" in
[../certification-quiz/SKILL.md](../certification-quiz/SKILL.md): a short
scenario stem ending in one direct question, exactly four options A–D with
exactly one correct, plausible distractors, PySpark code in fenced blocks, at
least a third of the questions involving code, current Databricks names, and
none of the guide's ten sample questions reused.

Additionally, for a mock exam:

- **Shuffle the order** so sections are mixed, as an exam form would be. Don't
  group questions by section.
- **Don't print the objective under each question** while the exam is open.
  The objective narrows the answer, so it acts as a hint. Keep the
  question → objective mapping yourself and reveal it at grading.
- **Vary question kinds within each section**: "which code block", "what is the
  result", "why choose X over Y", "how should the engineer diagnose".
- **Balance the answer key**: each letter A–D is correct on 10–12 questions,
  with no runs of three or more of the same letter in a row.
- **No near-duplicates.** Two questions on the same objective must test
  different facts.

### Verify before presenting

Check every correct answer, and that every distractor really is wrong, against
official sources before showing anything. Use the `databricks-docs` skill's
llms.txt index if it's available, otherwise `WebSearch` with
`site:docs.databricks.com` and `WebFetch`. Batch independent searches into one
turn; one doc page often settles several questions. Exact PySpark signatures
may cite the Apache Spark API reference (`spark.apache.org/docs`). Record the
URL for each question for grading. Replace any question you can't confirm.

If you can't browse at all, say so once at the top of the exam and tell the
user that grading explanations will point to doc sections to check by hand
instead of citing verified pages.

Writing and verifying 45 questions takes a while. Tell the user up front, in
one line, that you're preparing the exam.

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

Keep the answer key only in your own working context. Don't write it to a file,
print it, or encode it anywhere the user could see before submitting. Don't
bold, reorder or otherwise mark the correct option.

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
4. **Explanations**:
   - For each **wrong or skipped** question: why the correct option is right,
     the misconception behind the user's pick and why it fails, and the doc
     URL.
   - For each **correct** question: one line on why it's right, plus the URL.
     Keep these short. The detail goes to the misses.
   - If you couldn't verify a point in official docs, say so instead of citing.
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

Offer a fresh mock exam later. It should use new questions and a different
random choice of extra objectives.
