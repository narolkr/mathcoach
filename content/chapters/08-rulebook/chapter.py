"""Chapter 8 - The Rulebook (power, product and quotient rules)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SOLVE, by_template, validated
from mathcoach.generator import choice_problem, differentiate_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def derivatives(ids: set[str], limit: int = MAX_SOLVE) -> tuple:
        return tuple(
            differentiate_problem(template, inst)
            for template, inst in by_template(pairs, ids, limit)
        )

    standard = tuple(
        choice_problem(template, inst, instruction="From memory.")
        for template, inst in by_template(pairs, {"rb-standard"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch08-rulebook",
        number=8,
        act=2,
        name="The Rulebook",
        tag="power, product, quotient",
        subtitle="Four facts and three rules. Everything chapter 9 stands on.",
        requires=("ch07-slope",),
        gate=(
            "Differentiate x³ln x, (2x+1)/(x²−3) and x·e^x·sin x correctly on "
            "the first attempt."
        ),
        levels=(
            Level(
                id="ch08-l1-concept",
                type="concept",
                title="Four facts, three rules",
                blurb="And the habit that saves the most time: simplify first.",
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch08-l2-standard",
                type="choice",
                title="The four to know cold",
                blurb=(
                    "e^x, ln x, sin x, cos x. Watch the minus sign on the last "
                    "one - it costs more marks than anything else in Act II."
                ),
                problems=standard,
            ),
            Level(
                id="ch08-l3-power",
                type="solve",
                title="Power rule, every exponent",
                blurb=(
                    "Power down, exponent reduced. Both, every time - including "
                    "for negative and fractional powers, where there is no "
                    "special case."
                ),
                problems=derivatives({"rb-power", "rb-root"}),
            ),
            Level(
                id="ch08-l4-product",
                type="solve",
                title="Product rule",
                blurb=(
                    "Two terms, added. Not the product of the derivatives - "
                    "differentiation isn't multiplicative."
                ),
                problems=derivatives({"rb-product"}, limit=6),
            ),
            Level(
                id="ch08-l5-quotient",
                type="solve",
                title="Quotient rule",
                blurb=(
                    "Minus, u' first, denominator squared. If you forget the "
                    "order, rebuild it from uv⁻¹ and the product rule."
                ),
                problems=derivatives({"rb-quotient"}, limit=6),
            ),
        ),
    )


__all__ = ["build"]
