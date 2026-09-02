"""Chapter 15 - Trading Places: integration by parts.

The product rule read right to left, and the last general technique in the
roadmap. Everything is graded `up_to_constant`.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign, positive
from mathcoach.latex import integral_prompt, num, to_katex

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


def x_times_log(n: int) -> Instance:
    """∫ xⁿ·ln x dx - the case where you differentiate the log, not the power."""
    integrand = x_pos**n * sp.log(x_pos)
    answer = (
        x_pos ** (n + 1) * sp.log(x_pos) / (n + 1)
        - x_pos ** (n + 1) / (n + 1) ** 2
    )
    _check(answer, integrand, f"x_times_log({n})", x_pos)

    return Instance(
        expr=integrand,
        answer=answer,
        assumption="Assume x > 0.",
        prompt_latex=integral_prompt(integrand),
        slug=f"n{n}",
        instruction="Find the antiderivative.",
        hints=(
            "Two factors, and neither is the derivative of the other - so "
            "substitution won't help. This is by parts.",
            "You get to choose which factor to differentiate. Differentiate the "
            "logarithm: it becomes 1/x, which is simpler. Differentiating the "
            "power instead leaves you with the log still there.",
            f"u = ln x, dv = {_m(x_pos**n)}dx. Then du = dx/x and "
            f"v = {_m(x_pos ** (n + 1) / (n + 1))}.",
            "The remaining ∫v·du is a plain power, because the 1/x cancels one "
            "power of x.",
        ),
        steps=(
            (
                r"uv - \int v\,du",
                f"u = ln x, v = {_m(x_pos ** (n + 1) / (n + 1))}.",
            ),
            (
                f"{to_katex(x_pos ** (n + 1) * sp.log(x_pos) / (n + 1))} - "
                f"\\int {to_katex(x_pos**n / (n + 1))}\\,dx",
                "The 1/x from du cancels a power of x, leaving something "
                "elementary. That simplification is the whole reason for "
                "choosing u this way round.",
            ),
            (to_katex(answer), "Integrate the remaining power."),
        ),
        distractors=(
            (
                "product-of-integrals",
                x_pos ** (n + 1) / (n + 1) * sp.log(x_pos),
                "That's the first term only - uv, without subtracting ∫v du. By "
                "parts always leaves an integral behind, and here it contributes "
                "a second term.",
            ),
        ),
    )


def x_times_exp(n: int) -> Instance:
    """∫ xⁿ·e^x dx - by parts, applied n times."""
    if not 1 <= n <= 3:
        raise ValueError("x_times_exp handles n from 1 to 3")
    integrand = x**n * sp.exp(x)
    # Repeated by parts: sum_{k=0}^{n} (-1)^k n!/(n-k)! x^(n-k) e^x
    answer = sum(
        (-1) ** k * sp.factorial(n) / sp.factorial(n - k) * x ** (n - k) * sp.exp(x)
        for k in range(n + 1)
    )
    answer = sp.simplify(answer)
    _check(answer, integrand, f"x_times_exp({n})", x)

    return Instance(
        expr=integrand,
        answer=answer,
        prompt_latex=integral_prompt(integrand),
        slug=f"n{n}",
        instruction="Find the antiderivative.",
        hints=(
            "By parts. Which factor should you differentiate?",
            "Differentiate the power: it drops by one each time, and eventually "
            "reaches a constant. The exponential never gets simpler, so "
            "differentiating it would get you nowhere.",
            f"You'll need to apply by parts {n} time{'s' if n > 1 else ''} - each "
            "pass reduces the power by one.",
        ),
        steps=(
            (
                r"x^{n}e^{x} - n\int x^{n-1}e^{x}\,dx",
                "u = xⁿ, dv = e^x dx. The power drops by one.",
            ),
            (
                to_katex(answer),
                f"Repeat until the power is gone. Note the alternating signs - "
                f"each pass contributes another minus.",
            ),
        ),
        distractors=(
            (
                "single-pass",
                x**n * sp.exp(x) - n * x ** (n - 1) * sp.exp(x)
                if n >= 2
                else x * sp.exp(x),
                "You stopped after one pass. The remaining integral still has a "
                "power of x in it, so by parts has to be applied again.",
            ),
        )
        if n >= 2
        else (),
    )


TEMPLATES: tuple[Template, ...] = (
    Template(
        id="tp-log",
        tier="medium",
        variables=POSITIVE_X,
        integrates=True,
        shape="∫ xⁿ·ln x dx",
        skill="by parts, differentiating the logarithm",
        build=x_times_log,
        params=({"n": 1}, {"n": 2}, {"n": 3}),
    ),
    Template(
        id="tp-exp",
        tier="hard",
        variables=VARS,
        integrates=True,
        shape="∫ xⁿ·e^x dx",
        skill="by parts, applied repeatedly",
        build=x_times_exp,
        params=({"n": 1}, {"n": 2}, {"n": 3}),
    ),
)
