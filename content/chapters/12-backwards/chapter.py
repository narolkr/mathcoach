"""Chapter 12 - Running the Tape Backwards (antiderivatives)."""

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
        id="ch12-backwards",
        number=12,
        act=3,
        name="Running the Tape Backwards",
        tag="antiderivatives",
        subtitle="Which function has this as its derivative? That's the whole question.",
        requires=("ch08-rulebook",),
        gate=(
            "Integrate x⁻¹, x³, e^x, sin x and 1/(1+x²) from memory - with the "
            "x⁻¹ case correct, since it's the one everyone gets wrong."
        ),
        levels=(
            Level(
                id="ch12-l1-concept",
                type="concept",
                title="A question, not a procedure",
                blurb=(
                    "And the check that is always available: differentiate your "
                    "answer back."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch12-l2-power",
                type="solve",
                title="The power rule backwards",
                blurb="Exponent up by one, then divide by the new exponent.",
                problems=integrals({"rt-power"}),
            ),
            Level(
                id="ch12-l3-standard",
                type="solve",
                title="The table, read backwards",
                blurb=(
                    "Chapter 8's four derivatives in reverse. Watch where the "
                    "minus sign ends up."
                ),
                problems=integrals({"rt-standard"}),
            ),
            Level(
                id="ch12-l4-log",
                type="solve",
                title="The one exception",
                blurb=(
                    "1/x is the case the power rule cannot touch, for a boring "
                    "reason: it would divide by zero. Part of the chapter gate."
                ),
                problems=integrals({"rt-log"}, limit=6),
            ),
        ),
    )


__all__ = ["build"]
