"""Chapter 6 - Approaching Without Arriving (limits and continuity)."""

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
                template,
                inst,
                label="limit",
                instruction="Evaluate the limit. Exact answers only.",
            )
            for template, inst in by_template(pairs, ids, limit)
        )

    def choices(ids: set[str], instruction: str, limit: int = MAX_CHOICE) -> tuple:
        return tuple(
            choice_problem(template, inst, instruction=instruction)
            for template, inst in by_template(pairs, ids, limit)
        )

    return Chapter(
        id="ch06-approaching",
        number=6,
        act=2,
        name="Approaching Without Arriving",
        tag="limits",
        subtitle="Short on purpose. Get the intuition and the mechanics, then move on.",
        requires=("ch05-circles",),
        gate=(
            "Evaluate lim(x→0) sin(x)/x and lim(x→∞) (3x²+x)/(2x²−5), and "
            "explain why each technique applies."
        ),
        levels=(
            Level(
                id="ch06-l1-concept",
                type="concept",
                title="Near, not at",
                blurb=(
                    "The shortest concept card in Act II, deliberately. Limits "
                    "are where beginners get stuck for a month and quit."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch06-l2-indeterminate",
                type="solve",
                title="When substitution fails",
                blurb=(
                    "0/0 is a question, not an answer. Factor, cancel, then "
                    "substitute."
                ),
                problems=solves({"aw-removable", "aw-infinity"}),
            ),
            Level(
                id="ch06-l3-sinc",
                type="solve",
                title="The one limit calculus needs",
                blurb=(
                    "sin(x)/x → 1, rescaled. This is the fact that makes "
                    "d/dx sin x = cos x come out clean."
                ),
                problems=solves({"aw-sinc"}, limit=6),
            ),
            Level(
                id="ch06-l4-existence",
                type="choice",
                title="Does it even exist?",
                blurb=(
                    "Check both sides. A two-sided limit exists only when the "
                    "one-sided limits agree."
                ),
                problems=choices({"aw-one-sided"}, "What is this limit?"),
            ),
            Level(
                id="ch06-l5-continuity",
                type="choice",
                title="Three conditions",
                blurb=(
                    "The limit exists, the value exists, and they match. Each "
                    "can fail on its own - including the third, which people "
                    "forget is possible."
                ),
                problems=choices({"aw-continuity"}, "Is f continuous there?"),
            ),
        ),
    )


__all__ = ["build"]
