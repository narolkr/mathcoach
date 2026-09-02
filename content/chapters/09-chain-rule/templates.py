"""Chain rule problem templates.

Chapter 9 is the deliberate stress test for the whole engine: it needs rule
recognition, decomposition, free-form grading, and - the reason it was chosen -
the richest set of real misconceptions in beginner calculus. Every distractor
below is a mistake people actually make, not a random wrong expression.

Answers are written out longhand rather than taken from `sp.diff`, so that
`validate.check_answer_is_correct` is a genuine independent check on the maths
here rather than a tautology.

Prose fields (hints, step notes) carry inline math wrapped in `$...$`; the
frontend renders those with KaTeX. Always build them with `_m()` rather than
`sp.latex()`, so natural log renders as \\ln rather than \\log.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import X, Instance, Template
from mathcoach.latex import to_katex


def _m(expr: sp.Expr) -> str:
    """Inline math for prose fields."""
    return f"${to_katex(expr)}$"


# ---------------------------------------------------------------------------
# Chain rule families
# ---------------------------------------------------------------------------


def sin_of_polynomial(a: int, b: int, n: int) -> Instance:
    """sin(a·xⁿ + b) - trig outside, polynomial inside."""
    inner = a * X**n + b
    inner_deriv = a * n * X ** (n - 1)
    expr = sp.sin(inner)
    answer = inner_deriv * sp.cos(inner)
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"a{a}b{b}n{n}".replace("-", "m"),
        distractors=(
            (
                "forgot-inner",
                sp.cos(inner),
                "You differentiated the outer sine into a cosine correctly, but "
                "never multiplied by the derivative of what's inside it. The "
                "chain rule has two factors; you wrote one.",
            ),
            (
                "inner-only",
                inner_deriv,
                "That's the derivative of the inside only. The outer sine hasn't "
                "been differentiated at all - you need a cosine factor as well.",
            ),
            (
                "added-not-multiplied",
                sp.cos(inner) + inner_deriv,
                "Both pieces are right, but the chain rule multiplies them. "
                "You added them.",
            ),
        ),
        hints=(
            "This is one function applied to another. Which operation would you "
            "perform last if you were evaluating it for a specific x?",
            "Outer function: sine. Inner function: the polynomial inside it.",
            f"{_m(sp.Eq(sp.Derivative(sp.sin(u), X), sp.cos(u) * sp.Derivative(u, X), evaluate=False))} "
            "- write down u and du/dx separately before you combine them.",
            f"{_m(sp.Eq(u, inner, evaluate=False))}, so "
            f"{_m(sp.Eq(sp.Derivative(u, X), inner_deriv, evaluate=False))}. "
            "Now multiply the cosine by that.",
        ),
        steps=(
            (
                to_katex(sp.sin(u)),
                f"Name the inner function: {_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (
                r"\cos(u) \cdot \frac{du}{dx}",
                "Differentiate the outside, then multiply by the derivative of "
                "the inside.",
            ),
            (
                to_katex(answer),
                f"Substitute {_m(sp.Eq(sp.Derivative(u, X), inner_deriv, evaluate=False))} "
                "and u back in.",
            ),
        ),
    )


def exp_of_polynomial(a: int, b: int, n: int) -> Instance:
    """e^(a·xⁿ + b) - the shape that shows up everywhere in softmax."""
    inner = a * X**n + b
    inner_deriv = a * n * X ** (n - 1)
    expr = sp.exp(inner)
    answer = inner_deriv * sp.exp(inner)
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"a{a}b{b}n{n}".replace("-", "m"),
        distractors=(
            (
                "forgot-inner",
                sp.exp(inner),
                "e^u is its own derivative, which is why this one is tempting - "
                "but only with respect to u. Differentiating with respect to x "
                "still costs you a factor of du/dx.",
            ),
            (
                "inner-only",
                inner_deriv,
                "That's du/dx alone. The exponential factor is still part of the "
                "answer.",
            ),
        ),
        hints=(
            "The exponent is not just x, so this is a composition.",
            f"{_m(sp.Eq(sp.Derivative(sp.exp(u), X), sp.exp(u) * sp.Derivative(u, X), evaluate=False))} "
            "- the exponential survives untouched; the chain rule contributes "
            "the extra factor.",
            f"{_m(sp.Eq(u, inner, evaluate=False))}, "
            f"{_m(sp.Eq(sp.Derivative(u, X), inner_deriv, evaluate=False))}.",
        ),
        steps=(
            (
                to_katex(sp.exp(u)),
                f"{_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (r"e^{u} \cdot \frac{du}{dx}", "The outer derivative of e^u is e^u."),
            (to_katex(answer), "Substitute back."),
        ),
    )


def log_of_polynomial(a: int, b: int, n: int) -> Instance:
    """ln(a·xⁿ + b), with a, b > 0 and n even so the argument is always positive."""
    inner = a * X**n + b
    inner_deriv = a * n * X ** (n - 1)
    expr = sp.log(inner)
    answer = inner_deriv / inner
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"a{a}b{b}n{n}",
        distractors=(
            (
                "forgot-inner",
                1 / inner,
                "You used d(ln u)/du = 1/u, which is right, but stopped there. "
                "The derivative of the inside still has to multiply it.",
            ),
            (
                "inner-only",
                inner_deriv,
                "That's the derivative of the inside only - the logarithm has "
                "vanished from your answer entirely.",
            ),
            (
                "reciprocal-of-x",
                inner_deriv / X,
                "The 1/u in d(ln u)/du means one over the whole inner function, "
                "not one over x.",
            ),
        ),
        hints=(
            "The logarithm is applied to something more complicated than x.",
            f"{_m(sp.Eq(sp.Derivative(sp.log(u), X), sp.Derivative(u, X) / u, evaluate=False))}.",
            f"{_m(sp.Eq(u, inner, evaluate=False))}, "
            f"{_m(sp.Eq(sp.Derivative(u, X), inner_deriv, evaluate=False))}. "
            "The answer is a single fraction.",
        ),
        steps=(
            (
                to_katex(sp.log(u)),
                f"{_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (
                r"\frac{1}{u} \cdot \frac{du}{dx}",
                "The outer derivative of a natural log is one over its argument.",
            ),
            (to_katex(answer), "Substitute back and write as one fraction."),
        ),
    )


def power_of_linear(a: int, b: int, n: int) -> Instance:
    """(a·x + b)ⁿ - where dropping the inner coefficient is near-universal."""
    inner = a * X + b
    inner_deriv = sp.Integer(a)
    expr = inner**n
    answer = n * a * inner ** (n - 1)
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"a{a}b{b}n{n}".replace("-", "m"),
        distractors=(
            (
                "forgot-coefficient",
                n * inner ** (n - 1),
                f"The exponent came down correctly, but the inside is "
                f"{to_katex(inner)}, not x - so du/dx is {a}, and your answer is "
                f"missing that factor of {a}. This is the single most common "
                f"chain rule slip.",
            ),
            (
                "exponent-unchanged",
                n * a * inner**n,
                "You remembered the factor from the inside but left the exponent "
                "alone. Bringing the power down also reduces it by one.",
            ),
        ),
        hints=(
            "You could expand this, but there's a much faster route.",
            "Treat the bracket as a single object u and apply the power rule to "
            "u to the n, then the chain rule.",
            f"{_m(sp.Eq(sp.Derivative(u**n, X), n * u ** (n - 1) * sp.Derivative(u, X), evaluate=False))} "
            "- what is du/dx when u is linear?",
            f"{_m(sp.Eq(u, inner, evaluate=False))}, so du/dx is the constant "
            f"{a}. Multiply by it.",
        ),
        steps=(
            (
                to_katex(u**n),
                f"{_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (
                r"n u^{n-1} \cdot \frac{du}{dx}",
                "Power rule outside, chain rule to finish.",
            ),
            (
                to_katex(answer),
                f"du/dx is {a}, so the whole thing scales by {a}.",
            ),
        ),
    )


def power_of_trig(a: int, n: int, trig: str) -> Instance:
    """sinⁿ(a·x) or cosⁿ(a·x) - two nested compositions, not one."""
    fn = sp.sin if trig == "sin" else sp.cos
    inner = fn(a * X)
    # d/dx sin(ax) = a·cos(ax);  d/dx cos(ax) = -a·sin(ax)
    inner_deriv = a * sp.cos(a * X) if trig == "sin" else -a * sp.sin(a * X)
    # The same derivative with the inner coefficient dropped - a distinct mistake.
    inner_deriv_no_coeff = sp.cos(a * X) if trig == "sin" else -sp.sin(a * X)

    expr = inner**n
    answer = n * inner ** (n - 1) * inner_deriv
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"{trig}a{a}n{n}",
        distractors=(
            (
                "forgot-argument-coefficient",
                n * inner ** (n - 1) * inner_deriv_no_coeff,
                f"You peeled the power and the {trig} correctly, but there is a "
                f"third layer: the {a}x inside. Its derivative contributes a "
                f"factor of {a}.",
            ),
            (
                "forgot-trig-derivative",
                n * inner ** (n - 1) * a,
                f"You handled the power and the {a}x, but skipped the middle "
                f"layer - the derivative of {trig} itself.",
            ),
            (
                "power-only",
                n * inner ** (n - 1),
                "Only the power rule was applied. There are two more layers "
                "inside, and each contributes a factor.",
            ),
        ),
        hints=(
            f"Read it as {_m(inner)} raised to the power {n}. How many layers "
            "deep does this go?",
            "Three layers: the power on the outside, the trig function, and the "
            "linear argument inside it. Each contributes one factor.",
            f"Start with {_m(sp.Eq(u, inner, evaluate=False))} and apply the "
            f"power rule to u to the {n}.",
            f"{_m(sp.Eq(sp.Derivative(u, X), inner_deriv, evaluate=False))} - "
            "and note that already needed the chain rule itself.",
        ),
        steps=(
            (
                to_katex(u**n),
                f"{_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (
                r"n u^{n-1} \cdot \frac{du}{dx}",
                "Power rule on the outermost layer.",
            ),
            (
                to_katex(inner_deriv),
                f"du/dx needs the chain rule too: differentiate {_m(inner)}.",
            ),
            (to_katex(answer), "Multiply the layers together."),
        ),
    )


def sin_of_log(a: int, b: int) -> Instance:
    """sin(ln(a·x² + b)) - the roadmap's chapter 9 gate problem. Three layers."""
    innermost = a * X**2 + b
    innermost_deriv = 2 * a * X
    inner = sp.log(innermost)
    inner_deriv = innermost_deriv / innermost
    expr = sp.sin(inner)
    answer = sp.cos(inner) * inner_deriv
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"a{a}b{b}",
        distractors=(
            (
                "outermost-only",
                sp.cos(inner),
                "Only the outermost sine was differentiated. There are two more "
                "layers below it, and each one contributes a factor.",
            ),
            (
                "stopped-at-log",
                sp.cos(inner) / innermost,
                "You peeled the sine and the logarithm, then stopped. The "
                "polynomial inside the log still has to be differentiated - "
                "three layers means three factors.",
            ),
            (
                "skipped-log-derivative",
                sp.cos(inner) * innermost_deriv,
                "You differentiated the sine and the polynomial but jumped over "
                "the logarithm in between. The 1/u from the log is missing.",
            ),
        ),
        hints=(
            "Don't try to do this in one move. How many functions are nested "
            "here?",
            "Three: sine, then natural log, then a quadratic. Peel one at a "
            "time from the outside in.",
            f"{_m(sp.Eq(sp.Derivative(sp.sin(u), X), sp.cos(u) * sp.Derivative(u, X), evaluate=False))} "
            f"with {_m(sp.Eq(u, inner, evaluate=False))}. Now you need du/dx, "
            "which is its own chain rule problem.",
            f"{_m(sp.Eq(sp.Derivative(u, X), inner_deriv, evaluate=False))}. "
            "Multiply that by the cosine.",
        ),
        steps=(
            (
                to_katex(sp.sin(u)),
                f"Outermost layer: {_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (r"\cos(u) \cdot \frac{du}{dx}", "Differentiate the sine."),
            (
                to_katex(inner_deriv),
                f"Now du/dx, itself a chain rule: differentiate {_m(inner)}.",
            ),
            (to_katex(answer), "Combine all three layers."),
        ),
    )


