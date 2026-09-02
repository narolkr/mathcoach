"""Chapter 11 - Finding the Bottom (critical points, convexity, optimisation)."""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SLOTS, by_template, validated
from mathcoach.generator import choice_problem, slots_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    critical = tuple(
        slots_problem(
            template, inst, instruction="Give both critical points, smaller first."
        )
        for template, inst in by_template(pairs, {"fb-critical-points"}, MAX_SLOTS)
    )
    classify = tuple(
        choice_problem(template, inst, instruction="What kind of point is it?")
        for template, inst in by_template(pairs, {"fb-classify"}, MAX_CHOICE)
    )
    convexity = tuple(
        choice_problem(template, inst, instruction="Which follows?")
        for template, inst in by_template(pairs, {"fb-convexity"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch11-bottom",
        number=11,
        act=2,
        name="Finding the Bottom",
        tag="optimisation",
        subtitle="Gradient descent in one dimension, and why convexity is the easy case.",
        requires=("ch08-rulebook",),
        # Not skippable: the convexity and step-size material is the
        # ML-specific half and appears in no school treatment of stationary
        # points, so prior fluency is no evidence of knowing it.
        skippable=False,
        gate=(
            "Find and classify all critical points of f(x) = x³ − 3x² + 4, and "
            "explain why a convex function has exactly one minimum."
        ),
        levels=(
            Level(
                id="ch11-l1-concept",
                type="concept",
                title="This chapter is gradient descent",
                blurb=(
                    "Training a model means finding the minimum of a loss "
                    "function. That's this, with more variables."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch11-l2-critical",
                type="solve",
                title="Where the slope is zero",
                blurb="Differentiate, set to zero, solve. Half the chapter gate.",
                problems=critical,
            ),
            Level(
                id="ch11-l3-classify",
                type="choice",
                title="Which kind of flat point",
                blurb=(
                    "Curvature decides. And notice what the test cannot see - "
                    "that blind spot is why non-convex optimisation is hard."
                ),
                problems=classify,
            ),
            Level(
                id="ch11-l4-convexity",
                type="choice",
                title="Convexity and step size",
                blurb=(
                    "The other half of the gate, and the part that matters most "
                    "for Act V."
                ),
                problems=convexity,
            ),
        ),
    )


__all__ = ["build"]
