"""
Pick exam questions from the question bank in ``fixtures/questions``.

Used by the ``certification-quiz`` and ``mock-exam`` skills. Run it from the
repository root with the project environment::

    uv run python .claude/skills/certification-quiz/scripts/pick_questions.py --section 3
    uv run python .claude/skills/certification-quiz/scripts/pick_questions.py --objective 3.5 --count 5
    uv run python .claude/skills/certification-quiz/scripts/pick_questions.py --objective 5.3 --grep watermark
    uv run python .claude/skills/certification-quiz/scripts/pick_questions.py --mock

The output has two parts: the questions, ready to show the user with options
labelled A-D, and an answer key with every option's verdict, justification
and the source URL. The answer key is for grading only and must never be shown
to the user before they answer.

Options are shuffled so that the correct letters are spread evenly over A-D
with no run of three or more of the same letter.
"""

import argparse
import random
import sys
from collections.abc import Sequence

from project.questions import OBJECTIVES, Category, Question, load_questions

LETTERS = "ABCD"

#: Questions per section in a mock exam: the official section weights on the
#: certification page (20/20/30/10/10/5/5%) applied to 45 questions; see the
#: mock-exam skill for how the table is derived.
MOCK_BLUEPRINT: dict[int, int] = {1: 9, 2: 9, 3: 14, 4: 5, 5: 4, 6: 2, 7: 2}


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    rng = random.Random(args.seed)
    bank = [q for q in load_questions() if q.id not in set(args.exclude)]

    if args.mock:
        picked = _pick_mock(bank, rng)
        rng.shuffle(picked)
    else:
        objectives = _resolve_objectives(args.section, args.objective)
        pool = [q for q in bank if q.objective in objectives]
        if args.grep:
            pool = [q for q in pool if _matches(q, args.grep)]
        picked = _spread(pool, sorted(objectives, key=_objective_key), args.count, rng)
        if len(picked) < args.count:
            print(
                f"WARNING: only {len(picked)} matching questions in the bank "
                f"(asked for {args.count}).",
                file=sys.stderr,
            )

    letters = _balanced_letters(len(picked), rng)
    print(_render(picked, letters, rng, show_objective=not args.mock))
    return 0


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    scope = parser.add_argument_group("scope (combine --section/--objective freely)")
    scope.add_argument("--section", type=int, action="append", default=[],
                       help="exam section number, 1-7 (repeatable)")
    scope.add_argument("--objective", action="append", default=[],
                       help='objective id such as "3.5" (repeatable)')
    scope.add_argument("--mock", action="store_true",
                       help="pick a full 45-question mock exam by the blueprint")
    parser.add_argument("--count", type=int, default=10,
                        help="number of questions (ignored with --mock; default 10)")
    parser.add_argument("--grep", action="append", default=[],
                        help="keep questions whose stem or options contain this text, "
                             "case-insensitive (repeatable, any match)")
    parser.add_argument("--exclude", action="append", default=[],
                        help="question id to leave out, e.g. one already asked (repeatable)")
    parser.add_argument("--seed", type=int, help="random seed, for reproducible picks")
    args = parser.parse_args(argv)
    if args.mock and (args.section or args.objective or args.grep):
        parser.error("--mock picks from the whole outline; drop --section/--objective/--grep")
    if not args.mock and not (args.section or args.objective):
        args.section = [category.section for category in Category]
    return args


def _resolve_objectives(sections: list[int], objectives: list[str]) -> set[str]:
    unknown = [o for o in objectives if o not in OBJECTIVES]
    if unknown:
        sys.exit(f"Unknown objective(s): {unknown}. Valid ids: {sorted(OBJECTIVES, key=_objective_key)}")
    bad_sections = [s for s in sections if s not in MOCK_BLUEPRINT]
    if bad_sections:
        sys.exit(f"Unknown section(s): {bad_sections}. Valid sections: 1-7")
    return set(objectives) | {o.id for o in OBJECTIVES.values() if o.category.section in sections}


