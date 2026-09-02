"""Chapter 1 - Rust Remover (index laws, roots, fractions, sign discipline)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_SLOTS, by_template, validated
from mathcoach.generator import slots_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def slots(template_ids: set[str], limit: int = MAX_SLOTS) -> tuple:
        return tuple(
            slots_problem(template, inst, instruction="Fill in each value.")
            for template, inst in by_template(pairs, template_ids, limit)
        )

    return Chapter(
        id="ch01-rust-remover",
        number=1,
        act=1,
        name="Rust Remover",
        tag="index laws and signs",
        subtitle="Clearing the desk, so calculus has room to happen.",
        gate=(
            "Simplify (8x^(-2/3)·y⁴)^(1/2) / (2x⁴y^(-1)) with no calculator and "
            "no sign errors, twice in a row."
        ),
        levels=(
            Level(
                id="ch01-l1-concept",
                type="concept",
                title="Clearing the desk",
                blurb="Short. Read it, then start typing exponents.",
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch01-l2-signs",
                type="solve",
                title="Signs and fractions",
                blurb=(
                    "The unglamorous half. Nested minus signs and fraction "
                    "division, which between them cause more lost marks than "
                    "any concept in this chapter."
                ),
                problems=slots({"rr-nested-negation", "rr-fraction-chain"}),
            ),
            Level(
                id="ch01-l3-exponents",
                type="solve",
                title="Exponents and roots",
                blurb=(
                    "Subtracting negatives, and pulling squares out from under "
                    "a root."
                ),
                problems=slots({"rr-negative-exponent", "rr-surd"}),
            ),
            Level(
                id="ch01-l4-index-laws",
                type="solve",
                title="Everything at once",
                blurb=(
                    "The chapter gate lives here. A root over a quotient, with "
                    "fractional and negative powers throughout. Remember the "
                    "root applies to the coefficient too."
                ),
                problems=slots({"rr-index-quotient"}, limit=6),
            ),
        ),
    )


__all__ = ["build"]
