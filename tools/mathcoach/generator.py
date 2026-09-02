"""Turning templates into fingerprinted problems.

A *template* is a parameterised family of problems ("sine of a polynomial").
An *instance* is one member of that family with concrete numbers. This module
owns the conversion from instance to the `Problem` the frontend consumes:
picking shared sample points, fingerprinting the answer and every distractor,
and rendering all the LaTeX.

Templates themselves live with their chapter, under content/chapters/.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace

import sympy as sp

from .fingerprint import (
    Domain,
    Fingerprint,
    Variable,
    choose_points,
    fingerprint_at,
)
from .latex import derivative_prompt, to_katex
from .schema import Answer, Choice, Distractor, Problem, Step, Tier

# The single-variable default, used by every differentiation chapter.
X = sp.Symbol("x", real=True)
VAR_X = Variable("x", Domain.ANY)
ONE_VAR: tuple[Variable, ...] = (VAR_X,)


def positive(*names: str) -> tuple[Variable, ...]:
    """Variables restricted to positive values - for logs and fractional powers."""
    return tuple(Variable(name, Domain.POSITIVE) for name in names)


def any_sign(*names: str) -> tuple[Variable, ...]:
    return tuple(Variable(name, Domain.ANY) for name in names)


def symbols_of(variables: Sequence[Variable]) -> tuple[sp.Symbol, ...]:
    """The SymPy symbols a template must build its expressions from."""
    return tuple(variable.symbol for variable in variables)


@dataclass(frozen=True)
class Instance:
    """One concrete problem, still in SymPy terms."""

    # The expression the problem is about.
    expr: sp.Expr
    # The correct answer. Ignored for `choice` instances.
    answer: sp.Expr | None = None
    # (id, wrong expression, feedback naming the misconception).
    distractors: tuple[tuple[str, sp.Expr, str], ...] = ()
    hints: tuple[str, ...] = ()
    steps: tuple[tuple[str, str], ...] = ()
    # For `decompose` levels: extra named answer slots beyond the main one, as
    # (label, expression, help text).
    slots: tuple[tuple[str, sp.Expr, str], ...] = ()
    # For chain-rule decomposition specifically.
    inner: sp.Expr | None = None
    inner_deriv: sp.Expr | None = None
    # For `choice` instances.
    choices: tuple[Choice, ...] = ()
    correct_choice: str | None = None
    # Standing assumptions shown with the prompt, e.g. "assume x, y > 0".
    assumption: str = ""
    # Overrides the default prompt rendering.
    prompt_latex: str | None = None
    instruction: str | None = None
    # Distinguishes instances of the same template in problem ids.
    slug: str = ""


@dataclass(frozen=True)
class Template:
    id: str
    tier: Tier
    build: Callable[..., Instance]
    # Each entry is a kwargs dict passed to `build`.
    params: tuple[dict, ...] = ()
    # Variables in play, and the values they may be sampled at.
    variables: tuple[Variable, ...] = ONE_VAR
    # Which differentiation rule this family is *about*. Used to label
    # rule-recognition options; None outside those chapters.
    rule: str | None = None
    # Whether the answer is the derivative of the prompt rather than equal to it.
    # Separate from `rule` because chapters 7 and 8 differentiate without being
    # *about* a named rule, and validation needs to know which check applies:
    # `d/dx(expr) == answer` here, `expr == answer` for algebra.
    differentiates: bool = False
    # Whether the answer is an ANTIderivative of the prompt. Implies that the
    # answer is only defined up to an additive constant, so `solve_problem`
    # fingerprints it with `up_to_constant` and validation checks the answer by
    # differentiating it back rather than by integrating the prompt - SymPy's
    # integrator is far less reliable than its differentiator.
    integrates: bool = False
    supports_decompose: bool = False
    # A short description of the shape, for the Practice picker later.
    shape: str = ""
    # What this template drills, for diagnostic readouts.
    skill: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    # An extra invariant only this family can state, raising on violation.
    # Required for templates tagged `not-equal-to-prompt`, which opt out of the
    # generic numeric check and would otherwise ship unverified.
    verify: Callable[[Instance], None] | None = None

    @property
    def is_derivative(self) -> bool:
        """Whether the answer is d(prompt)/dx. `rule` implies it."""
        return self.differentiates or self.rule is not None

    def instances(self) -> list[Instance]:
        return [self.build(**p) for p in self.params]


def _fingerprint_set(
    answer: sp.Expr,
    distractors: Sequence[tuple[str, sp.Expr, str]],
    variables: tuple[Variable, ...],
    up_to_constant: bool = False,
) -> tuple[Fingerprint, tuple[Distractor, ...]]:
    """Fingerprint an answer and its distractors on one shared point set."""
    exprs = [answer, *(expr for _, expr, _ in distractors)]
    points = choose_points(exprs, variables)

    answer_fp = fingerprint_at(answer, variables, points, up_to_constant)
    built = tuple(
        Distractor(
            id=did,
            fingerprint=fingerprint_at(expr, variables, points, up_to_constant),
            feedback=feedback,
        )
        for did, expr, feedback in distractors
    )
    return answer_fp, built


def _var_names(variables: tuple[Variable, ...]) -> tuple[str, ...]:
    return tuple(variable.name for variable in variables)


def solve_problem(
    template: Template,
    inst: Instance,
    label: str = "answer",
    instruction: str = "Simplify as far as you can.",
    up_to_constant: bool | None = None,
) -> Problem:
    """A level where the learner types the answer.

    `up_to_constant` defaults to whether the template integrates: an
    antiderivative is only defined up to +C, so comparing absolute values would
    reject the perfectly correct `x^3/3 + 7`.
    """
    if inst.answer is None:
        raise ValueError(f"{template.id}/{inst.slug} has no answer to grade")

    if up_to_constant is None:
        up_to_constant = template.integrates

    answer_fp, distractors = _fingerprint_set(
        inst.answer, inst.distractors, template.variables, up_to_constant
    )
    return Problem(
        id=f"{template.id}--{inst.slug}--solve",
        template_id=template.id,
        tier=template.tier,
        instruction=inst.instruction or instruction,
        prompt_latex=inst.prompt_latex or to_katex(inst.expr),
        answers=(
            Answer(
                label=label,
                latex=to_katex(inst.answer),
                fingerprint=answer_fp,
                distractors=distractors,
            ),
        ),
        hints=inst.hints,
        steps=tuple(Step(latex=lx, note=note) for lx, note in inst.steps),
        variables=_var_names(template.variables),
        assumption=inst.assumption,
    )


def differentiate_problem(template: Template, inst: Instance) -> Problem:
    """A solve level whose prompt is `d/dx [...]`."""
    problem = solve_problem(
        template,
        inst,
        label="dy/dx",
        instruction="Differentiate with respect to x.",
    )
    return replace(
        problem,
        id=f"{template.id}--{inst.slug}--solve",
        prompt_latex=inst.prompt_latex or derivative_prompt(inst.expr),
    )


def slots_problem(
    template: Template,
    inst: Instance,
    instruction: str,
) -> Problem:
    """A level with several named answer slots, each graded independently.

    Used wherever the *form* of the answer matters and a single free-form
    expression could not distinguish it - "give a and b in (x+a)(x+b)" cannot be
    satisfied by handing back the unfactored quadratic.
    """
    if not inst.slots:
        raise ValueError(f"{template.id}/{inst.slug} has no slots")

    answers = []
    for label, expr, help_text in inst.slots:
        fingerprint, _ = _fingerprint_set(expr, (), template.variables)
        answers.append(
            Answer(
                label=label,
                latex=to_katex(expr),
                fingerprint=fingerprint,
                hint_text=help_text,
            )
        )

    return Problem(
        id=f"{template.id}--{inst.slug}--slots",
        template_id=template.id,
        tier=template.tier,
        instruction=inst.instruction or instruction,
        prompt_latex=inst.prompt_latex or to_katex(inst.expr),
        answers=tuple(answers),
        hints=inst.hints,
        steps=tuple(Step(latex=lx, note=note) for lx, note in inst.steps),
        variables=_var_names(template.variables),
        assumption=inst.assumption,
    )


def decompose_problem(template: Template, inst: Instance) -> Problem:
    """Name the inner function and its derivative.

    This is the skill the chain rule actually rests on - seeing the composition -
    so it gets its own level type rather than being folded into a solve.
    """
    if inst.inner is None or inst.inner_deriv is None:
        raise ValueError(f"{template.id}/{inst.slug} has no inner function")

    inner_fp, _ = _fingerprint_set(inst.inner, (), template.variables)
    deriv_fp, _ = _fingerprint_set(inst.inner_deriv, (), template.variables)

    return Problem(
        id=f"{template.id}--{inst.slug}--decompose",
        template_id=template.id,
        tier="easy",
        instruction=(
            "Write this as an outer function applied to an inner one. "
            "Give the inner function u, then du/dx."
        ),
        prompt_latex=to_katex(inst.expr),
        answers=(
            Answer(
                label="u",
                latex=to_katex(inst.inner),
                fingerprint=inner_fp,
                hint_text="in terms of x",
            ),
            Answer(
                label="du/dx",
                latex=to_katex(inst.inner_deriv),
                fingerprint=deriv_fp,
                hint_text="in terms of x",
            ),
        ),
        hints=(
            "Ask what you would have to compute *last* if you were evaluating "
            "this by hand for a specific x. That outermost operation is the "
            "outer function; everything inside it is u.",
            "The inner function is whatever sits inside the brackets, the "
            "exponent, or under the root.",
        ),
        variables=_var_names(template.variables),
    )


def choice_problem(
    template: Template,
    inst: Instance,
    instruction: str = "Pick one.",
    prompt_is_derivative: bool = False,
) -> Problem:
    """A level where the learner picks from options rather than typing.

    Used where an answer isn't an expression - which rule applies, what the
    domain is, which statement is true.
    """
    if not inst.choices or inst.correct_choice is None:
        raise ValueError(f"{template.id}/{inst.slug} is not a choice instance")

    prompt = inst.prompt_latex
    if prompt is None:
        prompt = (
            derivative_prompt(inst.expr)
            if prompt_is_derivative
            else to_katex(inst.expr)
        )

    return Problem(
        id=f"{template.id}--{inst.slug}--choice",
        template_id=template.id,
        tier=template.tier,
        instruction=inst.instruction or instruction,
        prompt_latex=prompt,
        choices=inst.choices,
        correct_choice=inst.correct_choice,
        hints=inst.hints,
        steps=tuple(Step(latex=lx, note=note) for lx, note in inst.steps),
        variables=_var_names(template.variables),
        assumption=inst.assumption,
    )


# ---------------------------------------------------------------------------
# Differentiation-rule recognition, the chapter 9 case of `choice`.
# ---------------------------------------------------------------------------

RULE_LABELS: dict[str, str] = {
    "chain": "Chain rule",
    "product": "Product rule",
    "quotient": "Quotient rule",
    "power": "Power rule",
}

# What each rule is *for*, phrased as a clause the UI drops into a sentence.
# Deliberately does NOT lead with the rule's own name: the interface supplies
# that, and having both produces "this is the chain rule: Chain rule: ...".
RULE_APPLIES_WHEN: dict[str, str] = {
    "chain": (
        "one function is applied to another, so you differentiate the outside "
        "and multiply by the derivative of the inside"
    ),
    "product": (
        "two independent factors are multiplied together, with neither one "
        "sitting inside the other"
    ),
    "quotient": (
        "one expression is divided by another and the denominator depends on x"
    ),
    "power": (
        "you have a sum of powers of x with nothing composed, multiplied or "
        "divided, so you differentiate term by term"
    ),
}

RECOGNIZE_OPTIONS: tuple[str, ...] = ("chain", "product", "quotient", "power")


def recognize_problem(template: Template, inst: Instance) -> Problem:
    """Which differentiation rule would you reach for first?

    Deliberately fast - this is the Sudoku Coach reflex, technique-spotting,
    and it is trained by volume rather than by depth.
    """
    if template.rule is None:
        raise ValueError(f"{template.id} has no rule to recognise")

    choices = tuple(
        Choice(
            id=rule,
            label=RULE_LABELS[rule],
            feedback=RULE_APPLIES_WHEN[rule],
        )
        for rule in RECOGNIZE_OPTIONS
    )

    return Problem(
        id=f"{template.id}--{inst.slug}--recognize",
        template_id=template.id,
        tier="easy",
        instruction="Which rule is the one you would reach for first?",
        prompt_latex=derivative_prompt(inst.expr),
        choices=choices,
        correct_choice=template.rule,
        hints=(
            "Don't differentiate it. Just look at how the expression is built: "
            "is something applied to something, multiplied by something, or "
            "divided by something?",
        ),
        variables=_var_names(template.variables),
    )
