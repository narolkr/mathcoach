"""Chapter 7 - The Slope of a Curve (what a derivative actually is)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SOLVE, by_template, validated
from mathcoach.generator import choice_problem, differentiate_problem, solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    first_principles = tuple(
        differentiate_problem(template, inst)
        for template, inst in by_template(pairs, {"sc-first-principles"}, MAX_SOLVE)
    )
    numeric = tuple(
        solve_problem(
            template,
            inst,
            label="f'(a)",
            instruction="Give the exact value, then check it numerically.",
        )
        for template, inst in by_template(pairs, {"sc-numeric"}, MAX_SOLVE)
    )
    meaning = tuple(
        choice_problem(template, inst, instruction="What does that number mean?")
        for template, inst in by_template(pairs, {"sc-meaning"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch07-slope",
        number=7,
        act=2,
        name="The Slope of a Curve",
        tag="the derivative itself",
        subtitle="A slope at a single point - and the numeric check that Act V ends on.",
        requires=("ch06-approaching",),
        gate=(
            "Derive f'(x) for f(x) = x² from the difference quotient, on paper, "
            "unaided. Then say in one sentence what the number f'(3) means."
        ),
        levels=(
            Level(
                id="ch07-l1-concept",
                type="concept",
                title="What a derivative is",
                blurb="A two-point slope, squeezed until the two points coincide.",
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch07-l2-definition",
                type="solve",
                title="From first principles",
                blurb=(
                    "The chapter gate. Substitute x+h, subtract, divide by h, "
                    "let h go to zero. Do it by hand a few times so you could "
                    "rebuild any rule you forget."
                ),
                problems=first_principles,
            ),
            Level(
                id="ch07-l3-meaning",
                type="choice",
                title="What the number tells you",
                blurb=(
                    "Not how to compute it. This reading is the one gradient "
                    "descent depends on."
                ),
                problems=meaning,
            ),
            Level(
                id="ch07-l4-numeric",
                type="solve",
                title="Check it with arithmetic",
                blurb=(
                    "The central difference. Exactly the gradient check that "
                    "verifies backpropagation in Act V - meet it now as "
                    "arithmetic."
                ),
                problems=numeric,
            ),
        ),
    )


__all__ = ["build"]