def exp_of_trig_squared(a: int) -> Instance:
    """e^(cos²(a·x)) - the roadmap's second gate problem. Four layers, one sign trap."""
    trig = sp.cos(a * X)
    inner = trig**2
    inner_deriv = 2 * trig * (-a * sp.sin(a * X))
    expr = sp.exp(inner)
    answer = sp.exp(inner) * inner_deriv
    u = sp.Symbol("u")

    return Instance(
        expr=expr,
        answer=answer,
        inner=inner,
        inner_deriv=inner_deriv,
        slug=f"a{a}",
        distractors=(
            (
                "sign-error",
                sp.exp(inner) * 2 * trig * a * sp.sin(a * X),
                "The structure is exactly right and every factor is present - "
                "but the derivative of cosine is minus sine. Your answer has "
                "the wrong overall sign.",
            ),
            (
                "forgot-trig-derivative",
                sp.exp(inner) * 2 * trig * a,
                "You got the exponential, the square and the inner coefficient, "
                "but skipped the derivative of cosine itself.",
            ),
            (
                "missing-exponential",
                inner_deriv,
                "That's the derivative of the exponent alone. e^u differentiates "
                "to e^u times du/dx, so the exponential factor stays.",
            ),
            (
                "outermost-only",
                sp.exp(inner),
                "Only the exponential was differentiated - and since e^u is its "
                "own derivative, that means nothing happened at all.",
            ),
        ),
        hints=(
            "Count the layers before you write anything.",
            "Four: the exponential, the square, the cosine, and the inner "
            "multiple of x. Every layer contributes exactly one factor.",
            f"Start from the outside: "
            f"{_m(sp.Eq(sp.Derivative(sp.exp(u), X), sp.exp(u) * sp.Derivative(u, X), evaluate=False))} "
            f"with {_m(sp.Eq(u, inner, evaluate=False))}.",
            "Now du/dx is itself a power-of-trig problem. Watch the sign when "
            "you differentiate the cosine.",
        ),
        steps=(
            (
                to_katex(sp.exp(u)),
                f"Outermost: {_m(sp.Eq(u, inner, evaluate=False))}.",
            ),
            (r"e^{u} \cdot \frac{du}{dx}", "The exponential survives unchanged."),
            (
                to_katex(inner_deriv),
                "du/dx: power rule, then cosine (picking up a minus), then the "
                "inner coefficient.",
            ),
            (to_katex(answer), "Combine. Note the overall sign is negative."),
        ),
    )


