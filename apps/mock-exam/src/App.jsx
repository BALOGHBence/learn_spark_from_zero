import { useEffect, useState } from "react";
import Markdown from "react-markdown";
import {
  EXAM_TITLE,
  LETTERS,
  QUESTION_COUNT,
  SECTIONS,
  TIME_LIMIT_MINUTES,
  correctIndex,
  createExam,
  objectiveText,
  sectionOf,
} from "./exam.js";
import { download, toJson, toPrompt } from "./export.js";

const STORAGE_KEY = "spark-mock-exam";

// An exam in progress survives a page reload. Browser storage can be missing or
// blocked, in which case the app just doesn't remember the exam.
function loadSaved() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
}

function save(state) {
  try {
    if (state) localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    else localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore: the exam still works, it just won't survive a reload.
  }
}

export default function App() {
  const [exam, setExam] = useState(loadSaved);

  useEffect(() => save(exam), [exam]);

  const start = () =>
    setExam({
      questions: createExam(),
      responses: Array(QUESTION_COUNT).fill(null),
      marked: [],
      current: 0,
      view: "question",
      startedAt: Date.now(),
      submittedAt: null,
    });

  const update = (changes) => setExam((e) => ({ ...e, ...changes }));

  if (!exam) return <Start onStart={start} />;
  if (exam.submittedAt) return <Results exam={exam} onRestart={() => setExam(null)} />;
  return <Exam exam={exam} update={update} />;
}

function Start({ onStart }) {
  return (
    <main className="start">
      <h1>Mock exam</h1>
      <p className="subtitle">{EXAM_TITLE}</p>
      <ul>
        <li>
          {QUESTION_COUNT} multiple-choice questions, suggested time {TIME_LIMIT_MINUTES} minutes.
        </li>
        <li>Questions are drawn from the course question bank, covering every exam objective.</li>
        <li>Mark questions you're unsure about and come back to them before you submit.</li>
        <li>You can change any answer until you submit. Results are shown only after submission.</li>
      </ul>
      <button className="primary" onClick={onStart}>
        Start exam
      </button>
    </main>
  );
}

function Timer({ startedAt }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, []);
  const left = Math.round((startedAt + TIME_LIMIT_MINUTES * 60_000 - now) / 1000);
  return (
    <span className={left < 0 ? "timer over" : "timer"}>
      {left < 0 ? "Over time " : "Time left "}
      {formatDuration(Math.abs(left))}
    </span>
  );
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}

function Exam({ exam, update }) {
  const { questions, responses, marked, current, view } = exam;
  const answered = responses.filter((r) => r !== null).length;

  const goTo = (index) => update({ current: index, view: "question" });
  const toggleMark = (index) =>
    update({
      marked: marked.includes(index) ? marked.filter((m) => m !== index) : [...marked, index],
    });
  const answer = (choice) =>
    update({ responses: responses.map((r, i) => (i === current ? choice : r)) });
  const submit = () => {
    const unanswered = QUESTION_COUNT - answered;
    const warnings = [
      unanswered && `${unanswered} unanswered`,
      marked.length && `${marked.length} marked for review`,
    ].filter(Boolean);
    const message = warnings.length
      ? `You have ${warnings.join(" and ")}. Submit anyway?`
      : "Submit the exam? You can't change your answers afterwards.";
    if (window.confirm(message)) update({ submittedAt: Date.now() });
  };

  return (
    <div className="exam">
      <header>
        <strong>Mock exam</strong>
        <span>
          {answered} / {QUESTION_COUNT} answered · {marked.length} marked
        </span>
        <Timer startedAt={exam.startedAt} />
        <button onClick={() => update({ view: view === "review" ? "question" : "review" })}>
          {view === "review" ? "Back to question" : "Review all"}
        </button>
        <button className="primary" onClick={submit}>
          Submit exam
        </button>
      </header>

      <Navigator exam={exam} goTo={goTo} />

      {view === "review" ? (
        <Review exam={exam} goTo={goTo} />
      ) : (
        <main className="question">
          <div className="question-head">
            <h2>
              Question {current + 1} of {QUESTION_COUNT}
            </h2>
            <label className="mark">
              <input
                type="checkbox"
                checked={marked.includes(current)}
                onChange={() => toggleMark(current)}
              />
              Mark for review
            </label>
          </div>
          <Markdown>{questions[current].question}</Markdown>
          <div className="options">
            {questions[current].answers.map((a, i) => (
              <button
                key={i}
                className={responses[current] === i ? "option selected" : "option"}
                onClick={() => answer(responses[current] === i ? null : i)}
              >
                <span className="letter">{LETTERS[i]}</span>
                <div className="option-text">
                  <Markdown>{a.text}</Markdown>
                </div>
              </button>
            ))}
          </div>
          <nav className="pager">
            <button disabled={current === 0} onClick={() => goTo(current - 1)}>
              ← Previous
            </button>
            <button disabled={current === QUESTION_COUNT - 1} onClick={() => goTo(current + 1)}>
              Next →
            </button>
          </nav>
        </main>
      )}
    </div>
  );
}

