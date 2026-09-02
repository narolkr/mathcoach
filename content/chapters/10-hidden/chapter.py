"""Chapter 10 - Hidden Relations (implicit differentiation, related rates)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_SOLVE, by_template, validated
from mathcoach.generator import solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    implicit = tuple(
        solve_problem(
            template,
            inst,
            label="dy/dx",
            instruction="Find dy/dx. The answer may contain both x and y.",
        )
        for template, inst in by_template(
            pairs, {"hr-implicit-circle", "hr-implicit-poly"}, MAX_SOLVE
        )
    )
    rates = tuple(
        solve_problem(
            template,
            inst,
            label="dV/dt",
            instruction="Give the exact rate. Keep the π.",
        )
        for template, inst in by_template(pairs, {"hr-related-rates"}, 6)
    )

    return Chapter(
        id="ch10-hidden",
        number=10,
        act=2,
        name="Hidden Relations",
        tag="implicit differentiation",
        subtitle="Slopes without ever solving for y - and the first multivariable answer.",
        requires=("ch09-chain-rule",),
        gate="Find dy/dx for x² + xy + y³ = 7.",
        levels=(
            Level(
                id="ch10-l1-concept",
                type="concept",
                title="When you can't solve for y",
                blurb=(
                    "One idea: treat y as a function of x, and let the chain "
                    "rule do the rest."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch10-l2-implicit",
                type="solve",
                title="Differentiate both sides",
                blurb=(
                    "Every y contributes a dy/dx. Collect them, then divide. "
                    "The chapter gate is in here."
                ),
                problems=implicit,
            ),
            Level(
                id="ch10-l3-rates",
                type="solve",
                title="Rates through time",
                blurb=(
                    "The same chain rule with t underneath. Write down what is "
                    "changing with respect to what before you start."
                ),
                problems=rates,
            ),
        ),
    )


__all__ = ["build"]