# ---------------------------------------------------------------------------
# Foils: not chain rule. Used only in `recognize` levels, so the learner has to
# actually discriminate rather than answering "chain" every time. There are
# roughly as many foils as recognisable chain items, on purpose.
# ---------------------------------------------------------------------------


def foil_product(a: int, n: int, kind: str) -> Instance:
    """Two independent factors, neither one inside the other."""
    if kind == "log":
        second, second_deriv = sp.log(X), 1 / X
    elif kind == "exp":
        second, second_deriv = sp.exp(X), sp.exp(X)
    else:
        second, second_deriv = sp.sin(X), sp.cos(X)

    first = a * X**n
    first_deriv = a * n * X ** (n - 1)
    expr = first * second
    answer = first_deriv * second + first * second_deriv
    return Instance(expr=expr, answer=answer, slug=f"a{a}n{n}{kind}")


def foil_quotient(a: int, b: int, c: int) -> Instance:
    """(a·x + b)/(x² + c) - a genuine quotient."""
    num = a * X + b
    den = X**2 + c
    expr = num / den
    answer = (a * den - num * 2 * X) / den**2
    return Instance(expr=expr, answer=answer, slug=f"a{a}b{b}c{c}".replace("-", "m"))


def foil_plain_power(a: int, n: int, b: int, m: int) -> Instance:
    """a·xⁿ + b·xᵐ - nothing composed, multiplied or divided."""
    expr = a * X**n + b * X**m
    answer = a * n * X ** (n - 1) + b * m * X ** (m - 1)
    return Instance(expr=expr, answer=answer, slug=f"a{a}n{n}b{b}m{m}".replace("-", "m"))


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

