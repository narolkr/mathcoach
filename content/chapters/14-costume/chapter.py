"""Chapter 14 - Change of Costume (u-substitution)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_SOLVE, by_template, validated
from mathcoach.generator import solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    indefinite = tuple(
        solve_problem(
            template,
            inst,
            label="antiderivative",
            instruction="Find the antiderivative. + C optional.",
        )
        for template, inst in by_template(pairs, {"cc-exp", "cc-log"}, MAX_SOLVE)
    )
    definite = tuple(
        solve_problem(
            template, inst, label="value", instruction="Evaluate exactly."
        )
        for template, inst in by_template(pairs, {"cc-definite"}, 6)
    )

    return Chapter(
        id="ch14-costume",
        number=14,
        act=3,
        name="Change of Costume",
        tag="substitution",
        subtitle="The chain rule read right to left. Nearly free if chapter 9 stuck.",
        requires=("ch13-bridge",),
        gate="Evaluate ∫2x·e^(x²) dx and ∫₀¹ x/(x²+1) dx.",
        levels=(
            Level(
                id="ch14-l1-concept",
                type="concept",
                title="Chapter 9, backwards",
                blurb=(
                    "Look for a function and its own derivative both present. "
                    "That's the signal."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch14-l2-substitute",
                type="solve",
                title="Spot the inner function",
                blurb=(
                    "Its derivative is already sitting there as a factor. Name "
                    "u, and the integral collapses."
                ),
                problems=indefinite,
            ),
            Level(
                id="ch14-l3-bounds",
                type="solve",
                title="With bounds",
                blurb=(
                    "Change the limits to u-values, or substitute back before "
                    "evaluating. Either works - mixing them doesn't."
                ),
                problems=definite,
            ),
        ),
    )


__all__ = ["build"]
