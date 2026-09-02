"""Act II consolidation - the Sudoku Coach BONUS node.

Mixed differentiation with **no hint about which rule applies**. That is the
whole point: in the technique chapters you always know what you're practising,
and knowing what to reach for is a separate skill that only unscaffolded mixing
trains.

Two tiers, as the roadmap has them: a Medium one after chapter 10 that checks
whether chapter 9 stuck, and a Hard one covering all of Act II.

Hints are stripped; worked steps are kept as the surrender path.
"""

from __future__ import annotations

from mathcoach.consolidation import build_level
from mathcoach.schema import Chapter

# Every differentiation family in Act II, by the chapter that teaches it.
ACT_TWO_DIFFERENTIATION: dict[str, set[str]] = {
    "07-slope": {"sc-first-principles"},
    "08-rulebook": {"rb-power", "rb-root", "rb-product", "rb-quotient"},
    "09-chain-rule": {
        "chain-sin-poly",
        "chain-exp-poly",
        "chain-log-poly",
        "chain-power-linear",
        "chain-power-trig",
        "chain-sin-log",
        "chain-exp-cos-squared",
    },
    "10-hidden": {"hr-implicit-circle", "hr-implicit-poly"},
}

# The Medium tier draws only on the rules and the simpler chain shapes.
MEDIUM_SOURCES: dict[str, set[str]] = {
    "08-rulebook": {"rb-power", "rb-product", "rb-quotient"},
    "09-chain-rule": {"chain-sin-poly", "chain-exp-poly", "chain-power-linear"},
}


def build() -> Chapter:
    return Chapter(
        id="ch11a-consolidation",
        # Shares chapter 11's number: consolidation tiers are ★ nodes in the
        # roadmap, not numbered chapters, and the campaign map draws them as
        # stars and skips them when looking for missing chapters.
        number=11,
        act=2,
        is_consolidation=True,
        name="No Scaffolding",
        tag="consolidation",
        subtitle="Mixed problems, nothing telling you which rule to reach for.",
        requires=("ch10-hidden",),
        # Never skippable: the diagnostic tests individual techniques, and this
        # tests choosing between them, which is a different thing entirely.
        skippable=False,
        gate=(
            "Work a mixed set without being told which rule applies, and get "
            "the technique right first time more often than not."
        ),
        levels=(
            build_level(
                level_id="ch11a-l1-medium",
                title="Medium tier",
                blurb=(
                    "Power, product, quotient and chain, shuffled. Decide which "
                    "rule you need before writing anything - that decision is "
                    "what's being tested."
                ),
                sources=MEDIUM_SOURCES,
                tier="medium",
                limit=8,
            ),
            build_level(
                level_id="ch11a-l2-hard",
                title="Hard tier",
                blurb=(
                    "All of Act II, including three- and four-layer "
                    "compositions, implicit curves and first principles. No "
                    "hints at all. If you finish with fewer factors than layers, "
                    "you dropped one."
                ),
                sources=ACT_TWO_DIFFERENTIATION,
                tier=None,
                limit=12,
            ),
        ),
    )


__all__ = ["build"]
