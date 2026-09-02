"""Chapter 13 - The Bridge: the Fundamental Theorem of Calculus.

Definite integrals evaluate to numbers, and free-form grading is safe: the
prompt is an integral with bounds, not an expression, so there is nothing to
paste back.

The theorem itself is a choice question, because "what does the FTC say" has no
expression as an answer - and because being able to state it is the chapter gate.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import (
    definite_integral_prompt,
    evaluated_at,
    num,
    to_katex,
)
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def definite_polynomial(a: int, n: int, lower: int, upper: int) -> Instance:
    """Evaluate the integral of a·xⁿ between two bounds."""
    if n == -1:
        raise ValueError("definite_polynomial cannot take n = -1")
    integrand = a * x**n
    antiderivative = sp.Rational(a, n + 1) * x ** (n + 1)

    # Independent check on the antiderivative, then evaluate it.
    if sp.simplify(sp.diff(antiderivative, x) - integrand) != 0:
        raise ValueError(f"definite_polynomial({a},{n}): antiderivative is wrong")

    answer = antiderivative.subs(x, upper) - antiderivative.subs(x, lower)

    # And an independent check on the number, by SymPy's own integrator.
    from_sympy = sp.integrate(integrand, (x, lower, upper))
    if sp.simplify(answer - from_sympy) != 0:
        raise ValueError(
            f"definite_polynomial({a},{n},{lower},{upper}): got {answer}, "
            f"SymPy says {from_sympy}"
        )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=definite_integral_prompt(integrand, num(lower), num(upper)),
        slug=f"a{a}n{n}l{lower}u{upper}".replace("-", "m"),
        instruction="Evaluate. Exact answer.",
        hints=(
            "Find an antiderivative first, then use the Fundamental Theorem: "
            "top minus bottom.",
            f"An antiderivative is {_m(antiderivative)}.",
            f"Now evaluate it at {upper} and subtract its value at {lower}. Note "
            "that the +C would cancel in the subtraction, which is why definite "
            "integrals don't need one.",
        ),
        steps=(
            (
                evaluated_at(to_katex(antiderivative), num(lower), num(upper)),
                "Any antiderivative will do - the constant cancels when you "
                "subtract.",
            ),
            (
                f"{to_katex(antiderivative.subs(x, upper))} - "
                f"{to_katex(antiderivative.subs(x, lower))}",
                "Top minus bottom, in that order.",
            ),
            (to_katex(answer), "Evaluate."),
        ),
        distractors=_definite_distractors(integrand, answer, lower, upper),
    )


def _definite_distractors(
    integrand: sp.Expr, answer: sp.Expr, lower: int, upper: int
) -> tuple[tuple[str, sp.Expr, str], ...]:
    """The misconceptions, minus any that collide with the answer.

    `no-antiderivative` collides for a·x² from 0 to 3, where both the correct
    value and the naive one come to 9 - a coincidence of the bounds rather than
    anything meaningful, so it is filtered rather than designed around.
    """
    candidates = (
        (
            "backwards",
            -answer,
            "You subtracted the other way round. It's F(upper) − F(lower): "
            "swapping the bounds negates a definite integral.",
        ),
        (
            "no-antiderivative",
            integrand.subs(x, upper) - integrand.subs(x, lower),
            "You evaluated the integrand at the bounds rather than its "
            "antiderivative. The FTC needs F, not f.",
        ),
    )
    return tuple(
        candidate
        for candidate in candidates
        if sp.simplify(candidate[1] - answer) != 0
    )


def ftc_statement(part: str) -> Instance:
    """What the two parts of the theorem actually say."""
    if part == "evaluation":
        prompt = r"\int_{a}^{b} f(x)\,dx = ?"
        correct = "difference"
        options = (
            Choice(
                id="difference",
                label=r"F(b) - F(a) \text{ where } F' = f",
                is_latex=True,
                feedback=(
                    "This is what makes integration computable at all. Instead "
                    "of adding up infinitely many infinitesimal slices, you find "
                    "one antiderivative and subtract two numbers. The whole of "
                    "Act III depends on it."
                ),
            ),
            Choice(
                id="sum",
                label=r"F(b) + F(a) \text{ where } F' = f",
                is_latex=True,
                feedback=(
                    "Minus, not plus. Think of F as an accumulated total: the "
                    "amount accumulated between a and b is the total at b less "
                    "the total already there at a."
                ),
            ),
            Choice(
                id="derivative",
                label=r"f'(b) - f'(a)",
                is_latex=True,
                feedback=(
                    "That differentiates when it should antidifferentiate. "
                    "Integration undoes differentiation, so you need the "
                    "function whose derivative is f."
                ),
            ),
            Choice(
                id="average",
                label=r"\frac{f(a) + f(b)}{2}(b-a)",
                is_latex=True,
                feedback=(
                    "That is the trapezoidal *approximation* - a genuinely "
                    "useful numerical method, and exact only when f is linear. "
                    "The FTC is exact for everything."
                ),
            ),
        )
        hints = (
            "You need a function whose derivative is f. Then what do you do "
            "with it?",
        )
        steps = (
            (
                r"\int_{a}^{b} f = F(b) - F(a)",
                "Find one antiderivative, evaluate at both ends, subtract. The "
                "constant of integration cancels, which is why definite "
                "integrals never carry a +C.",
            ),
        )
    else:
        prompt = r"\frac{d}{dx}\int_{a}^{x} f(t)\,dt = ?"
        correct = "f-of-x"
        options = (
            Choice(
                id="f-of-x",
                label="f(x)",
                is_latex=True,
                feedback=(
                    "Differentiation and integration are exact inverses. "
                    "Accumulate f up to x, then ask how fast that total grows as "
                    "x moves - and the answer is however big f is right there. "
                    "This is the half of the theorem that says the two "
                    "operations undo each other."
                ),
            ),
            Choice(
                id="f-prime",
                label="f'(x)",
                is_latex=True,
                feedback=(
                    "That differentiates twice over. The integral already "
                    "antidifferentiated once, so the d/dx brings you back to f "
                    "itself, not past it."
                ),
            ),
            Choice(
                id="f-diff",
                label="f(x) - f(a)",
                is_latex=True,
                feedback=(
                    "The a-dependence disappears when you differentiate: the "
                    "lower bound contributes a constant, and constants "
                    "differentiate to zero."
                ),
            ),
            Choice(
                id="zero",
                label="0",
                is_latex=True,
                feedback=(
                    "The integral is a function of x - the upper bound moves - "
                    "so it is not constant and its derivative is not zero."
                ),
            ),
        )
        hints = (
            "The integral depends on x through its upper bound. What does "
            "nudging x do to the accumulated total?",
            "Extending the upper limit by a sliver adds an area of roughly "
            "f(x)·dx. Divide by dx.",
        )
        steps = (
            (
                r"\frac{d}{dx}\int_{a}^{x} f(t)\,dt = f(x)",
                "The two operations are exact inverses. This is why "
                "antiderivatives are the right tool for areas at all - a fact "
                "that is not obvious and took a long time to discover.",
            ),
        )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=prompt,
        choices=options,
        correct_choice=correct,
        slug=part,
        instruction="Which is it?",
        hints=hints,
        steps=steps,
    )


TEMPLATES: tuple[Template, ...] = (
    Template(
        id="br-definite",
        tier="easy",
        variables=VARS,
        shape="definite integral of a·xⁿ",
        skill="evaluating a definite integral by the FTC",
        build=definite_polynomial,
        params=(
            {"a": 1, "n": 2, "lower": 0, "upper": 3},
            {"a": 3, "n": 1, "lower": 1, "upper": 4},
            {"a": 2, "n": 3, "lower": -1, "upper": 2},
            {"a": 1, "n": -2, "lower": 1, "upper": 2},
        ),
    ),
    Template(
        id="br-statement",
        tier="medium",
        variables=VARS,
        shape="the two parts of the FTC",
        skill="stating the Fundamental Theorem",
        build=ftc_statement,
        params=({"part": "evaluation"}, {"part": "derivative"}),
    ),
)
