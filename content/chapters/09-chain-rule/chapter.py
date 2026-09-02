"""Chapter 9 - Nesting Dolls (the chain rule).

Assembles levels from the templates in this directory. The level *order* here is
the pedagogy: recognise the shape, then decompose it, then execute, then do it
all with no scaffolding.

Level sizes are capped so one level is roughly one 30-minute sitting. Instances
that don't make the cut aren't wasted - they're the pool the Practice section and
the spaced-repetition warm-up draw from later.
"""

from __future__ import annotations

from pathlib import Path

from mathcoach.generator import (
    Instance,
    Template,
    decompose_problem,
    differentiate_problem,
    recognize_problem,
)
from mathcoach.schema import Chapter, Level, Problem
from mathcoach.validate import check_instance

from .templates import CHAIN_TEMPLATES, FOIL_TEMPLATES

HERE = Path(__file__).parent

# Roughly one sitting each, per the roadmap's 30-minute daily protocol.
# Recognition items are ~45 seconds, decomposition ~2 minutes, solves 2-45.
MAX_RECOGNIZE = 16
MAX_DECOMPOSE = 10
MAX_SOLVE = 8

# (a·x + b)^n is excluded from `recognize`: whether you call it the chain rule or
# the generalised power rule is a matter of taste, and an item with two
# defensible answers teaches nothing but frustration.
_AMBIGUOUS_FOR_RECOGNIZE = {"chain-power-linear"}

Pair = tuple[Template, Instance]


def _validated(templates: tuple[Template, ...]) -> list[Pair]:
    pairs: list[Pair] = []
    for template in templates:
        for inst in template.instances():
            check_instance(template, inst)
            pairs.append((template, inst))
    return pairs


def _round_robin(pairs: list[Pair], limit: int) -> list[Pair]:
    """Take up to `limit` pairs, spreading across templates rather than
    exhausting one shape before moving to the next."""
    by_template: dict[str, list[Pair]] = {}
    for template, inst in pairs:
        by_template.setdefault(template.id, []).append((template, inst))

    picked: list[Pair] = []
    depth = 0
    while len(picked) < limit:
        added = False
        for bucket in by_template.values():
            if depth < len(bucket) and len(picked) < limit:
                picked.append(bucket[depth])
                added = True
        if not added:
            break
        depth += 1
    return picked


def _interleave(chain: list[Pair], foils: list[Pair], limit: int) -> list[Pair]:
    """Alternate chain and non-chain items, and stop as soon as either side runs
    out - so "chain" is never the safe guess for a run of trailing items."""
    out: list[Pair] = []
    for index in range(min(len(chain), len(foils))):
        out.append(chain[index])
        out.append(foils[index])
        if len(out) >= limit:
            break
    return out[:limit]


def build() -> Chapter:
    concept_md = (HERE / "concept.md").read_text(encoding="utf-8")

    chain_pairs = _validated(CHAIN_TEMPLATES)
    foil_pairs = _validated(FOIL_TEMPLATES)

    # --- Level 2: rule recognition -----------------------------------------
    recognisable_chain = _round_robin(
        [(t, i) for t, i in chain_pairs if t.id not in _AMBIGUOUS_FOR_RECOGNIZE],
        MAX_RECOGNIZE,
    )
    recognize_pool = [
        recognize_problem(template, inst)
        for template, inst in _interleave(
            recognisable_chain, _round_robin(foil_pairs, MAX_RECOGNIZE), MAX_RECOGNIZE
        )
    ]

    # --- Level 3: decomposition --------------------------------------------
    decompose_pool = [
        decompose_problem(template, inst)
        for template, inst in _round_robin(
            [(t, i) for t, i in chain_pairs if t.supports_decompose], MAX_DECOMPOSE
        )
    ]

    # --- Levels 4-6: execution, split by tier ------------------------------
    def solves(tiers: set[str]) -> tuple[Problem, ...]:
        pool = _round_robin(
            [(t, i) for t, i in chain_pairs if t.tier in tiers], MAX_SOLVE
        )
        return tuple(differentiate_problem(template, inst) for template, inst in pool)

    return Chapter(
        id="ch09-chain-rule",
        number=9,
        act=2,
        name="Nesting Dolls",
        tag="the chain rule",
        gate=(
            "Differentiate sin(ln(3x²+1)) and e^(cos²(2x)) with no errors - "
            "and explain what you're doing at each layer, not just execute it."
        ),
        levels=(
            Level(
                id="ch09-l1-concept",
                type="concept",
                title="Why this rule matters most",
                blurb="Read this once. Then stop reading and start solving.",
                body_md=concept_md,
            ),
            Level(
                id="ch09-l2-recognize",
                type="choice",
                title="Spot the rule",
                blurb=(
                    "Don't differentiate anything. Just say which rule you'd "
                    "reach for. Fast reps - recognising the shape is a separate "
                    "skill from executing it."
                ),
                problems=tuple(recognize_pool),
            ),
            Level(
                id="ch09-l3-decompose",
                type="decompose",
                title="Name the inner function",
                blurb=(
                    "No differentiating the whole thing yet. Just identify u and "
                    "du/dx. This is the skill the chain rule actually rests on."
                ),
                problems=tuple(decompose_pool),
            ),
            Level(
                id="ch09-l4-solve-easy",
                type="solve",
                title="One layer",
                blurb="Single compositions. Outer function, inner function, multiply.",
                problems=solves({"easy"}),
            ),
            Level(
                id="ch09-l5-solve-medium",
                type="solve",
                title="Two layers",
                blurb=(
                    "Now the inner function needs work of its own. Count the "
                    "layers before you start."
                ),
                problems=solves({"medium"}),
            ),
            Level(
                id="ch09-l6-solve-hard",
                type="solve",
                title="Three and four layers",
                blurb=(
                    "The chapter gate lives here. Every layer contributes exactly "
                    "one factor - if you finish with fewer factors than layers, "
                    "you dropped one."
                ),
                problems=solves({"hard"}),
            ),
        ),
    )


__all__ = ["build"]
