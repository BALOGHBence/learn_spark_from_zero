# Taking a Mock Exam in the Browser

{doc}`Taking a Mock Exam with Claude Code <03_taking_a_mock_exam_with_claude_code>` runs a mock exam in a chat. If you'd rather sit the exam in a form closer to a real testing screen, the repository also ships a small React app in `apps/mock-exam/`. It runs locally in your browser, needs no Databricks connection and no Claude Code, and draws its questions from the same question bank in `fixtures/questions/`.

## What the App Does

- **Same length as the real exam.** Each exam has 45 multiple-choice questions and a suggested time of 90 minutes, the numbers in the exam guide in `resources/databricks-certified-associate-developer-apache-spark-exam-guide-oct-2025.pdf`. A timer shows the time left, and then how far over you are, but it doesn't end the exam for you.
- **Official section weights, every objective covered.** The questions are spread over the seven sections by the section weights on the certification page ([Databricks Certified Associate Developer for Apache Spark](https://www.databricks.com/learn/certification/apache-spark-developer-associate)), rounded to 9, 9, 14, 5, 4, 2 and 2 questions, the same as the `mock-exam` skill. Within a section every objective gets at least one question, and the rest are spread over its objectives at random. {doc}`Taking a Mock Exam with Claude Code <03_taking_a_mock_exam_with_claude_code>` shows how the rounding works.
- **Mixed order, shuffled options.** Sections are mixed and the objective of each question is hidden until you submit, because it would give away part of the answer.
- **No feedback until you submit.** You see your score, the correct answers and the explanations only after you submit the whole exam.

:::{admonition} Note: AI-Generated Questions Are Not a Readiness Score
:class: note

The questions are written by an AI model. They aren't official exam items and they aren't calibrated against the real exam's difficulty. Treat your score as a guide to where you're weak, not as a prediction of whether you'll pass.
:::

## Running the App Locally

You need [Node.js](https://nodejs.org/) 20 or later, which includes `npm`. Check your version with `node --version`.

From the root of the repository, install the app's dependencies once:

```shell
cd apps/mock-exam
npm install
```

Then start the development server:

```shell
npm run dev
```

Open the URL it prints, usually `http://localhost:5173/`, and select **Start exam**. Stop the server with `Ctrl+C` when you're done.

The app reads the question bank when it starts, so questions you add to `fixtures/questions/` show up in the next exam. To build a static copy instead, run `npm run build` and serve the `dist/` folder, for example with `npm run preview`.

## Taking the Exam

- **Answer** a question by selecting an option. Select it again to clear it. Use **Previous** and **Next**, or the numbered grid on the left, to move between questions.
- **Mark for review** any question you're unsure about with the checkbox next to its number. Marked questions get a dot in the grid.
- **Review all** opens a list of questions filtered by **Marked**, **Unanswered** or **All**, with your current answer next to each one. Select a question to go back to it and change your answer.
- **Submit exam** asks for confirmation and warns you if questions are still unanswered or marked. After submitting you can't change your answers.

Your answers are saved in the browser as you go, so reloading the page doesn't lose the exam. Starting a new exam clears the previous one.

## Reading Your Results

After you submit, the app shows:

- your overall score and the time you took;
- a score for each section, weakest first;
- every question with the objective it tests, your answer, the correct answer, the question bank's explanation for each option, and a link to the documentation page that supports it. Tick **Show only wrong answers** to hide the ones you got right.

## Exporting Your Wrong Answers

The results page has three export buttons. All of them cover the questions you got wrong and the ones you left unanswered.

- **Copy LLM prompt** copies a ready-to-paste prompt to your clipboard. Paste it into a chat with an LLM such as Claude. The prompt asks the model to act as your tutor, to use only official sources (docs.databricks.com, Databricks Academy and spark.apache.org) with a link for each key claim, and to say so when it can't confirm something. For each question it asks the model to explain your misconception, explain why the correct answer is right, and give you a new question on the same concept without revealing its answer. Each question in the prompt includes its objective, the options, your answer, the correct answer, the question bank's notes and the source URL.
- **Download prompt** saves the same prompt as a Markdown file, in case copying to the clipboard isn't allowed in your browser.
- **Download wrong answers (JSON)** saves the same questions as structured data, with the bank id, section, objective, every option with its verdict and justification, your answer, the correct answer and the source URL. Use it to keep a history of your mistakes or to feed them to your own tools.

Then go back to {doc}`short quizzes <02_quizzing_yourself_with_claude_code>` on your weakest section, and take a fresh mock exam once your section scores improve. Each new exam draws a new random set of questions.
