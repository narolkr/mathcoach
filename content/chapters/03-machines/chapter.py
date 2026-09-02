"""Chapter 3 - Machines with Inputs (composition, domains, inverses)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SOLVE, round_robin, validated
from mathcoach.generator import choice_problem, solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent

COMPOSE_IDS = {
    "mi-compose-power",
    "mi-compose-root-1",
    "mi-compose-root-2",
    "mi-compose-root-4",
}


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    def pick(ids: set[str], limit: int) -> list:
        return round_robin([(t, i) for t, i in pairs if t.id in ids], limit)

    compose = tuple(
        solve_problem(
            template,
            inst,
            label="f(g(x))",
            instruction="Write f(g(x)) in terms of x.",
        )
        for template, inst in pick(COMPOSE_IDS, MAX_SOLVE)
    )

    inverses = tuple(
        solve_problem(
            template, inst, label="f⁻¹(x)", instruction="Find the inverse."
        )
        for template, inst in pick({"mi-inverse"}, 6)
    )

    domains = tuple(
        choice_problem(
            template, inst, instruction="What is the exact domain of f(g(x))?"
        )
        for template, inst in pick({"mi-domain"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch03-machines",
        number=3,
        act=1,
        name="Machines with Inputs",
        tag="composition",
        subtitle="The idea chapter 9 is entirely about, met early and made automatic.",
        requires=("ch02-rearranging",),
        gate=(
            "Given f(x) = √(x−1) and g(x) = 1/x, write f∘g and g∘f with their "
            "exact domains."
        ),
        levels=(
            Level(
                id="ch03-l1-concept",
                type="concept",
                title="Composition, and why it matters most",
                blurb=(
                    "The one idea in Act I that chapter 9 depends on completely."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch03-l2-compose",
                type="solve",
                title="Substitute the whole thing",
                blurb=(
                    "Everywhere f has an x, the entire g(x) goes in - brackets "
                    "included. Order matters: f(g(x)) is not g(f(x))."
                ),
                problems=compose,
            ),
            Level(
                id="ch03-l3-domains",
                type="choice",
                title="Where is it actually defined?",
                blurb=(
                    "Two things can go wrong at once: g must be defined, and f "
                    "must accept what g hands it. Composing shrinks domains."
                ),
                problems=domains,
            ),
            Level(
                id="ch03-l4-inverses",
                type="solve",
                title="Undo it",
                blurb=(
                    "Set y = f(x), rearrange for x, swap the letters. And keep "
                    "f⁻¹ distinct from 1/f."
                ),
                problems=inverses,
            ),
        ),
    )


__all__ = ["build"]
