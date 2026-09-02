"""Shared level-assembly helpers.

Every chapter caps its levels at roughly one 30-minute sitting and spreads
problems across templates rather than exhausting one shape before moving on.
Instances that don't make a level aren't wasted - they're the pool the Practice
section and the spaced-repetition warm-up will draw from.
"""

from __future__ import annotations

from collections.abc import Iterable

from .generator import Instance, Template
from .validate import check_instance

Pair = tuple[Template, Instance]

# Per the roadmap's 30-minute daily protocol. Choice items run ~45 seconds,
# slot and decompose items ~2 minutes, solves anywhere from 2 to 45.
MAX_CHOICE = 16
MAX_SLOTS = 10
MAX_SOLVE = 8


def validated(templates: Iterable[Template]) -> list[Pair]:
    """Build and check every instance of every template."""
    pairs: list[Pair] = []
    for template in templates:
        for inst in template.instances():
            check_instance(template, inst)
            pairs.append((template, inst))
    return pairs


def round_robin(pairs: list[Pair], limit: int) -> list[Pair]:
    """Take up to `limit` pairs, one from each template before repeating."""
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


def interleave(primary: list[Pair], others: list[Pair], limit: int) -> list[Pair]:
    """Alternate two pools, stopping when either runs out.

    Used so a recognition level never ends in a long run of one answer, which
    would let the learner score well by guessing rather than by looking.
    """
    out: list[Pair] = []
    for index in range(min(len(primary), len(others))):
        out.append(primary[index])
        out.append(others[index])
        if len(out) >= limit:
            break
    return out[:limit]


def by_tier(pairs: list[Pair], tiers: set[str], limit: int = MAX_SOLVE) -> list[Pair]:
    return round_robin([(t, i) for t, i in pairs if t.tier in tiers], limit)


def by_template(pairs: list[Pair], template_ids: set[str], limit: int) -> list[Pair]:
    return round_robin([(t, i) for t, i in pairs if t.id in template_ids], limit)
