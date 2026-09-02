"""Chapter 15 - Trading Places (integration by parts)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_SOLVE, by_template, validated
from mathcoach.generator import solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def integrals(ids: set[str], limit: int = MAX_SOLVE) -> tuple:
        return tuple(
            solve_problem(
                template,
                inst,
                label="antiderivative",
                instruction="Find the antiderivative. + C optional.",
            )
            for template, inst in by_template(pairs, ids, limit)
        )

    return Chapter(
        id="ch15-trading",
        number=15,
        act=3,
        name="Trading Places",
        tag="by parts",
        subtitle="The product rule backwards, and the last general technique here.",
        requires=("ch14-costume",),
        gate="Evaluate ∫x·ln x dx and ∫x²e^x dx.",
        levels=(
            Level(
                id="ch15-l1-concept",
                type="concept",
                title="Trading one integral for another",
                blurb=(
                    "It doesn't solve anything outright. The art is making the "
                    "trade favourable - which is entirely about choosing u."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch15-l2-log",
                type="solve",
                title="Differentiate the logarithm",
                blurb=(
                    "The log becomes 1/x, which cancels a power of x and leaves "
                    "something elementary. Choose the other way and you make no "
                    "progress at all."
                ),
                problems=integrals({"tp-log"}, limit=6),
            ),
            Level(
                id="ch15-l3-exp",
                type="solve",
                title="Apply it again",
                blurb=(
                    "Differentiate the power instead - it drops each pass and "
                    "eventually vanishes. If an x remains in the leftover "
                    "integral, you aren't finished."
                ),
                problems=integrals({"tp-exp"}, limit=6),
            ),
        ),
    )


__all__ = ["build"]
