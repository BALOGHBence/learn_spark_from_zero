# Taking a Mock Exam with Claude Code

{doc}`Quizzing Yourself with Claude Code <02_quizzing_yourself_with_claude_code>`
covers short quizzes on one section or topic. Use those while you study. Once
you've worked through the course, find out how you do on the whole exam in one
sitting. This repository ships a second [Claude Code](https://claude.com/claude-code)
skill for that, `mock-exam`. It runs a full-length practice version of the
**Databricks Certified Associate Developer for Apache Spark** exam.

## What the Skill Does

The skill lives in `.claude/skills/mock-exam/` and loads automatically whenever
you ask Claude Code, from inside this repository, for a mock exam, practice
exam or full exam. Two rules apply on every run, whether or not you say them in
your prompt:

- **Same length as the real exam, covering every objective.** The exam has
  45 scored multiple-choice questions and a 90-minute time limit
  ([Databricks Certified Associate Developer for Apache Spark](https://www.databricks.com/learn/certification/apache-spark-developer-associate)),
  so the mock exam has 45 questions. Every objective in the exam guide in
  `resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`
  gets at least one question.
- **No answers until you submit everything.** Claude doesn't show an answer
  key, a score, a hint or any feedback on your answers until you've submitted
  all 45.

The questions are written the same way as in the quiz skill: a short scenario,
four options (A–D), exactly one correct answer, and code in PySpark. Unlike the
quiz, the mock exam mixes the sections together and doesn't show which
objective each question targets, because that would give away part of the
answer. You see the objectives when your exam is graded.

### How the Questions Are Spread Across Sections

The certification page publishes a weight for each section
([Databricks Certified Associate Developer for Apache Spark](https://www.databricks.com/learn/certification/apache-spark-developer-associate)).
The skill currently doesn't use those weights: it gives every objective in the
exam guide an equal share of the 45 questions instead. The two allocations
compare as follows:

| Section | Official weight | Questions at that weight | Objectives | Skill's questions |
| --- | ---: | ---: | ---: | ---: |
| 1: Apache Spark Architecture and Components | 20% | 9 | 7 | 10 |
| 2: Using Spark SQL | 20% | 9 | 4 | 6 |
| 3: Developing Apache Spark™ DataFrame/DataSet API Applications | 30% | 13.5 | 10 | 14 |
| 4: Troubleshooting and Tuning Apache Spark DataFrame API Applications | 10% | 4.5 | 3 | 4 |
| 5: Structured Streaming | 10% | 4.5 | 4 | 5 |
| 6: Using Spark Connect to deploy applications | 5% | 2.25 | 2 | 3 |
| 7: Using Pandas API on Apache Spark | 5% | 2.25 | 2 | 3 |
| **Total** | **100%** | **45** | **32** | **45** |

The biggest difference is Section 2, Spark SQL, which the skill under-samples
compared with its official 20%. Within a section, a few objectives get a
second question. Which ones changes at random on each run, so two mock exams
don't cover exactly the same ground.

:::{admonition} Note: AI-Generated Questions Are Not a Readiness Score
:class: note

The questions are written by an AI model. They aren't official exam items and
they aren't calibrated against the real exam's difficulty. Treat your score
as a guide to where you're weak, not as a prediction of whether you'll pass.
The certification page doesn't state a passing score.
:::

## Example Prompts

Open Claude Code at the root of this repository and type any of the prompts
below.

**Start a mock exam:**

```text
Give me a full mock exam.
```

The full form of the prompt does the same thing. The skill applies the
question count and hidden answers either way:

```text
Generate a full mock exam with the number of scored questions in the exam guide, spread across all objectives. Don't reveal answers until I submit all responses.
```

**Time yourself.** Claude notes the time when the exam starts and reports how
long you took when you submit. It doesn't stop you at 90 minutes:

```text
Give me a timed mock exam.
```

**Take a fresh exam later.** Each run writes new questions:

```text
Give me another mock exam with new questions.
```

## Answering and Submitting

Claude preparing 45 questions and checking each answer against the Databricks
documentation takes a few minutes. The exam then arrives in three parts of 15
questions. Answer each part to get the next one:

```text
1-B, 2-D, 3-A, 4-C, 5-B, 6-A, 7-D, 8-C, 9-B, 10-A, 11-C, 12-D, 13-A, 14-B, 15-C
```

Claude only confirms how many answers it has recorded. It doesn't tell you
whether any of them are right. While the exam is open you can:

- **Change an answer** ("change 7 to C").
- **Ask about the wording** of a question that seems unclear. Claude clarifies
  the wording but doesn't hint at the answer.
- **End the exam early** ("end the exam and grade it"). Unanswered questions
  count as wrong.

Hints and single answers aren't available during a mock exam, unlike in the
quiz. If you ask for one, Claude offers to carry on or to end the exam.

After Part 3, Claude lists any questions you haven't answered. Reply `submit`
to get graded.

## Reading Your Results

The graded exam contains:

- your overall score, and the time you took if the exam was timed;
- a score for each section, weakest first;
- a table of every question with its objective, your answer and the correct
  answer;
- for each question you missed, why the correct option is right, what was
  wrong with yours, and a link to the docs.databricks.com page that confirms
  it (questions you got right get one line each);
- the objectives you missed, with links to the course pages that teach them;
- follow-up prompts for studying those objectives.

Then go back to {doc}`short quizzes <02_quizzing_yourself_with_claude_code>`
on your weakest section, for example:

```text
Quiz me with 10 questions on Section 4.
```

Once your section scores improve, take a fresh mock exam.
