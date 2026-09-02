"""Chapter 4 - Growth and Its Undoing (exponentials and logarithms).

The heaviest chapter in Act I, deliberately: this is where softmax,
cross-entropy and log-likelihood actually come from.
"""

from __future__ import annotations

from pathlib import Path

from mathcoach.assemble import MAX_CHOICE, MAX_SLOTS, MAX_SOLVE, by_template, validated
from mathcoach.generator import choice_problem, slots_problem, solve_problem
from mathcoach.schema import Chapter, Level

from .templates import TEMPLATES

HERE = Path(__file__).parent


def build() -> Chapter:
    pairs = validated(TEMPLATES)

    expand = tuple(
        slots_problem(
            template,
            inst,
            instruction="Give each coefficient.",
        )
        for template, inst in by_template(pairs, {"gu-expand-log"}, MAX_SLOTS)
    )

    condense = tuple(
        solve_problem(
            template,
            inst,
            label="argument",
            instruction="What goes inside the single logarithm?",
        )
        for template, inst in by_template(pairs, {"gu-condense-log"}, MAX_SOLVE)
    )

    solving = tuple(
        solve_problem(
            template, inst, label="x", instruction="Solve for x, exactly."
        )
        for template, inst in by_template(pairs, {"gu-solve-exponential"}, MAX_SOLVE)
    )

    why = tuple(
        choice_problem(template, inst, instruction="Why?")
        for template, inst in by_template(pairs, {"gu-why-logs"}, MAX_CHOICE)
    )

    return Chapter(
        id="ch04-growth",
        number=4,
        act=1,
        name="Growth and Its Undoing",
        tag="exponentials and logs",
        subtitle="Where softmax, cross-entropy and log-likelihood come from.",
        requires=("ch01-rust-remover",),
        # Not skippable by the diagnostic: even someone fluent in school logs
        # benefits from the log-likelihood material, which is the AI-specific
        # half and appears in no school syllabus.
        skippable=False,
        gate=(
            "Expand ln(a²b/√c) into separate logs and reverse it, instantly. "
            "Explain why log turns a product of probabilities into a sum - and "
            "why that matters when you multiply 10,000 of them."
        ),
        levels=(
            Level(
                id="ch04-l1-concept",
                type="concept",
                title="The chapter to over-invest in",
                blurb=(
                    "Three laws, one inverse relationship, and the reason every "
                    "loss function has a log in it."
                ),
                body_md=(HERE / "concept.md").read_text(encoding="utf-8"),
            ),
            Level(
                id="ch04-l2-solve",
                type="solve",
                title="Unstick the exponent",
                blurb=(
                    "The unknown is trapped in an exponent. One move frees it."
                ),
                problems=solving,
            ),
            Level(
                id="ch04-l3-expand",
                type="solve",
                title="Break it apart",
                blurb=(
                    "The chapter gate. Products to sums, quotients to "
                    "differences, powers to multipliers - and remember a root is "
                    "a fractional power sitting in a denominator."
                ),
                problems=expand,
            ),
            Level(
                id="ch04-l4-condense",
                type="solve",
                title="Put it back together",
                blurb=(
                    "The same three laws, run backwards. The gate asks you to do "
                    "this instantly, in both directions."
                ),
                problems=condense,
            ),
            Level(
                id="ch04-l5-why",
                type="choice",
                title="Why logs are everywhere in ML",
                blurb=(
                    "The half of this chapter no school syllabus covers, and the "
                    "reason it earned extra weight."
                ),
                problems=why,
            ),
        ),
    )


__all__ = ["build"]
