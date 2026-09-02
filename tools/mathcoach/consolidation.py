"""Consolidation tiers - the Sudoku Coach BONUS analogue.

Sudoku Coach interleaves its technique chapters with difficulty-graded BONUS
nodes: mixed puzzles, no scaffolding, and crucially **no hint about which
technique applies**. Recognising what to reach for is the skill those stages
train, and it's a different skill from executing a named technique.

These are separate chapters on the campaign map, exactly as BONUS nodes are
separate nodes, and they are built the same way: draw instances from the
chapters already covered, strip the hints, and mix the order so consecutive
problems rarely want the same tool.

Worked steps are kept. Hints would tell you the technique, which is the whole
point of withholding them; steps are the surrender path, taken after you've
tried.
"""

from __future__ import annotations

from dataclasses import replace

from .assemble import Pair, validated
from .generator import (
    Instance,
    Template,
    differentiate_problem,
    slots_problem,
    solve_problem,
)
from .loader import templates_of
from .schema import Level, Problem, Tier


def _unscaffold(inst: Instance) -> Instance:
    """Strip everything that would name the technique.

    Hints, obviously. But also the instance's own `instruction`, which is where
    this first leaked: chapter 7's first-principles template says "from the
    definition, not from the rules", which hands over the method as plainly as
    any hint would.

    The instruction is only dropped for free-form answers, where the generic
    "differentiate this" is a complete brief. Slot problems keep theirs, because
    there the instruction describes the *format* the answer must take ("give p,
    then q") and the learner genuinely cannot proceed without it.
    """
    return replace(
        inst,
        hints=(),
        instruction=None if not inst.slots else inst.instruction,
    )


def gather(sources: dict[str, set[str]]) -> list[Pair]:
    """Validated instances from `{chapter_dir: {template_id, ...}}`."""
    pairs: list[Pair] = []
    for dirname, wanted in sources.items():
        chapter_templates = [
            template for template in templates_of(dirname) if template.id in wanted
        ]
        missing = wanted - {t.id for t in chapter_templates}
        if missing:
            raise KeyError(f"{dirname}: no such templates {sorted(missing)}")
        pairs.extend(validated(chapter_templates))
    return pairs


def _spread(pairs: list[Pair], limit: int) -> list[Pair]:
    """Interleave across templates so neighbours rarely share a technique.

    Round-robin over template buckets: one from each in turn, which by
    construction puts a different shape next to every problem.
    """
    buckets: dict[str, list[Pair]] = {}
    for template, inst in pairs:
        buckets.setdefault(template.id, []).append((template, inst))

    out: list[Pair] = []
    depth = 0
    while len(out) < limit:
        added = False
        for bucket in buckets.values():
            if depth < len(bucket) and len(out) < limit:
                out.append(bucket[depth])
                added = True
        if not added:
            break
        depth += 1
    return out


def _to_problem(template: Template, inst: Instance) -> Problem:
    """Assemble without saying which kind of problem it is."""
    stripped = _unscaffold(inst)
    if stripped.slots:
        return slots_problem(
            template,
            stripped,
            instruction="Work it out. Nothing here tells you which tool to use.",
        )
    if template.rule is not None:
        return differentiate_problem(template, stripped)
    return solve_problem(
        template,
        stripped,
        instruction="Work it out. Nothing here tells you which tool to use.",
    )


def build_level(
    level_id: str,
    title: str,
    blurb: str,
    sources: dict[str, set[str]],
    tier: Tier | None = None,
    limit: int = 10,
) -> Level:
    """One unscaffolded mixed level. `tier=None` draws from every tier."""
    pairs = gather(sources)
    if tier is not None:
        pairs = [(t, i) for t, i in pairs if t.tier == tier]
    chosen = _spread(pairs, limit)
    if not chosen:
        raise ValueError(
            f"{level_id}: no instances matched {sources}"
            + (f" at tier {tier}" if tier else "")
        )

    problems = tuple(
        # Consolidation ids must not collide with the chapters they came from,
        # which hold the scaffolded copies of the same instances.
        replace(_to_problem(template, inst), id=f"{level_id}--{template.id}--{inst.slug}")
        for template, inst in chosen
    )

    return Level(id=level_id, type="solve", title=title, blurb=blurb, problems=problems)
