from collections import Counter
from pathlib import Path

import pytest
from pydantic import ValidationError

from project.questions import (
    OBJECTIVES,
    Category,
    DuplicateQuestionIdError,
    Question,
    Verdict,
    group_by_category,
    group_by_objective,
    load_question_file,
    load_questions,
)

# Questions per section: 1000 questions spread equally over the 32 objectives
# of the exam guide, section totals rounded with the largest-remainder method.
EXPECTED_PER_CATEGORY = {
    Category.ARCHITECTURE: 219,
    Category.SPARK_SQL: 125,
    Category.DATAFRAME_API: 313,
    Category.TROUBLESHOOTING_AND_TUNING: 94,
    Category.STRUCTURED_STREAMING: 125,
    Category.SPARK_CONNECT: 62,
    Category.PANDAS_API_ON_SPARK: 62,
}


def _answer(text: str, verdict: str = "incorrect") -> dict[str, str]:
    return {"text": text, "verdict": verdict, "justification": f"Why {text}."}


def _answers(*verdicts: str) -> list[dict[str, str]]:
    texts = ["Inner", "Left", "Right", "Cross"]
    return [_answer(t, v) for t, v in zip(texts, verdicts, strict=True)]


def _question(**overrides: object) -> dict[str, object]:
    data: dict[str, object] = {
        "id": "3.5-001",
        "category": "developing_dataframe_dataset_api_applications",
        "objective": "3.5",
        "question": "Which join type is the default?",
        "answers": _answers(
            "correct", "incorrect", "partially_correct", "true_but_irrelevant"
        ),
        "source_url": "https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-join.html",
    }
    data.update(overrides)
    return data


@pytest.fixture(scope="module")
def bank() -> list[Question]:
    return load_questions()


def test_bank_has_1000_questions(bank: list[Question]) -> None:
    assert len(bank) == 1000


def test_bank_follows_blueprint(bank: list[Question]) -> None:
    assert Counter(q.category for q in bank) == EXPECTED_PER_CATEGORY


def test_every_objective_is_covered(bank: list[Question]) -> None:
    counts = Counter(q.objective for q in bank)
    assert set(counts) == set(OBJECTIVES)
    assert all(n in (31, 32) for n in counts.values())


def test_question_texts_are_unique(bank: list[Question]) -> None:
    assert len({q.question for q in bank}) == len(bank)


def test_answer_key_is_balanced(bank: list[Question]) -> None:
    counts = Counter(q.correct_index for q in bank)
    assert set(counts) == {0, 1, 2, 3}
    assert max(counts.values()) - min(counts.values()) <= 10


def test_filter_by_category_and_objective(bank: list[Question]) -> None:
    streaming = load_questions(category=Category.STRUCTURED_STREAMING)
    assert len(streaming) == 125
    assert all(q.category is Category.STRUCTURED_STREAMING for q in streaming)

    joins = load_questions(objective="3.5")
    assert joins and all(q.objective == "3.5" for q in joins)


def test_grouping(bank: list[Question]) -> None:
    by_category = group_by_category(bank)
    assert list(by_category) == list(Category)
    by_objective = group_by_objective(bank)
    assert list(by_objective)[:2] == ["1.1", "1.2"]
    assert list(by_objective)[-1] == "7.2"


def test_every_answer_is_justified(bank: list[Question]) -> None:
    for question in bank:
        assert sum(a.verdict is Verdict.CORRECT for a in question.answers) == 1
        assert all(a.justification for a in question.answers)


def test_no_stray_yaml_block_indicators(bank: list[Question]) -> None:
    # A `|` left on the first line of a `|-` block ends up in the rendered text.
    stray = [
        question.id
        for question in bank
        for text in [question.question, *(a.text for a in question.answers)]
        if text.startswith("|")
    ]
    assert stray == []


def test_question_helpers() -> None:
    question = Question.model_validate(_question())
    assert question.correct_index == 0
    assert question.correct_answer.text == "Inner"
    assert question.answers[2].verdict is Verdict.PARTIALLY_CORRECT
    assert question.is_correct("Inner")
    assert question.is_correct(0)
    assert not question.is_correct("Left")
    assert question.objective_text.startswith("Combine DataFrames")
    assert question.category.section == 3


@pytest.mark.parametrize(
    "overrides",
    [
        # no correct answer
        {"answers": _answers("incorrect", "incorrect", "incorrect", "incorrect")},
        # two correct answers
        {"answers": _answers("correct", "correct", "incorrect", "incorrect")},
        # duplicate answer texts
        {"answers": [_answer("Inner", "correct")] + [_answer("Left")] * 3},
        # only three answers
        {"answers": _answers("correct", "incorrect", "incorrect", "incorrect")[:3]},
        # unknown verdict
        {"answers": _answers("correct", "wrong", "incorrect", "incorrect")},
        # empty justification
        {
            "answers": [{"text": "Inner", "verdict": "correct", "justification": ""}]
            + _answers("correct", "incorrect", "incorrect", "incorrect")[1:]
        },
        {"objective": "9.9", "id": "9.9-001"},
        {"category": "structured_streaming"},
        {"id": "3.4-001"},
        {"source_url": "https://medium.com/some-blog-post"},
        {"explanation": "extra fields are not allowed"},
    ],
)
def test_invalid_questions_are_rejected(overrides: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Question.model_validate(_question(**overrides))


def test_duplicate_ids_are_rejected(tmp_path: Path) -> None:
    text = (
        "- id: '3.5-001'\n"
        "  category: developing_dataframe_dataset_api_applications\n"
        "  objective: '3.5'\n"
        "  question: Which join type is the default?\n"
        "  answers:\n"
        + "".join(
            f"  - {{text: {t}, verdict: {v}, justification: because}}\n"
            for t, v in [
                ("Inner", "correct"),
                ("Left", "incorrect"),
                ("Right", "incorrect"),
                ("Cross", "incorrect"),
            ]
        )
        + "  source_url: https://spark.apache.org/docs/latest/index.html\n"
    )
    (tmp_path / "a.yaml").write_text(text)
    (tmp_path / "b.yaml").write_text(text)
    assert len(load_question_file(tmp_path / "a.yaml")) == 1
    with pytest.raises(DuplicateQuestionIdError):
        load_questions(tmp_path)


def test_missing_directory_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_questions(tmp_path / "missing")
