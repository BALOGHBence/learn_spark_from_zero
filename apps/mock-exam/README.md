# Mock Exam App

A small React app that runs a full-length mock exam for the Databricks Certified Associate Developer for Apache Spark in your browser. It draws 45 questions from the course's question bank in [`fixtures/questions`](../../fixtures/questions), spread over the seven sections by the official section weights. It needs no Databricks connection and no Claude Code.

A hosted copy is published with the documentation at [https://baloghbence.github.io/learn_spark_from_zero/mock-exam/](https://baloghbence.github.io/learn_spark_from_zero/mock-exam/), so you can use it without installing anything. The [docs workflow](../../.github/workflows/docs.yml) builds the app on every push to `main` and serves it from the `mock-exam/` subfolder of the GitHub Pages site.

## Requirements

[Node.js](https://nodejs.org/) 20 or later, which includes `npm`. Check your version with `node --version`.

## Run It

From the root of the repository:

```shell
cd apps/mock-exam
npm install    # once
npm run dev
```

Open the URL it prints (usually http://localhost:5173/) and select **Start exam**. Stop the server with `Ctrl+C`.

The app reads the question bank when it starts, so questions added to `fixtures/questions/` show up in the next exam. To build a static copy, run `npm run build` and serve the `dist/` folder, for example with `npm run preview`.

## Using It

- **During the exam:** 45 questions and a 90-minute timer that doesn't stop you. Move freely between questions, change any answer, and mark the ones you're unsure about. **Review all** lists your marked and unanswered questions. Your answers are saved in the browser, so reloading the page doesn't lose the exam.
- **After you submit:** your score, a breakdown by section, and every question with the correct answer, an explanation for each option and a link to the supporting documentation. Nothing is revealed before you submit.
- **Exports:** **Copy LLM prompt** and **Download prompt** give you your wrong and unanswered questions as a ready-to-paste tutoring prompt for an LLM. **Download wrong answers (JSON)** saves them as structured data.

The full guide is in [Taking a Mock Exam in the Browser](../../docs/source/00_getting_started/04_taking_a_mock_exam_in_the_browser.md).

## Code Layout

| File | Purpose |
| --- | --- |
| [`src/exam.js`](src/exam.js) | Loads the question bank and builds an exam from the section blueprint |
| [`src/export.js`](src/export.js) | Builds the LLM prompt and the JSON export of wrong answers |
| [`src/App.jsx`](src/App.jsx) | The exam, review and results screens |
| [`vite.config.js`](vite.config.js) | Lets the dev server read `fixtures/questions` outside the app folder |
