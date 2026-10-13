# Quizzing Yourself with Claude Code

Reading the course pages is only half of exam preparation. The other half is
finding out what you *don't* know yet. This repository ships a
[Claude Code](https://claude.com/claude-code) skill, `certification-quiz`, that
turns Claude into an exam-style quiz master for the
**Databricks Certified Associate Developer for Apache Spark** exam.

The skill follows the "Diagnose" step of the Databricks AI Prep Guide (a copy is
in `resources/ai-prep-guide-any-databricks-certification.pdf`): before studying a
section in depth, take a short quiz on it, then spend your time on the
objectives you missed.

## What the Skill Does

The skill lives in `.claude/skills/certification-quiz/` and loads automatically
whenever you ask Claude Code, from inside this repository, to quiz or test you.
Two rules apply on every quiz, whether or not you say them in your prompt:

- **Questions are always in the style of the real exam.** Each question names
  the exam objective it targets, word for word from the exam guide, sets up a
  short scenario, and offers four options (A–D) with exactly one correct
  answer. Code is written in PySpark, as on the exam.
- **Answers stay hidden until you respond.** Claude shows the questions and
  stops. You don't see an answer key, a highlighted option, or a hint until you
  submit your answers.

Once you answer, Claude grades the quiz. You get a score, a table of right and
wrong answers, an explanation of each question with a link to the
docs.databricks.com page that backs it up, the objectives you missed, and
follow-up prompts for studying them.

Questions are mapped to the exam outline in
`resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`.
If you ask about a topic the outline doesn't cover, Claude tells you so rather
than presenting it as an exam objective.

:::{admonition} Note: AI-Generated Questions Are Not a Readiness Score
:class: note

The questions are written by an AI model. They aren't official exam items and
they aren't calibrated against the real exam's difficulty. Use them to find
weak spots, and confirm anything that surprises you in the
[Databricks documentation](https://docs.databricks.com).
:::

## Example Prompts

Open Claude Code at the root of this repository and type any of the prompts
below. `[SECTION]` can be a section number, a section name, a single objective,
or a topic.

**Diagnose a whole exam section** (the prompt from the AI Prep Guide):

```text
Quiz me with 10 multiple-choice questions on Section 5: Structured Streaming, in the style of an actual Databricks certification exam. Don't show answers until I respond.
```

**The short form works the same way.** The exam style and hidden answers are
applied anyway:

```text
Quiz me on Section 2.
```

```text
Give me 5 questions on Using Spark Connect to deploy applications.
```

**Drill a single objective** you got wrong last time:

```text
Quiz me with 8 questions on "Combine DataFrames with operations such as Inner join, left join, broadcast join, multiple keys, cross join, union, and union all."
```

**Quiz by topic.** Claude finds the matching objective(s):

```text
Test me on watermarks and streaming deduplication.
```

```text
Quiz me on Adaptive Query Execution and data skew.
```

**One question at a time**, graded as you go:

```text
Quiz me on Section 3, one question at a time.
```

**A full mock exam**, 45 questions across all seven sections like the real
exam, is handled by a separate skill. See
{doc}`Taking a Mock Exam with Claude Code <03_taking_a_mock_exam_with_claude_code>`.

## Answering and Getting Feedback

When the questions appear, reply with your choices in any readable form:

```text
1-B, 2-D, 3-A, 4-C, 5-B, 6-A, 7-D, 8-C, 9-B, 10-A
```

You can also:

- **Ask for a hint** on a question ("hint for 4"). The hint narrows down the
  concept without giving the answer away.
- **Reveal a single answer** ("just tell me the answer to 7"). Only that
  question is revealed; the rest stay hidden.
- **Stop early** ("I'm done"). Questions you didn't answer are marked as
  skipped.

After grading, go through each missed objective with the "Deep dive" and
"Repair" prompts that Claude suggests. Then ask for a new quiz that covers only
those objectives:

```text
Quiz me again, only on the objectives I missed.
```
