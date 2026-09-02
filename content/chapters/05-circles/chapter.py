"""Chapter 5 - Just Enough Circles (only the trig later chapters need)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, by_template, validated
from mathcoach.generator import choice_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def choices(ids: set[str], instruction: str, limit: int = MAX_CHOICE) -> tuple:
        return tuple(
            choice_problem(template, inst, instruction=instruction)
            for template, inst in by_template(pairs, ids, limit)
        )

    return Chapter(
        id="ch05-circles",
        number=5,
        act=1,
        name="Just Enough Circles",
        tag="trigonometry, minimally",
        subtitle="Ten values and one identity. Deliberately no more than that.",
        requires=("ch03-machines",),
        gate="State sin and cos of 0, π/6, π/4, π/3, π/2 from memory.",
        levels=(
            Level(
                id="ch05-l1-concept",
                type="concept",
                title="The enough",
                blurb=(
                    "Short on purpose. Spend spare time on chapter 4 instead."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch05-l2-values",
                type="choice",
                title="The ten values",
                blurb=(
                    "The chapter gate. Every wrong option is a real value from "
                    "the same table, so you can't get there by elimination."
                ),
                problems=choices(
                    {"jc-exact-value"}, "From memory. No calculator."
                ),
            ),
            Level(
                id="ch05-l3-identity",
                type="choice",
                title="The one identity",
                blurb=(
                    "sin² + cos² = 1, for any argument at all. It swaps the "
                    "function and leaves the argument alone."
                ),
                problems=choices({"jc-identity"}, "Simplify."),
            ),
            Level(
                id="ch05-l4-facts",
                type="choice",
                title="Why radians",
                blurb=(
                    "The two facts calculus leans on, and the reason degrees "
                    "never appear again after this chapter."
                ),
                problems=choices({"jc-calculus-facts"}, "Pick one."),
            ),
        ),
    )


__all__ = ["build"]
