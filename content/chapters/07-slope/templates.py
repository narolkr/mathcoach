"""Chapter 7 - The Slope of a Curve: what a derivative actually is.

One template family here is not a drill but a rehearsal for Act V. The
finite-difference derivative

    f'(x) ~ (f(x+h) - f(x-h)) / 2h

is exactly the gradient check that verifies the hand-derived backpropagation in
the roadmap's final boss. Meeting it now, as arithmetic, means it is already
familiar when it becomes the thing that proves your calculus is right.

Free-form grading is safe throughout: the prompt is f(x) or a difference
quotient, and the answer is f'(x) or a number - never the prompt itself.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import (
    coeff,
    difference_quotient,
    frac,
    num,
    paren,
    power,
    to_katex,
)
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol
h = sp.Symbol("h", real=True)


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


# ---------------------------------------------------------------------------
# From the definition
# ---------------------------------------------------------------------------


def from_first_principles(a: int, b: int, c: int) -> Instance:
    """Differentiate a·x² + b·x + c from the difference quotient."""
    f = a * x**2 + b * x + c
    answer = 2 * a * x + b
    # Independent check: the quotient really does have this limit.
    quotient = (f.subs(x, x + h) - f) / h
    actual = sp.limit(sp.simplify(quotient), h, 0)
    if sp.simplify(actual - answer) != 0:
        raise ValueError(
            f"from_first_principles({a},{b},{c}): quotient limit is {actual}, "
            f"not {answer}"
        )

    expanded = sp.expand(f.subs(x, x + h) - f)

    return Instance(
        expr=f,
        answer=answer,
        prompt_latex=(
            f"f(x) = {to_katex(f)} \\qquad " + difference_quotient("f")
        ),
        slug=f"a{a}b{b}c{c}".replace("-", "m"),
        instruction="Work out f'(x) from the definition, not from the rules.",
        hints=(
            "Write out f(x+h) in full first. Everywhere the formula has an x, "
            "put (x+h) - brackets included.",
            f"f(x+h) = {_m(sp.expand(f.subs(x, x + h)))}. Now subtract f(x).",
            f"The difference is {_m(expanded)}. Notice every term has an h in it "
            f"- that is what makes the division survive.",
            f"Divide by h to get {_m(sp.simplify(quotient))}, then let h go to 0.",
        ),
        steps=(
            (
                to_katex(sp.expand(f.subs(x, x + h))),
                "Substitute x+h into the whole formula.",
            ),
            (
                to_katex(expanded),
                f"Subtract f(x). The constant {c} cancels, and so does the x² "
                f"term's leading part - only h-containing terms survive.",
            ),
            (
                to_katex(sp.simplify(quotient)),
                "Divide by h. This is the only step that needed the algebra: "
                "before dividing you had 0/0, after dividing you have a "
                "polynomial.",
            ),
            (to_katex(answer), "Now let h go to 0."),
        ),
        # No "you forgot the limit" distractor, tempting though it is: that
        # answer still contains h, and h is not one of this problem's declared
        # variables, so it could not be fingerprinted. The point is made in the
        # third worked step instead.
        distractors=(
            (
                "power-not-reduced",
                a * x**2 + b,
                "You differentiated the x² term as if the power stayed. "
                "Expanding (x+h)² gives x² + 2xh + h², so after subtracting "
                "and dividing the surviving term is 2ax, not ax².",
            ),
        ),
    )


def numeric_derivative(a: int, b: int, at: int, exponent: int) -> Instance:
    """The central difference (f(x+h) - f(x-h)) / 2h - the Act V gradient check."""
    f = a * x**exponent + b * x
    answer = sp.diff(f, x).subs(x, at)

    step = sp.Rational(1, 1000)
    approx = (f.subs(x, at + step) - f.subs(x, at - step)) / (2 * step)

    # An independent check on the symbolic answer, by the same finite-difference
    # method the roadmap's final boss uses on backpropagation. For a polynomial
    # the central difference is exact up to the h² term, so agreement should be
    # tight; a real disagreement would mean SymPy and arithmetic differ, which
    # would be worth knowing about.
    error = abs(float(approx - answer))
    if error > 1e-3:
        raise ValueError(
            f"numeric_derivative({a},{b},at={at},n={exponent}): exact answer "
            f"{answer} disagrees with the central difference {float(approx)} "
            f"by {error}"
        )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=(
            f"f(x) = {to_katex(f)} \\qquad f'({num(at)}) = ?"
        ),
        slug=f"a{a}b{b}at{at}n{exponent}".replace("-", "m"),
        instruction=f"Give f'({at}) exactly.",
        hints=(
            "You can do this from the rules, but check it the other way too: "
            "compute the slope over a tiny interval either side of the point.",
            r"$\frac{f(x+h) - f(x-h)}{2h}$ with h = 0.001 should land very close "
            "to the exact answer.",
            f"With h = 0.001 the central difference gives "
            f"{float(approx):.6f}, which tells you the exact answer is "
            f"{_m(answer)}.",
        ),
        steps=(
            (
                to_katex(sp.diff(f, x)),
                "Differentiate, then substitute.",
            ),
            (
                to_katex(answer),
                f"And the numeric check: the central difference at h = 0.001 "
                f"gives {float(approx):.6f}. Agreement to several decimal places "
                f"is how you catch your own algebra errors - and in Act V it is "
                f"how you will verify backpropagation.",
            ),
        ),
    )


def meaning_of_the_number(a: int, at: int) -> Instance:
    """What f'(at) *means*, as opposed to how to compute it."""
    f = a * x**2
    slope = sp.diff(f, x).subs(x, at)

    choices = (
        Choice(
            id="rate",
            label=(
                f"the instantaneous rate at which f changes as x passes {at}"
            ),
            feedback=(
                f"Nudge x a tiny amount past {at} and f changes about {slope} "
                f"times as much. This is the reading that matters for machine "
                f"learning: the gradient says how much the loss moves when you "
                f"nudge a weight."
            ),
        ),
        Choice(
            id="value",
            label=f"the value of f at x = {at}",
            feedback=(
                f"That is f({at}) = {f.subs(x, at)}, a different number. The "
                f"derivative is about *change*, not position."
            ),
        ),
        Choice(
            id="average",
            label=f"the average slope of f between 0 and {at}",
            feedback=(
                "That's a secant slope over an interval. The derivative is the "
                "limit as the interval shrinks to nothing - a property of the "
                "single point."
            ),
        ),
        Choice(
            id="area",
            label=f"the area under f up to x = {at}",
            feedback=(
                "That's an integral, which is Act III. Derivatives and integrals "
                "are inverse operations, so it's a reasonable thing to confuse - "
                "but they answer opposite questions."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=f"f(x) = {to_katex(f)} \\qquad f'({num(at)}) = {to_katex(slope)}",
        choices=choices,
        correct_choice="rate",
        slug=f"a{a}at{at}".replace("-", "m"),
        instruction=f"What does the number {slope} actually tell you?",
        hints=(
            "Not how to compute it - what it means. If you nudged x slightly, "
            "what would this number predict?",
        ),
        steps=(
            (
                r"f(x + \varepsilon) \approx f(x) + f'(x)\,\varepsilon",
                "The derivative is the multiplier that turns a small change in x "
                "into the resulting change in f. That is the whole idea, and it "
                "is what gradient descent exploits.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="sc-first-principles",
        tier="medium",
        variables=VARS,
        differentiates=True,
        shape="a·x² + b·x + c from the definition",
        skill="differentiating from the difference quotient",
        build=from_first_principles,
        params=(
            {"a": 1, "b": 0, "c": 0},
            {"a": 3, "b": -2, "c": 5},
            {"a": -2, "b": 4, "c": -1},
        ),
    ),
    Template(
        id="sc-numeric",
        tier="easy",
        variables=VARS,
        shape="f'(a) exactly, checked numerically",
        skill="the central difference, and checking your own work",
        build=numeric_derivative,
        params=(
            {"a": 1, "b": 0, "at": 3, "exponent": 2},
            {"a": 2, "b": -3, "at": 2, "exponent": 3},
            {"a": -1, "b": 5, "at": -2, "exponent": 2},
        ),
    ),
    Template(
        id="sc-meaning",
        tier="easy",
        variables=VARS,
        shape="what f'(a) means",
        skill="reading a derivative as a rate of change",
        build=meaning_of_the_number,
        params=({"a": 1, "at": 3}, {"a": 2, "at": -1}),
    ),
)
