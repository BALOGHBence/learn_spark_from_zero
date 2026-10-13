"""
Read the question bank from ``fixtures/questions`` as :class:`Question` objects.

Typical usage::

    from project.questions import Category, load_questions

    questions = load_questions()                       # all 1000 questions
    streaming = load_questions(category=Category.STRUCTURED_STREAMING)
    joins = load_questions(objective="3.5")
"""

from collections import Counter, defaultdict
from collections.abc import Iterable
from pathlib import Path

import yaml
from pydantic import TypeAdapter

from project.questions.schema import Category, Question

#: ``fixtures/questions`` in the repository checkout.
DEFAULT_QUESTIONS_DIR = Path(__file__).resolve().parents[3] / "fixtures" / "questions"

_QUESTION_LIST = TypeAdapter(list[Question])


class DuplicateQuestionIdError(ValueError):
    """Raised when two questions in the bank share the same id."""


def load_question_file(path: str | Path) -> list[Question]:
    """Load and validate one YAML file holding a list of questions."""
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return _QUESTION_LIST.validate_python(data)


def load_questions(
    directory: str | Path | None = None,
    *,
    category: Category | str | None = None,
    objective: str | None = None,
) -> list[Question]:
    """Load every ``*.yaml`` file under *directory*, sorted by question id.

    Parameters
    ----------
    directory:
        Root of the question bank. Defaults to :data:`DEFAULT_QUESTIONS_DIR`.
    category:
        Only return questions of this exam section.
    objective:
        Only return questions of this objective id, e.g. ``"3.5"``.

    Raises
    ------
    FileNotFoundError
        When *directory* does not exist.
    DuplicateQuestionIdError
        When two questions share an id.
    pydantic.ValidationError
        When a question does not match the schema.
    """
    root = Path(directory) if directory is not None else DEFAULT_QUESTIONS_DIR
    if not root.is_dir():
        raise FileNotFoundError(f"Question directory not found: {root}")

    questions = [
        question
        for path in sorted(root.rglob("*.yaml"))
        for question in load_question_file(path)
    ]
    _check_unique_ids(questions)

    if category is not None:
        questions = [q for q in questions if q.category == Category(category)]
    if objective is not None:
        questions = [q for q in questions if q.objective == objective]
    return sorted(questions, key=_sort_key)


def group_by_category(questions: Iterable[Question]) -> dict[Category, list[Question]]:
    """Group questions by exam section, in exam guide order."""
    groups: dict[Category, list[Question]] = defaultdict(list)
    for question in questions:
        groups[question.category].append(question)
    return {category: groups[category] for category in Category if category in groups}


def group_by_objective(questions: Iterable[Question]) -> dict[str, list[Question]]:
    """Group questions by objective id, in exam guide order."""
    groups: dict[str, list[Question]] = defaultdict(list)
    for question in questions:
        groups[question.objective].append(question)
    return {key: groups[key] for key in sorted(groups, key=_objective_key)}


def _check_unique_ids(questions: Iterable[Question]) -> None:
    duplicates = [i for i, n in Counter(q.id for q in questions).items() if n > 1]
    if duplicates:
        raise DuplicateQuestionIdError(f"Duplicate question ids: {sorted(duplicates)}")


def _objective_key(objective: str) -> tuple[int, ...]:
    return tuple(int(part) for part in objective.split("."))


def _sort_key(question: Question) -> tuple[tuple[int, ...], str]:
    return _objective_key(question.objective), question.id
