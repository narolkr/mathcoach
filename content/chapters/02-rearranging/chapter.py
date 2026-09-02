"""Chapter 2 - Rearranging the Furniture (quadratics and inequalities)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SLOTS, by_template, validated
from mathcoach.generator import choice_problem, slots_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def slots(ids: set[str], limit: int = MAX_SLOTS) -> tuple:
        return tuple(
            slots_problem(template, inst, instruction="Fill in each value.")
            for template, inst in by_template(pairs, ids, limit)
        )

    def choices(ids: set[str], limit: int = MAX_CHOICE) -> tuple:
        return tuple(
            choice_problem(template, inst, instruction="Solve for x.")
            for template, inst in by_template(pairs, ids, limit)
        )

    return Chapter(
        id="ch02-rearranging",
        number=2,
        act=1,
        name="Rearranging the Furniture",
        tag="quadratics",
        subtitle="The same quadratic in three costumes, each useful for something else.",
        requires=("ch01-rust-remover",),
        gate="Complete the square on any quadratic in under 60 seconds.",
        levels=(
            Level(
                id="ch02-l1-concept",
                type="concept",
                title="Three costumes",
                blurb="Expanded, factored, completed square - and what each gives you.",
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch02-l2-roots",
                type="solve",
                title="Find the roots",
                blurb=(
                    "Two numbers that multiply to the constant and add to the "
                    "middle coefficient. Watch the sign flip between factor and "
                    "root."
                ),
                problems=slots({"rf-integer-roots"}, limit=8),
            ),
            Level(
                id="ch02-l3-complete-square",
                type="solve",
                title="Complete the square",
                blurb=(
                    "The chapter gate. Halve the middle coefficient, expand, "
                    "then correct the constant."
                ),
                problems=slots({"rf-complete-square"}, limit=8),
            ),
            Level(
                id="ch02-l4-inequalities",
                type="choice",
                title="Which way round?",
                blurb=(
                    "Half of these divide by a negative. Decide the direction "
                    "before you commit."
                ),
                problems=choices({"rf-inequality"}),
            ),
            Level(
                id="ch02-l5-formula",
                type="solve",
                title="When it won't factor",
                blurb=(
                    "The quadratic formula, kept exact. Leave surds as surds - "
                    "a decimal is a rounded answer, not an answer."
                ),
                problems=slots({"rf-surd-roots"}, limit=6),
            ),
        ),
    )


__all__ = ["build"]
