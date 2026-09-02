"""The build output contract.

These dataclasses are the single source of truth for the JSON the frontend
loads. `tools/build.py` writes the matching TypeScript, so a change here that
the frontend hasn't caught up with fails `npm run build` rather than breaking a
level at runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .fingerprint import Fingerprint

# 2: fingerprints became multivariable (xs -> variables + points), and
#    `recognize` generalised to arbitrary choice options.
SCHEMA_VERSION = 2

LevelType = Literal["concept", "choice", "decompose", "solve"]
Tier = Literal["easy", "medium", "hard", "challenge"]

# Time budgets from the roadmap's difficulty tiers, in seconds. The UI shows
# these as guidance next to the hint button; it never enforces them.
TIER_SECONDS: dict[str, int] = {
    "easy": 5 * 60,
    "medium": 20 * 60,
    "hard": 45 * 60,
    "challenge": 0,  # 0 == open-ended
}


@dataclass(frozen=True)
class Distractor:
    """A specific wrong answer, with the misconception it reveals."""

    id: str
    fingerprint: Fingerprint
    # Written to the learner, second person, naming what they did.
    feedback: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "fingerprint": self.fingerprint.to_dict(),
            "feedback": self.feedback,
        }


@dataclass(frozen=True)
class Step:
    latex: str
    note: str

    def to_dict(self) -> dict:
        return {"latex": self.latex, "note": self.note}


@dataclass(frozen=True)
class Answer:
    """One gradeable slot. `decompose` levels have two or more; solves have one."""

    label: str
    latex: str
    fingerprint: Fingerprint
    distractors: tuple[Distractor, ...] = ()
    # Shown under the input: "a number", "in terms of x", and so on.
    hint_text: str = ""

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "latex": self.latex,
            "fingerprint": self.fingerprint.to_dict(),
            "distractors": [d.to_dict() for d in self.distractors],
            "hintText": self.hint_text,
        }


@dataclass(frozen=True)
class Choice:
    """One option in a `choice` problem."""

    id: str
    # Plain text, or LaTeX when `is_latex` is set.
    label: str
    is_latex: bool = False
    # Why this option is right or wrong. Shown after picking.
    feedback: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "isLatex": self.is_latex,
            "feedback": self.feedback,
        }


@dataclass(frozen=True)
class Problem:
    id: str
    template_id: str
    tier: Tier
    # What the learner is asked to do, in words.
    instruction: str
    # The expression under discussion, as KaTeX.
    prompt_latex: str
    answers: tuple[Answer, ...] = ()
    # Progressive hints, revealed one rung at a time. Never the full solution.
    hints: tuple[str, ...] = ()
    steps: tuple[Step, ...] = ()
    # `choice` problems only.
    choices: tuple[Choice, ...] = ()
    correct_choice: str | None = None
    # Variables the learner may use in a typed answer, for the input's help text.
    variables: tuple[str, ...] = ()
    # Standing assumptions, e.g. "assume x, y > 0". Shown with the prompt.
    assumption: str = ""

    def to_dict(self) -> dict:
        out: dict = {
            "id": self.id,
            "templateId": self.template_id,
            "tier": self.tier,
            "instruction": self.instruction,
            "promptLatex": self.prompt_latex,
            "answers": [a.to_dict() for a in self.answers],
            "hints": list(self.hints),
            "steps": [s.to_dict() for s in self.steps],
            "variables": list(self.variables),
            "assumption": self.assumption,
        }
        if self.choices:
            out["choices"] = [c.to_dict() for c in self.choices]
            out["correctChoice"] = self.correct_choice
        return out


@dataclass(frozen=True)
class Level:
    id: str
    type: LevelType
    title: str
    # One-line framing shown before the first problem.
    blurb: str
    problems: tuple[Problem, ...] = ()
    # `concept` levels only: Markdown body with $...$ math.
    body_md: str = ""

    def to_dict(self) -> dict:
        out: dict = {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "blurb": self.blurb,
            "problems": [p.to_dict() for p in self.problems],
        }
        if self.body_md:
            out["bodyMd"] = self.body_md
        return out


@dataclass(frozen=True)
class Chapter:
    id: str
    number: int
    act: int
    name: str
    tag: str
    # The mastery gate from the roadmap - the thing you can do when you're done.
    gate: str
    levels: tuple[Level, ...] = ()
    # Chapter ids recommended before this one. Advisory: nothing is hard-locked.
    requires: tuple[str, ...] = ()
    # A chapter the diagnostic can mark as already-known and collapse.
    skippable: bool = True
    # One line on why this chapter exists, shown on the campaign map.
    subtitle: str = ""
    # A consolidation tier - the Sudoku Coach BONUS node. Shown with a star
    # rather than a number, because the roadmap doesn't number these, and
    # skipped by the campaign map's missing-chapter detection: it shares its
    # `number` with the chapter it follows, so counting it would invent a gap.
    is_consolidation: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "number": self.number,
            "act": self.act,
            "name": self.name,
            "tag": self.tag,
            "gate": self.gate,
            "requires": list(self.requires),
            "skippable": self.skippable,
            "subtitle": self.subtitle,
            "isConsolidation": self.is_consolidation,
            "levels": [level.to_dict() for level in self.levels],
        }


@dataclass(frozen=True)
class DiagnosticItem:
    """One placement question, and the chapter it reports on."""

    problem: Problem
    chapter_id: str
    # What this item is actually testing, for the results readout.
    skill: str

    def to_dict(self) -> dict:
        return {
            "problem": self.problem.to_dict(),
            "chapterId": self.chapter_id,
            "skill": self.skill,
        }


@dataclass(frozen=True)
class Diagnostic:
    """The placement quiz. Decides which Act I chapters are worth your time."""

    id: str
    title: str
    blurb: str
    items: tuple[DiagnosticItem, ...]
    # Getting this fraction of a chapter's items right marks it as known.
    pass_threshold: float = 0.999

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "blurb": self.blurb,
            "passThreshold": self.pass_threshold,
            "items": [item.to_dict() for item in self.items],
        }


@dataclass(frozen=True)
class Bundle:
    chapters: tuple[Chapter, ...]
    diagnostic: Diagnostic | None = None
    acts: dict[int, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schemaVersion": SCHEMA_VERSION,
            "tierSeconds": TIER_SECONDS,
            "acts": {str(k): v for k, v in sorted(self.acts.items())},
            "chapters": [c.to_dict() for c in self.chapters],
            "diagnostic": self.diagnostic.to_dict() if self.diagnostic else None,
        }