function Navigator({ exam, goTo }) {
  const { responses, marked, current, view } = exam;
  return (
    <nav className="navigator" aria-label="Questions">
      {responses.map((r, i) => {
        const classes = ["cell"];
        if (r !== null) classes.push("answered");
        if (marked.includes(i)) classes.push("marked");
        if (i === current && view === "question") classes.push("current");
        return (
          <button key={i} className={classes.join(" ")} onClick={() => goTo(i)}>
            {i + 1}
          </button>
        );
      })}
      <p className="legend">
        <span className="cell answered" /> answered <span className="cell marked" /> marked
      </p>
    </nav>
  );
}

function Review({ exam, goTo }) {
  const { questions, responses, marked } = exam;
  const [filter, setFilter] = useState(marked.length ? "marked" : "all");
  const shown = questions
    .map((q, i) => ({ q, i }))
    .filter(({ i }) => {
      if (filter === "marked") return marked.includes(i);
      if (filter === "unanswered") return responses[i] === null;
      return true;
    });

  return (
    <main className="review">
      <h2>Review</h2>
      <div className="filters">
        {[
          ["marked", `Marked (${marked.length})`],
          ["unanswered", `Unanswered (${responses.filter((r) => r === null).length})`],
          ["all", `All (${QUESTION_COUNT})`],
        ].map(([key, label]) => (
          <button
            key={key}
            className={filter === key ? "selected" : ""}
            onClick={() => setFilter(key)}
          >
            {label}
          </button>
        ))}
      </div>
      {shown.length === 0 && <p className="muted">No questions here.</p>}
      <ul className="review-list">
        {shown.map(({ q, i }) => (
          <li key={q.id}>
            <button onClick={() => goTo(i)}>
              <span className="number">{i + 1}</span>
              <span className="preview">{firstLine(q.question)}</span>
              <span className="status">
                {marked.includes(i) && <span className="badge marked">Marked</span>}
                {responses[i] === null ? (
                  <span className="badge">Unanswered</span>
                ) : (
                  <span className="badge answered">{LETTERS[responses[i]]}</span>
                )}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}

function firstLine(markdown) {
  return markdown.split("\n").find((line) => line.trim()).replaceAll("`", "");
}

function Results({ exam, onRestart }) {
  const { questions, responses, startedAt, submittedAt } = exam;
  const [onlyWrong, setOnlyWrong] = useState(false);
  const [copied, setCopied] = useState(false);
  const isCorrect = (i) => responses[i] === correctIndex(questions[i]);
  const score = questions.filter((_, i) => isCorrect(i)).length;
  const minutes = Math.round((submittedAt - startedAt) / 60_000);

  const sections = Object.entries(SECTIONS)
    .map(([number, { title }]) => {
      const indexes = questions
        .map((q, i) => i)
        .filter((i) => sectionOf(questions[i].objective) === Number(number));
      const correct = indexes.filter(isCorrect).length;
      return { number, title, total: indexes.length, correct };
    })
    .sort((a, b) => a.correct / a.total - b.correct / b.total);

  const copyPrompt = async () => {
    try {
      await navigator.clipboard.writeText(toPrompt(questions, responses, score));
      setCopied(true);
    } catch {
      window.alert("Couldn't copy to the clipboard. Use Download prompt instead.");
    }
  };

  const restart = () => {
    if (window.confirm("Start a new exam? These results will be cleared.")) onRestart();
  };

  return (
    <main className="results">
      <h1>
        Score: {score} / {questions.length} ({Math.round((100 * score) / questions.length)}%)
      </h1>
      <p className="muted">
        Time taken: {minutes} minutes (suggested {TIME_LIMIT_MINUTES}). The exam guide doesn't publish
        a passing score, and these AI-written practice questions aren't calibrated to the real exam, so
        treat the score as a guide to your weak spots.
      </p>

      <div className="actions">
        <button className="primary" onClick={copyPrompt}>
          {copied ? "Copied!" : "Copy LLM prompt"}
        </button>
        <button
          onClick={() =>
            download("mock-exam-wrong-answers.md", toPrompt(questions, responses, score), "text/markdown")
          }
        >
          Download prompt
        </button>
        <button
          onClick={() =>
            download("mock-exam-wrong-answers.json", toJson(questions, responses, score), "application/json")
          }
        >
          Download wrong answers (JSON)
        </button>
        <button onClick={restart}>New exam</button>
      </div>

      <h2>By section (weakest first)</h2>
      <table>
        <thead>
          <tr>
            <th>Section</th>
            <th>Correct</th>
            <th>%</th>
          </tr>
        </thead>
        <tbody>
          {sections.map((s) => (
            <tr key={s.number}>
              <td>
                {s.number}. {s.title}
              </td>
              <td>
                {s.correct} / {s.total}
              </td>
              <td>{Math.round((100 * s.correct) / s.total)}%</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="question-list-head">
        <h2>Questions</h2>
        <label>
          <input type="checkbox" checked={onlyWrong} onChange={() => setOnlyWrong(!onlyWrong)} />
          Show only wrong answers
        </label>
      </div>
      {questions.map((q, i) =>
        onlyWrong && isCorrect(i) ? null : (
          <ResultCard key={q.id} number={i + 1} question={q} selected={responses[i]} />
        ),
      )}
    </main>
  );
}

function ResultCard({ number, question, selected }) {
  const correct = correctIndex(question);
  const right = selected === correct;
  return (
    <article className={right ? "result right" : "result wrong"}>
      <h3>
        {right ? "✓" : "✗"} Question {number}
        <span className="muted">
          {" "}
          · Objective {question.objective}: {objectiveText(question.objective)}
        </span>
      </h3>
      <Markdown>{question.question}</Markdown>
      {question.answers.map((a, i) => {
        const classes = ["answer"];
        if (i === correct) classes.push("correct");
        if (i === selected && !right) classes.push("chosen");
        return (
          <div key={i} className={classes.join(" ")}>
            <div className="answer-text">
              <span className="letter">{LETTERS[i]}</span>
              <Markdown>{a.text}</Markdown>
            </div>
            <div className="justification">
              <Markdown>
                {(i === correct ? "**Correct.** " : "") +
                  (i === selected && !right ? "**Your answer.** " : "") +
                  a.justification}
              </Markdown>
            </div>
          </div>
        );
      })}
      {selected === null && <p className="muted">You didn't answer this question.</p>}
      <p>
        Source:{" "}
        <a href={question.source_url} target="_blank" rel="noreferrer">
          {question.source_url}
        </a>
      </p>
    </article>
  );
}