def _matches(question: Question, needles: list[str]) -> bool:
    haystack = " ".join([question.question, *(a.text for a in question.answers)]).lower()
    return any(needle.lower() in haystack for needle in needles)


def _spread(pool: list[Question], objectives: list[str], count: int,
            rng: random.Random) -> list[Question]:
    """Pick *count* questions, round-robin over *objectives* so they stay even."""
    by_objective = {o: [q for q in pool if q.objective == o] for o in objectives}
    for questions in by_objective.values():
        rng.shuffle(questions)
    order = [o for o in objectives if by_objective[o]]
    rng.shuffle(order)
    picked: list[Question] = []
    while len(picked) < count and order:
        for objective in list(order):
            if len(picked) == count:
                break
            picked.append(by_objective[objective].pop())
            if not by_objective[objective]:
                order.remove(objective)
    return sorted(picked, key=lambda q: (_objective_key(q.objective), q.id))


def _pick_mock(bank: list[Question], rng: random.Random) -> list[Question]:
    """One question per objective, extras dealt out over the objectives at random.

    The extras go to the section's objectives one at a time in a random order,
    so they land on different objectives before any objective gets a third.
    """
    picked: list[Question] = []
    for section, total in MOCK_BLUEPRINT.items():
        objectives = [o.id for o in OBJECTIVES.values() if o.category.section == section]
        counts = dict.fromkeys(objectives, 1)
        order = rng.sample(objectives, len(objectives))
        for i in range(total - len(objectives)):
            counts[order[i % len(objectives)]] += 1
        for objective in objectives:
            pool = [q for q in bank if q.objective == objective]
            n = counts[objective]
            if len(pool) < n:
                sys.exit(f"Not enough questions left for objective {objective}.")
            picked.extend(rng.sample(pool, n))
    return picked


def _balanced_letters(n: int, rng: random.Random) -> list[str]:
    """Correct letters spread evenly over A-D, with no run of three."""
    base = [LETTERS[i % 4] for i in range(n)]
    for _ in range(10_000):
        rng.shuffle(base)
        if all(not (base[i] == base[i - 1] == base[i - 2]) for i in range(2, n)):
            return base
    return base


def _render(questions: list[Question], letters: list[str], rng: random.Random,
            show_objective: bool) -> str:
    shown: list[str] = []
    key: list[str] = []
    for number, (question, letter) in enumerate(zip(questions, letters, strict=True), 1):
        wrong = [a for a in question.answers if not a.is_correct]
        rng.shuffle(wrong)
        options = wrong[:]
        options.insert(LETTERS.index(letter), question.correct_answer)

        block = [f"### Question {number}", ""]
        if show_objective:
            block += [f"*Objective: {question.objective_text}*", ""]
        block += [question.question, ""]
        for opt_letter, answer in zip(LETTERS, options, strict=True):
            block.append(_option(opt_letter, answer.text))
        shown.append("\n".join(block))

        lines = [
            f"Q{number} [{question.id}] objective {question.objective} "
            f"(Section {question.category.section}) -> correct: {letter}",
            f"  objective text: {question.objective_text}",
        ]
        for opt_letter, answer in zip(LETTERS, options, strict=True):
            lines.append(f"  {opt_letter} ({answer.verdict.value}): {answer.justification}")
        lines.append(f"  source: {question.source_url}")
        key.append("\n".join(lines))

    return "\n".join([
        "=" * 30 + " QUESTIONS (show to the user) " + "=" * 30,
        "",
        "\n\n".join(shown),
        "",
        "=" * 30 + " ANSWER KEY (never show before grading) " + "=" * 30,
        "",
        "\n\n".join(key),
    ])


def _option(letter: str, text: str) -> str:
    if "\n" in text:
        indented = "\n".join(f"   {line}" if line else "" for line in text.splitlines())
        return f"**{letter}.**\n\n{indented}\n"
    return f"**{letter}.** {text}\n"


def _objective_key(objective: str) -> tuple[int, ...]:
    return tuple(int(part) for part in objective.split("."))


if __name__ == "__main__":
    sys.exit(main())
