"""Act III consolidation - mixed integration with nothing naming the technique.

Choosing between substitution, by parts and straight recognition is the skill
this trains, and it is the skill the technique chapters cannot test: in chapter
14 you know it's substitution because that's the chapter you're in.
"""

from __future__ import annotations

from mathcoach.consolidation import build_level
from mathcoach.schema import Chapter

ACT_THREE_INTEGRATION: dict[str, set[str]] = {
    "12-backwards": {"rt-power", "rt-log", "rt-standard"},
    "14-costume": {"cc-exp", "cc-log"},
    "15-trading": {"tp-log", "tp-exp"},
}


def build() -> Chapter:
    return Chapter(
        id="ch16a-consolidation",
        # Shares chapter 16's number: consolidation tiers are ★ nodes, not
        # numbered chapters.
        number=16,
        act=3,
        is_consolidation=True,
        name="Which Technique?",
        tag="consolidation",
        subtitle="Recognise, substitute or integrate by parts - with no clue which.",
        requires=("ch16-expectations",),
        skippable=False,
        gate=(
            "Given a mixed set of integrals, pick the right technique first time "
            "more often than not."
        ),
        levels=(
            build_level(
                level_id="ch16a-l1-mixed",
                title="Hard tier",
                blurb=(
                    "All of Act III. Before writing anything, ask: do I "
                    "recognise this outright, is a function's own derivative "
                    "present, or is it a product of two unrelated things? Those "
                    "three questions pick the technique."
                ),
                sources=ACT_THREE_INTEGRATION,
                tier=None,
                limit=12,
            ),
        ),
    )


__all__ = ["build"]