CHAIN_TEMPLATES: tuple[Template, ...] = (
    Template(
        id="chain-sin-poly",
        rule="chain",
        tier="easy",
        shape="sin(a·xⁿ + b)",
        skill="chain rule: trig outside a polynomial",
        supports_decompose=True,
        build=sin_of_polynomial,
        params=(
            {"a": 3, "b": 1, "n": 2},
            {"a": 2, "b": -1, "n": 3},
            {"a": 5, "b": 4, "n": 2},
        ),
    ),
    Template(
        id="chain-exp-poly",
        rule="chain",
        tier="easy",
        shape="e^(a·xⁿ + b)",
        skill="chain rule: exponential of a polynomial",
        supports_decompose=True,
        build=exp_of_polynomial,
        params=(
            {"a": 2, "b": 1, "n": 2},
            {"a": 1, "b": -1, "n": 3},
        ),
    ),
    Template(
        id="chain-log-poly",
        rule="chain",
        tier="medium",
        shape="ln(a·xⁿ + b)",
        skill="chain rule: log of a polynomial",
        supports_decompose=True,
        build=log_of_polynomial,
        params=(
            {"a": 3, "b": 1, "n": 2},
            {"a": 2, "b": 4, "n": 2},
        ),
    ),
    Template(
        id="chain-power-linear",
        rule="chain",
        tier="easy",
        shape="(a·x + b)ⁿ",
        skill="chain rule: power of a linear expression",
        supports_decompose=True,
        build=power_of_linear,
        params=(
            {"a": 3, "b": 1, "n": 4},
            {"a": 2, "b": -1, "n": 5},
            {"a": 5, "b": 2, "n": 3},
        ),
    ),
    Template(
        id="chain-power-trig",
        rule="chain",
        tier="medium",
        shape="sinⁿ(a·x), cosⁿ(a·x)",
        skill="chain rule: two nested layers inside a power",
        supports_decompose=True,
        build=power_of_trig,
        params=(
            {"a": 2, "n": 2, "trig": "cos"},
            {"a": 3, "n": 2, "trig": "sin"},
            {"a": 2, "n": 3, "trig": "sin"},
        ),
    ),
    Template(
        id="chain-sin-log",
        rule="chain",
        tier="hard",
        shape="sin(ln(a·x² + b))",
        skill="chain rule: three nested layers",
        supports_decompose=True,
        build=sin_of_log,
        params=(
            {"a": 3, "b": 1},
            {"a": 2, "b": 4},
        ),
    ),
    Template(
        id="chain-exp-cos-squared",
        rule="chain",
        tier="hard",
        shape="e^(cos²(a·x))",
        skill="chain rule: four nested layers, with a sign trap",
        supports_decompose=True,
        build=exp_of_trig_squared,
        params=(
            {"a": 2},
            {"a": 3},
        ),
    ),
)

