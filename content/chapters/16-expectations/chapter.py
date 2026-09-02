"""Chapter 16 - Areas, Averages, Expectations."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SOLVE, by_template, validated
from mathcoach.generator import choice_problem, solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def solves(ids: set[str], limit: int = MAX_SOLVE) -> tuple:
        return tuple(
            solve_problem(
                template, inst, label="value", instruction="Evaluate exactly."
            )
            for template, inst in by_template(pairs, ids, limit)
        )

    why = tuple(
        choice_problem(template, inst, instruction="What does this say?")
        for template, inst in by_template(pairs, {"ae-why"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch16-expectations",
        number=16,
        act=3,
        name="Areas, Averages, Expectations",
        tag="improper integrals",
        subtitle="Where probability notation stops looking like hieroglyphics.",
        requires=("ch15-trading",),
        # Not skippable: the probability half is the AI-specific payoff of the
        # whole act and appears in no standard calculus syllabus.
        skippable=False,
        gate=(
            "Show ∫₀^∞ e^(−x) dx = 1, and explain why E[X] = ∫x·p(x)dx is a "
            "weighted average - and why a probability density must integrate "
            "to 1."
        ),
        levels=(
            Level(
                id="ch16-l1-concept",
                type="concept",
                title="Where Act III pays off",
                blurb=(
                    "Every ∫p(x)dx you will meet in a paper is this chapter."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch16-l2-improper",
                type="solve",
                title="Infinite region, finite area",
                blurb=(
                    "An improper integral is a limit. Whether it converges is a "
                    "question about how fast the tail decays."
                ),
                problems=solves({"ae-improper"}, limit=6),
            ),
            Level(
                id="ch16-l3-why",
                type="choice",
                title="Reading the notation",
                blurb=(
                    "The chapter gate, and the reason every normalising constant "
                    "in machine learning exists."
                ),
                problems=why,
            ),
            Level(
                id="ch16-l4-expectation",
                type="solve",
                title="An expectation, computed",
                blurb=(
                    "By parts inside an improper integral. This is what E[X] "
                    "actually is when you do the arithmetic."
                ),
                problems=solves({"ae-expectation"}, limit=6),
            ),
        ),
    )


__all__ = ["build"]
