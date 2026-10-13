import {
  EXAM_TITLE,
  LETTERS,
  SECTIONS,
  correctIndex,
  objectiveText,
  sectionOf,
} from "./exam.js";

// Wrong and unanswered questions, with everything the bank knows about them.
export function wrongAnswers(questions, responses) {
  return questions
    .map((q, i) => ({ q, number: i + 1, selected: responses[i] }))
    .filter(({ q, selected }) => selected !== correctIndex(q))
    .map(({ q, number, selected }) => ({
      number,
      id: q.id,
      section: `${sectionOf(q.objective)}: ${SECTIONS[sectionOf(q.objective)].title}`,
      objective: `${q.objective} ${objectiveText(q.objective)}`,
      question: q.question,
      options: q.answers.map((a, j) => ({
        letter: LETTERS[j],
        text: a.text,
        verdict: a.verdict,
        justification: a.justification,
      })),
      your_answer: selected == null ? null : LETTERS[selected],
      correct_answer: LETTERS[correctIndex(q)],
      source_url: q.source_url,
    }));
}

export function toJson(questions, responses, score) {
  return JSON.stringify(
    {
      exam: EXAM_TITLE,
      taken_at: new Date().toISOString(),
      score: { correct: score, total: questions.length },
      wrong_answers: wrongAnswers(questions, responses),
    },
    null,
    2,
  );
}

const INSTRUCTIONS = `You are my study tutor for the ${EXAM_TITLE} exam. I just took a practice exam and below are the questions I got wrong or left unanswered.

Rules:
- Ground every explanation in official sources only: docs.databricks.com, Databricks Academy, and spark.apache.org for open-source Apache Spark behaviour. Do not rely on third-party blogs, tutorials or forum posts.
- Cite the documentation page URL for each key claim. Each question includes a source URL from the question bank. Start there.
- Use only current Databricks product names and behaviours, and do not invent exam objectives. The objectives below are quoted verbatim from the official exam guide.
- If you cannot confirm a claim in the official documentation, or cannot browse, say so explicitly instead of guessing, and tell me where in the docs I should verify it.
- The practice questions were written by an AI model and are not official exam items. If you believe an answer key is wrong, say so and explain why with a citation.

For each question:
1. Explain the misconception behind my answer (or, if I left it blank, what I needed to know).
2. Explain why the correct answer is right, citing the documentation.
3. Give me one new multiple-choice question that tests the same concept differently. Do not reveal its answer until I reply.

When you have gone through all questions, summarise the objectives I should study again, weakest first.`;

export function toPrompt(questions, responses, score) {
  const wrong = wrongAnswers(questions, responses);
  const blocks = wrong.map((w, i) => {
    const options = w.options.map((o) => `${o.letter}. ${o.text}`).join("\n\n");
    const notes = w.options
      .map((o) => `- ${o.letter} (${o.verdict}): ${o.justification}`)
      .join("\n");
    return [
      `## Question ${i + 1} (exam question ${w.number}, bank id ${w.id})`,
      `Section: ${w.section}`,
      `Objective: ${w.objective}`,
      "",
      w.question,
      "",
      options,
      "",
      `My answer: ${w.your_answer ?? "not answered"}`,
      `Correct answer: ${w.correct_answer}`,
      "",
      "Question bank notes:",
      notes,
      "",
      `Source: ${w.source_url}`,
    ].join("\n");
  });

  return [
    INSTRUCTIONS,
    "",
    `My score: ${score} / ${questions.length}. Questions to review: ${wrong.length}.`,
    "",
    ...blocks.flatMap((b) => [b, ""]),
  ].join("\n");
}

export function download(filename, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