FOIL_TEMPLATES: tuple[Template, ...] = (
    Template(
        id="foil-product",
        rule="product",
        tier="easy",
        shape="a·xⁿ · g(x)",
        skill="spotting a product rather than a composition",
        build=foil_product,
        params=(
            {"a": 1, "n": 3, "kind": "log"},
            {"a": 2, "n": 2, "kind": "exp"},
            {"a": 1, "n": 2, "kind": "sin"},
            {"a": 3, "n": 1, "kind": "log"},
        ),
    ),
    Template(
        id="foil-quotient",
        rule="quotient",
        tier="easy",
        shape="(a·x + b)/(x² + c)",
        skill="spotting a quotient rather than a composition",
        build=foil_quotient,
        params=(
            {"a": 2, "b": 1, "c": 3},
            {"a": 1, "b": -4, "c": 1},
            {"a": 3, "b": 2, "c": 5},
        ),
    ),
    Template(
        id="foil-plain-power",
        rule="power",
        tier="easy",
        shape="a·xⁿ + b·xᵐ",
        skill="spotting a plain sum of powers",
        build=foil_plain_power,
        params=(
            {"a": 4, "n": 3, "b": -2, "m": 2},
            {"a": 1, "n": 5, "b": 3, "m": 1},
            {"a": 2, "n": 4, "b": -5, "m": 3},
        ),
    ),
)

ALL_TEMPLATES: tuple[Template, ...] = CHAIN_TEMPLATES + FOIL_TEMPLATES
