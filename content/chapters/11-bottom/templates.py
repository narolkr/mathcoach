"""Chapter 11 - Finding the Bottom: critical points, convexity, optimisation.

This is gradient descent in one dimension. Everything about learning rates,
local minima, saddle points and why convex problems are "easy" starts here, and
once you see that *training a model* means *find the minimum of a loss
function*, this chapter is the whole idea.

Critical points are asked for as slots - the x-values, smallest first - because
"solve f'(x) = 0" has a set as its answer, not an expression. Classification and
convexity are choices, for the same reason.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import coeff, num, power, to_katex
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _cubic_latex(a: int, b: int, c: int, d: int) -> str:
    parts = [coeff(a, power("x", 3))]
    for value, symbol in ((b, power("x", 2)), (c, "x"), (d, "")):
        if value == 0:
            continue
        body = coeff(abs(value), symbol) if symbol else num(abs(value))
        parts.append(f"{'+' if value > 0 else '-'} {body}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Finding critical points
# ---------------------------------------------------------------------------


def cubic_critical_points(a: int, b: int, c: int, d: int) -> Instance:
    """Critical points of a·x³ + b·x² + c·x + d, chosen to have two real ones."""
    f = a * x**3 + b * x**2 + c * x + d
    derivative = 3 * a * x**2 + 2 * b * x + c

    roots = sorted(sp.solve(sp.Eq(derivative, 0), x))
    if len(roots) != 2 or any(not root.is_real for root in roots):
        raise ValueError(
            f"cubic_critical_points({a},{b},{c},{d}): needs two distinct real "
            f"critical points, got {roots}"
        )
    smaller, larger = roots

    return Instance(
        expr=f,
        answer=None,
        prompt_latex=f"f(x) = {_cubic_latex(a, b, c, d)}",
        slug=f"a{a}b{b}c{c}d{d}".replace("-", "m"),
        instruction="Find both critical points. Smaller x first.",
        slots=(
            ("smaller x", smaller, "a number"),
            ("larger x", larger, "a number"),
        ),
        hints=(
            "A critical point is where the slope is zero. So differentiate, then "
            "solve.",
            f"f'(x) = {_m(derivative)}. Set that equal to zero.",
            "It's a quadratic, so factor it or use the formula.",
        ),
        steps=(
            (
                to_katex(derivative) + " = 0",
                "Critical points are where the derivative vanishes.",
            ),
            (
                f"x = {to_katex(smaller)} \\quad\\text{{or}}\\quad x = "
                f"{to_katex(larger)}",
                "Two solutions, so two critical points - a cubic has a local "
                "maximum and a local minimum whenever its derivative has two "
                "real roots.",
            ),
        ),
    )


def classify_critical_point(a: int, b: int, c: int, d: int, which: str) -> Instance:
    """Second-derivative test at one of a cubic's two critical points."""
    f = a * x**3 + b * x**2 + c * x + d
    derivative = 3 * a * x**2 + 2 * b * x + c
    second = 6 * a * x + 2 * b

    roots = sorted(sp.solve(sp.Eq(derivative, 0), x))
    if len(roots) != 2:
        raise ValueError("classify_critical_point needs two critical points")
    point = roots[0] if which == "smaller" else roots[1]
    curvature = second.subs(x, point)
    if curvature == 0:
        raise ValueError("classify_critical_point: second derivative vanishes")

    is_min = curvature > 0
    correct = "min" if is_min else "max"

    choices = (
        Choice(
            id="min",
            label=r"\text{local minimum}",
            is_latex=True,
            feedback=(
                f"f''({to_katex(point)}) = {to_katex(curvature)}, which is "
                f"{'positive' if is_min else 'negative'}. Positive curvature "
                f"means the graph bends upwards, so a point with zero slope "
                f"there sits at the bottom of a bowl."
            ),
        ),
        Choice(
            id="max",
            label=r"\text{local maximum}",
            is_latex=True,
            feedback=(
                f"f''({to_katex(point)}) = {to_katex(curvature)}, which is "
                f"{'positive' if is_min else 'negative'}. Negative curvature "
                f"means the graph bends downwards, so zero slope puts you at the "
                f"top of a hill."
            ),
        ),
        Choice(
            id="inflection",
            label=r"\text{a point of inflection}",
            is_latex=True,
            feedback=(
                f"That would need f'' = 0 there. Here f'' = "
                f"{to_katex(curvature)}, which is not zero, so the curvature has "
                f"a definite sign and the test is decisive."
            ),
        ),
        Choice(
            id="global",
            label=r"\text{the global minimum}",
            is_latex=True,
            feedback=(
                "A cubic has no global minimum at all - it runs to −∞ in one "
                "direction. The second-derivative test is inherently local: it "
                "sees the neighbourhood and nothing beyond it. That limitation "
                "is exactly why non-convex optimisation is hard."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=(
            f"f(x) = {_cubic_latex(a, b, c, d)} \\qquad x = {to_katex(point)}"
        ),
        choices=choices,
        correct_choice=correct,
        slug=f"a{a}b{b}c{c}d{d}{which}".replace("-", "m"),
        instruction="The slope is zero here. What kind of point is it?",
        hints=(
            "The first derivative tells you the slope is zero. The second tells "
            "you which way the curve bends.",
            f"f''(x) = {_m(second)}. Evaluate it at x = {_m(point)} and look at "
            "the sign.",
        ),
        steps=(
            (
                to_katex(second),
                "The second derivative measures curvature.",
            ),
            (
                f"f''({to_katex(point)}) = {to_katex(curvature)}",
                f"{'Positive' if is_min else 'Negative'}, so the curve bends "
                f"{'upwards' if is_min else 'downwards'} - a local "
                f"{'minimum' if is_min else 'maximum'}.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Convexity - the property that makes optimisation tractable
# ---------------------------------------------------------------------------


def convexity_question(kind: str) -> Instance:
    """Why one minimum, and what convexity buys you."""
    if kind == "one-minimum":
        prompt = r"f''(x) > 0 \text{ for all } x"
        correct = "unique"
        options = (
            Choice(
                id="unique",
                label=r"\text{at most one minimum, and it is global}",
                is_latex=True,
                feedback=(
                    "Positive curvature everywhere means the slope f' is "
                    "strictly increasing, so it can cross zero at most once. "
                    "One crossing, one minimum - and with nothing to bend the "
                    "curve back down, that minimum is global. This is why convex "
                    "problems are the easy case: gradient descent cannot get "
                    "stuck anywhere else, because there is nowhere else."
                ),
            ),
            Choice(
                id="many",
                label=r"\text{possibly many local minima}",
                is_latex=True,
                feedback=(
                    "Several minima would need the slope to cross zero upwards "
                    "more than once, which means decreasing in between - and that "
                    "needs f'' < 0 somewhere. Ruled out by the assumption."
                ),
            ),
            Choice(
                id="none",
                label=r"\text{no minimum at all}",
                is_latex=True,
                feedback=(
                    "Possible in principle - e^x is convex and never reaches a "
                    "minimum - which is why the careful statement is *at most* "
                    "one rather than exactly one."
                ),
            ),
            Choice(
                id="saddle",
                label=r"\text{a saddle point}",
                is_latex=True,
                feedback=(
                    "Saddles need curvature of different signs in different "
                    "directions, so they cannot occur in one variable at all. "
                    "They arrive in chapter 20, with the Hessian - and they are "
                    "the characteristic obstacle in high-dimensional "
                    "optimisation."
                ),
            ),
        )
        hints = (
            "f'' > 0 everywhere says something about f'. What?",
            "If f'' > 0 then f' is strictly increasing. How many times can a "
            "strictly increasing function cross zero?",
        )
        steps = (
            (
                r"f'' > 0 \implies f' \text{ strictly increasing}",
                "So f' crosses zero at most once, and there is at most one "
                "stationary point - necessarily a minimum.",
            ),
        )
    else:
        prompt = r"\text{gradient descent: } x \leftarrow x - \eta\,f'(x)"
        correct = "overshoot"
        options = (
            Choice(
                id="overshoot",
                label=r"\text{too large an } \eta \text{ overshoots and diverges}",
                is_latex=True,
                feedback=(
                    "Each step moves against the slope by η times its size. If η "
                    "is larger than the curvature can absorb - roughly η > 2/f'' "
                    "near the minimum - each step lands further out than the last "
                    "and the iteration flies apart. Too small and it converges, "
                    "just slowly. The curvature f'' is what sets the safe range, "
                    "which is why second-order information is so valuable."
                ),
            ),
            Choice(
                id="always",
                label=r"\text{any } \eta > 0 \text{ converges eventually}",
                is_latex=True,
                feedback=(
                    "Not so. Try f(x) = x² with η = 2: from x = 1 you get "
                    "1 → −1 → 1 → −1, oscillating forever. Larger η diverges "
                    "outright."
                ),
            ),
            Choice(
                id="sign",
                label=r"\text{the sign of } \eta \text{ is irrelevant}",
                is_latex=True,
                feedback=(
                    "Very much not: a negative η would step *along* the gradient "
                    "rather than against it, climbing the loss instead of "
                    "descending it."
                ),
            ),
            Choice(
                id="zero",
                label=r"\text{it stops only when } f'(x) = 0",
                is_latex=True,
                feedback=(
                    "True but not the interesting part - and it is exactly why "
                    "the algorithm halts at *any* stationary point, including a "
                    "local maximum or a saddle, not only at a minimum."
                ),
            ),
        )
        hints = (
            "Think about f(x) = x² and a large step size. What happens from "
            "x = 1?",
            "With η = 2 the step is exactly 2x, so x → x − 2x = −x. It "
            "oscillates and never settles.",
        )
        steps = (
            (
                r"x_{n+1} = x_n - \eta f'(x_n)",
                "For f = x², f' = 2x, so x_{n+1} = (1 − 2η)x_n. That shrinks "
                "only when |1 − 2η| < 1, which means 0 < η < 1. Outside that "
                "range it grows without bound.",
            ),
        )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=prompt,
        choices=options,
        correct_choice=correct,
        slug=kind,
        instruction="Which of these follows?",
        hints=hints,
        steps=steps,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="fb-critical-points",
        tier="medium",
        variables=VARS,
        shape="critical points of a cubic",
        skill="solving f'(x) = 0",
        tags=("not-equal-to-prompt", "unordered-slots"),
        verify=lambda inst: _verify_critical(inst),
        build=cubic_critical_points,
        params=(
            # The roadmap's gate: x³ - 3x² + 4.
            {"a": 1, "b": -3, "c": 0, "d": 4},
            {"a": 1, "b": 0, "c": -12, "d": 1},
            {"a": 2, "b": 3, "c": -12, "d": 0},
        ),
    ),
    Template(
        id="fb-classify",
        tier="medium",
        variables=VARS,
        shape="second-derivative test",
        skill="classifying a critical point by curvature",
        build=classify_critical_point,
        params=(
            {"a": 1, "b": -3, "c": 0, "d": 4, "which": "smaller"},
            {"a": 1, "b": -3, "c": 0, "d": 4, "which": "larger"},
            {"a": 1, "b": 0, "c": -12, "d": 1, "which": "larger"},
        ),
    ),
    Template(
        id="fb-convexity",
        tier="hard",
        variables=VARS,
        shape="convexity and step size",
        skill="why convex problems are the easy case",
        build=convexity_question,
        params=({"kind": "one-minimum"}, {"kind": "step-size"}),
    ),
)


def _verify_critical(inst: Instance) -> None:
    """Every slot value is a genuine critical point, in the promised order."""
    derivative = sp.diff(inst.expr, x)
    for label, value, _ in inst.slots:
        residual = sp.simplify(derivative.subs(x, value))
        if residual != 0:
            raise ValueError(
                f"slot {label!r} = {value} is not a critical point: "
                f"f'({value}) = {residual}"
            )
    values = [sp.simplify(value) for _, value, _ in inst.slots]
    if len(values) == 2 and sp.N(values[0]) >= sp.N(values[1]):
        raise ValueError(f"slots out of order: {values}")
