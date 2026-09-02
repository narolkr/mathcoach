"""Chapter 12 - Running the Tape Backwards: antiderivatives.

The first chapter to use `up_to_constant` fingerprints, built and tested in
Phase 1 and unused until now. An antiderivative is only defined up to an
additive constant, so the grader compares *differences* between sample points
rather than absolute values - which means `x^3/3`, `x^3/3 + 7` and
`x^3/3 + C` all grade correct, exactly as they should.

That is not laxity. It is the mathematically correct notion of equality for this
question, and getting it wrong in either direction would be a real error:
rejecting `+7` would be wrong, and accepting `x^3/3 + x` would be worse.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign, positive
from mathcoach.latex import coeff, integral_prompt, num, power, root, to_katex

VARS = any_sign("x")
x = VARS[0].symbol

POSITIVE_X = positive("x")
x_pos = POSITIVE_X[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _check_antiderivative(F: sp.Expr, f: sp.Expr, where: str, var=None) -> None:
    """d/dx of the stated antiderivative really is the integrand.

    The independent check for this whole chapter: differentiation is easy and
    unambiguous, so verifying an antiderivative by differentiating it back is
    both cheap and complete.
    """
    variable = var if var is not None else x
    residual = sp.simplify(sp.diff(F, variable) - f)
    if residual != 0:
        raise ValueError(
            f"{where}: d/dx({F}) = {sp.simplify(sp.diff(F, variable))}, not {f} "
            f"(differs by {residual})"
        )


# ---------------------------------------------------------------------------
# The power rule, backwards
# ---------------------------------------------------------------------------


def reverse_power(a: int, n: int) -> Instance:
    """a·xⁿ integrated. n != -1, which is the case that breaks the pattern."""
    if n == -1:
        raise ValueError("reverse_power cannot handle n = -1; use log_case instead")
    integrand = a * x**n
    answer = sp.Rational(a, n + 1) * x ** (n + 1)
    _check_antiderivative(answer, integrand, f"reverse_power({a},{n})")

    return Instance(
        expr=integrand,
        answer=answer,
        prompt_latex=integral_prompt(integrand),
        slug=f"a{a}n{n}".replace("-", "m"),
        instruction="Find the antiderivative. You may write + C or leave it off.",
        hints=(
            "Run the power rule backwards. Differentiating multiplies by the "
            "power and reduces it, so integrating must do the opposite.",
            "Raise the exponent by one, then divide by the new exponent.",
            f"The exponent becomes {n + 1}, so you divide by {n + 1}.",
        ),
        steps=(
            (
                to_katex(answer),
                f"Exponent up by one to {n + 1}, then divide by {n + 1}. Check "
                f"it by differentiating back - that is always available and "
                f"always decisive.",
            ),
        ),
        distractors=(
            (
                "differentiated-instead",
                a * n * x ** (n - 1),
                "You differentiated. Integration goes the other way: exponent "
                "up, then divide.",
            ),
            (
                "forgot-to-divide",
                a * x ** (n + 1),
                "You raised the exponent but didn't divide by the new one. "
                "Differentiate your answer back and you'll see the extra factor "
                f"of {n + 1}.",
            ),
        ),
    )


def log_case(a: int) -> Instance:
    """a/x - the one case the power rule cannot do."""
    integrand = a / x_pos
    answer = a * sp.log(x_pos)
    _check_antiderivative(answer, integrand, f"log_case({a})", var=x_pos)

    return Instance(
        expr=integrand,
        answer=answer,
        prompt_latex=integral_prompt(integrand),
        assumption="Assume x > 0, so |x| is just x.",
        slug=f"a{a}".replace("-", "m"),
        instruction="Find the antiderivative.",
        hints=(
            "Try the power rule on x⁻¹ and see what goes wrong.",
            "Raising −1 by one gives 0, and you would be dividing by zero. So "
            "the power rule genuinely cannot do this case.",
            "Which function has derivative 1/x? You learned it in chapter 8.",
        ),
        steps=(
            (
                to_katex(answer),
                "This is the single exception to the power rule, and the reason "
                "is dividing by zero rather than anything deep. For all real x "
                "it's a·ln|x|; here x > 0 so the bars are unnecessary.",
            ),
        ),
        distractors=(
            # ln(ax) = ln a + ln x, which differs from a·ln x by a constant -
            # and constants are exactly what `up_to_constant` grading ignores.
            # So for a != 1 it differs in the coefficient, which the grader does
            # see; at a = 1 the two are identical and it must be dropped.
            *(
                (
                    (
                        "coefficient-inside",
                        sp.log(a * x_pos) if a > 0 else sp.log(-a * x_pos),
                        f"You put the {a} inside the logarithm. ln({a}x) is "
                        f"ln {a} + ln x - the coefficient becomes an additive "
                        f"constant, not a multiplier. What you want is "
                        f"{a}·ln x.",
                    ),
                )
                if abs(a) != 1
                else ()
            ),
            (
                "differentiated-instead",
                -a / x_pos**2,
                "That's the derivative of a/x, not its antiderivative. You went "
                "the wrong way.",
            ),
        ),
    )


def reverse_standard(which: str) -> Instance:
    """The antiderivatives that just reverse chapter 8's four facts."""
    table = {
        "exp": (sp.exp(x), sp.exp(x)),
        "sin": (sp.sin(x), -sp.cos(x)),
        "cos": (sp.cos(x), sp.sin(x)),
        "reciprocal-square": (1 / (1 + x**2), sp.atan(x)),
    }
    integrand, answer = table[which]
    _check_antiderivative(answer, integrand, f"reverse_standard({which})")

    notes = {
        "exp": "e^x is its own antiderivative as well as its own derivative.",
        "sin": (
            "The minus sign MOVES. Differentiating cos gives −sin, so "
            "integrating sin must give −cos. Half of all sign errors in Act III "
            "are this."
        ),
        "cos": "Integrating cos gives +sin, with no sign change.",
        "reciprocal-square": (
            "This one is worth recognising on sight: 1/(1+x²) integrates to "
            "arctan. It looks like it should need work and doesn't."
        ),
    }

    return Instance(
        expr=integrand,
        answer=answer,
        prompt_latex=integral_prompt(integrand),
        slug=which,
        instruction="Find the antiderivative.",
        hints=(
            "Which function differentiates to this? That question is the whole "
            "of integration.",
            "Chapter 8 gave you four derivatives. Read the table backwards.",
        ),
        steps=((to_katex(answer), notes[which]),),
        distractors=(
            (
                "sign-flipped",
                -answer,
                "Right function, wrong sign. Differentiate your answer back and "
                "compare it with the integrand - that check catches every sign "
                "error you will ever make here.",
            ),
        )
        if which in {"sin", "cos"}
        else (),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="rt-power",
        tier="easy",
        variables=VARS,
        integrates=True,
        shape="a·xⁿ",
        skill="the power rule in reverse",
        build=reverse_power,
        params=(
            {"a": 1, "n": 3},
            {"a": 6, "n": 2},
            {"a": 2, "n": -3},
            {"a": -4, "n": 5},
        ),
    ),
    Template(
        id="rt-log",
        tier="medium",
        variables=POSITIVE_X,
        integrates=True,
        shape="a/x",
        skill="the one case the power rule cannot do",
        build=log_case,
        params=({"a": 1}, {"a": 5}, {"a": -2}),
    ),
    Template(
        id="rt-standard",
        tier="easy",
        variables=VARS,
        integrates=True,
        shape="e^x, sin x, cos x, 1/(1+x²)",
        skill="reading the derivative table backwards",
        build=reverse_standard,
        params=(
            {"which": "exp"},
            {"which": "sin"},
            {"which": "cos"},
            {"which": "reciprocal-square"},
        ),
    ),
)
