"""Chapter 13 - The Bridge (the Fundamental Theorem of Calculus)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SOLVE, by_template, validated
from mathcoach.generator import choice_problem, solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    definite = tuple(
        solve_problem(
            template, inst, label="value", instruction="Evaluate. Exact answer."
        )
        for template, inst in by_template(pairs, {"br-definite"}, MAX_SOLVE)
    )
    statement = tuple(
        choice_problem(template, inst, instruction="Which is it?")
        for template, inst in by_template(pairs, {"br-statement"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch13-bridge",
        number=13,
        act=3,
        name="The Bridge",
        tag="the FTC",
        subtitle="Slopes and areas are inverse operations - which is not obvious at all.",
        requires=("ch12-backwards",),
        gate=(
            "State both parts of the FTC in your own words, and explain why "
            "differentiation and integration are inverse operations."
        ),
        levels=(
            Level(
                id="ch13-l1-concept",
                type="concept",
                title="Two questions, one answer",
                blurb=(
                    "There is no reason slopes and areas should be related. They "
                    "are, and it took centuries to notice."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch13-l2-statement",
                type="choice",
                title="What the theorem says",
                blurb="The chapter gate. Both halves.",
                problems=statement,
            ),
            Level(
                id="ch13-l3-evaluate",
                type="solve",
                title="Top minus bottom",
                blurb=(
                    "Find one antiderivative, evaluate at both ends, subtract. "
                    "No + C - it cancels."
                ),
                problems=definite,
            ),
        ),
    )


__all__ = ["build"]
