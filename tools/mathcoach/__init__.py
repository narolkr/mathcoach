"""MathCoach build-time content pipeline.

All symbolic work happens here, offline, so the browser never needs a CAS.
See docs/ARCHITECTURE.md for why.
"""

from .fingerprint import (
    Domain,
    Fingerprint,
    Variable,
    agrees,
    choose_points,
    fingerprint_at,
)
from .generator import (
    ONE_VAR,
    RULE_APPLIES_WHEN,
    RULE_LABELS,
    VAR_X,
    X,
    Instance,
    Template,
    any_sign,
    choice_problem,
    decompose_problem,
    differentiate_problem,
    positive,
    recognize_problem,
    slots_problem,
    solve_problem,
    symbols_of,
)
from .latex import derivative_prompt, to_katex
from .schema import (
    SCHEMA_VERSION,
    Answer,
    Bundle,
    Chapter,
    Choice,
    Diagnostic,
    DiagnosticItem,
    Distractor,
    Level,
    Problem,
    Step,
)
from .validate import ValidationError, check_bundle, check_instance

__all__ = [
    "ONE_VAR",
    "RULE_APPLIES_WHEN",
    "RULE_LABELS",
    "SCHEMA_VERSION",
    "VAR_X",
    "X",
    "Answer",
    "Bundle",
    "Chapter",
    "Choice",
    "Diagnostic",
    "DiagnosticItem",
    "Distractor",
    "Domain",
    "Fingerprint",
    "Instance",
    "Level",
    "Problem",
    "Step",
    "Template",
    "ValidationError",
    "Variable",
    "agrees",
    "any_sign",
    "check_bundle",
    "check_instance",
    "choice_problem",
    "choose_points",
    "decompose_problem",
    "derivative_prompt",
    "differentiate_problem",
    "fingerprint_at",
    "positive",
    "recognize_problem",
    "slots_problem",
    "solve_problem",
    "symbols_of",
    "to_katex",
]
