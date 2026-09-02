"""Chapter 14 - Change of Costume: u-substitution.

Substitution is the chain rule read right to left. If chapter 9 is solid this
chapter is nearly free - and whether it feels free is a good check on whether
chapter 9 really stuck.

Antiderivatives here are graded `up_to_constant`.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign, positive
from mathcoach.latex import definite_integral_prompt, integral_prompt, num, to_katex

VARS = any_sign("x")
x = VARS[0].symbol

POSITIVE_X = positive("x")
x_pos = POSITIVE_X[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _check(F: sp.Expr, f: sp.Expr, where: str, var) -> None:
    residual = sp.simplify(sp.diff(F, var) - f)
    if residual != 0:
        raise ValueError(f"{where}: d/d{var}({F}) is not {f} (differs by {residual})")


def exp_of_square(a: int) -> Instance:
    """∫ 2a·x·e^(a·x²) dx - the pattern where du/dx is sitting right there."""
    inner = a * x**2
    integrand = 2 * a * x * sp.exp(inner)
    answer = sp.exp(inner)
    _check(answer, integrand, f"exp_of_square({a})", x)

    return Instance(
        expr=integrand,
        answer=answer,
        prompt_latex=integral_prompt(integrand),
        slug=f"a{a}".replace("-", "m"),
        instruction="Find the antiderivative.",
        hints=(
            "Look for a function and its own derivative both present in the "
            "integrand. That's the signal for substitution.",
            f"Take u = {_m(inner)}. What is du/dx?",
            f"du/dx = {_m(sp.diff(inner, x))}, which is exactly the factor "
            "sitting outside the exponential. So the whole thing is ∫e^u du.",
        ),
        steps=(
            (
                f"u = {to_katex(inner)}, \\quad du = {to_katex(sp.diff(inner, x))}\\,dx",
                "The derivative of the inside is already a factor of the "
                "integrand - that is what makes substitution work here.",
            ),
            (r"\int e^{u}\,du", "The integral becomes trivial."),
            (to_katex(answer), "Substitute back."),
        ),
        distractors=(
            (
                "factor-by-factor",
                a * x**2 * sp.exp(inner),
                "You integrated the two factors separately and multiplied the "
                "results. Integration does not distribute over a product - that "
                "is exactly the gap substitution fills.",
            ),
        ),
    )


def log_of_polynomial(a: int, b: int) -> Instance:
    """∫ 2a·x/(a·x² + b) dx - substitution producing a logarithm."""
    if b <= 0 or a <= 0:
        raise ValueError("log_of_polynomial keeps the denominator positive")
    inner = a * x**2 + b
    integrand = 2 * a * x / inner
    answer = sp.log(inner)
    _check(answer, integrand, f"log_of_polynomial({a},{b})", x)

    return Instance(
        expr=integrand,
        answer=answer,
        prompt_latex=integral_prompt(integrand),
        slug=f"a{a}b{b}",
        instruction="Find the antiderivative.",
        hints=(
            "The numerator is suspiciously close to the derivative of the "
            "denominator. Check.",
            f"u = {_m(inner)} gives du/dx = {_m(sp.diff(inner, x))} - exactly "
            "the numerator.",
            "So the integral is ∫du/u, which is a logarithm.",
        ),
        steps=(
            (
                f"u = {to_katex(inner)}, \\quad du = {to_katex(sp.diff(inner, x))}\\,dx",
                "The numerator is du.",
            ),
            (r"\int \frac{du}{u}", "Which is chapter 12's logarithm case."),
            (to_katex(answer), "Substitute back."),
        ),
        distractors=(
            (
                "reciprocal-power",
                -2 * a * x / inner**2,
                "You differentiated instead of integrating. Integration of "
                "du/u gives a log, not a negative power.",
            ),
        ),
    )


def definite_with_substitution(a: int, lower: int, upper: int) -> Instance:
    """∫ from lower to upper of x/(x²+a) dx - bounds and all."""
    inner = x**2 + a
    integrand = x / inner
    antiderivative = sp.log(inner) / 2
    _check(antiderivative, integrand, f"definite_with_substitution({a})", x)

    answer = antiderivative.subs(x, upper) - antiderivative.subs(x, lower)
    from_sympy = sp.integrate(integrand, (x, lower, upper))
    if sp.simplify(answer - from_sympy) != 0:
        raise ValueError(
            f"definite_with_substitution({a},{lower},{upper}): {answer} vs "
            f"SymPy's {from_sympy}"
        )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=definite_integral_prompt(integrand, num(lower), num(upper)),
        slug=f"a{a}l{lower}u{upper}".replace("-", "m"),
        instruction="Evaluate exactly. Keep the logarithms.",
        hints=(
            f"Substitute u = {_m(inner)}. The numerator is half of du/dx, so "
            "you'll pick up a factor of one half.",
            "Either change the bounds to u-values, or substitute back to x "
            "before evaluating. Both work; pick one and be consistent.",
            f"The antiderivative is {_m(antiderivative)}. Now top minus bottom.",
        ),
        steps=(
            (
                to_katex(antiderivative),
                "Substitution gives a half times a logarithm - the half because "
                "the numerator is x, not 2x.",
            ),
            (to_katex(answer), "Evaluate at both bounds and subtract."),
        ),
        distractors=(
            (
                "forgot-half",
                sp.log(inner).subs(x, upper) - sp.log(inner).subs(x, lower),
                "You dropped the factor of one half. du = 2x·dx, but the "
                "numerator is only x, so the integral is half of ∫du/u.",
            ),
        ),
    )


TEMPLATES: tuple[Template, ...] = (
    Template(
        id="cc-exp",
        tier="medium",
        variables=VARS,
        integrates=True,
        shape="∫ 2ax·e^(ax²) dx",
        skill="substitution where du/dx is already a factor",
        build=exp_of_square,
        params=({"a": 1}, {"a": 3}, {"a": 2}),
    ),
    Template(
        id="cc-log",
        tier="medium",
        variables=VARS,
        integrates=True,
        shape="∫ 2ax/(ax²+b) dx",
        skill="substitution producing a logarithm",
        build=log_of_polynomial,
        params=({"a": 1, "b": 1}, {"a": 3, "b": 1}, {"a": 2, "b": 4}),
    ),
    Template(
        id="cc-definite",
        tier="hard",
        variables=VARS,
        shape="definite integral needing substitution",
        skill="substitution with bounds",
        build=definite_with_substitution,
        params=(
            {"a": 1, "lower": 0, "upper": 1},
            {"a": 4, "lower": 0, "upper": 2},
            {"a": 1, "lower": 1, "upper": 3},
        ),
    ),
)
