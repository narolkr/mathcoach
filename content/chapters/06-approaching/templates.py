"""Chapter 6 - Approaching Without Arriving: limits and continuity.

Deliberately light. Limits are the *logical* foundation of calculus but rarely
the practical one, and beginners routinely burn a month on epsilon-delta and
quit before reaching derivatives. The roadmap says get the intuition, get the
mechanics, move on.

Grading shapes:

- A limit that **exists and is finite** is graded free-form. That is safe here
  even though the answer is a number: the prompt is a limit, not an expression,
  so there is nothing to paste back. Typing the function itself gives its value
  at the sample points, not its limit, and fails.
- A limit that is **infinite or doesn't exist** goes to multiple choice, because
  neither is a number you can type.
- Continuity questions are choices: "is it continuous" is not an expression.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import (
    coeff,
    frac,
    limit_prompt,
    num,
    paren,
    power,
    to_katex,
)
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _assert_limit(function: sp.Expr, point, expected: sp.Expr, where: str) -> None:
    """Independently confirm the stated limit with SymPy.

    These templates set `expr = answer` (a constant), which makes the generic
    answer-equals-prompt check vacuous: it compares the answer to itself. So the
    real invariant - that the number really is the limit of the function - has
    to be asserted here, or a wrong limit would ship unnoticed.
    """
    actual = sp.limit(function, x, point)
    if sp.simplify(actual - expected) != 0:
        raise ValueError(
            f"{where}: stated limit {expected} is wrong; SymPy says {actual} "
            f"for {function} as x -> {point}"
        )


# ---------------------------------------------------------------------------
# Limits that exist: free-form
# ---------------------------------------------------------------------------


def removable_discontinuity(root: int, other: int) -> Instance:
    """(x²-(r+o)x+ro)/(x-r) as x -> r. The factor cancels; the limit exists.

    The archetypal 0/0: substitution gives nonsense, factoring gives the answer.
    """
    numerator = (x - root) * (x - other)
    denominator = x - root
    expr = numerator / denominator
    answer = sp.Integer(root - other)
    _assert_limit(expr, root, answer, f"removable_discontinuity(r={root}, o={other})")

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=(
            r"\lim_{x \to " + num(root) + "} "
            + frac(to_katex(sp.expand(numerator)), to_katex(denominator))
        ),
        slug=f"r{root}o{other}".replace("-", "m"),
        instruction="Evaluate the limit.",
        hints=(
            f"Substituting x = {root} gives 0/0, which tells you nothing yet - "
            "not that the limit fails, only that substitution won't find it.",
            "Factor the top. Something will cancel with the bottom.",
            f"The numerator factors as {_m(sp.factor(sp.expand(numerator)))}, so "
            f"the {_m(denominator)} cancels.",
            f"That leaves {_m(x - other)}, and *now* substitution works.",
        ),
        steps=(
            (
                frac(to_katex(sp.factor(sp.expand(numerator))), to_katex(denominator)),
                "Factor the numerator.",
            ),
            (
                to_katex(x - other),
                f"Cancel. This is not the same function - it differs at "
                f"x = {root} - but it has the same limit, which is all we need.",
            ),
            (to_katex(answer), f"Now substitute x = {root}."),
        ),
        distractors=(
            (
                "substituted-too-early",
                sp.Integer(0),
                "Substituting straight away gives 0/0, and reading that as 0 is "
                "the mistake. An indeterminate form is a signal to do more work, "
                "not an answer.",
            ),
        ),
    )


def rational_at_infinity(a: int, b: int, c: int, d: int) -> Instance:
    """(a·x² + b·x)/(c·x² + d) as x -> infinity. Ratio of leading coefficients."""
    numerator = a * x**2 + b * x
    denominator = c * x**2 + d
    answer = sp.Rational(a, c)
    _assert_limit(
        numerator / denominator, sp.oo, answer, f"rational_at_infinity({a},{b},{c},{d})"
    )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=(
            r"\lim_{x \to \infty} "
            + frac(to_katex(numerator), to_katex(denominator))
        ),
        slug=f"a{a}b{b}c{c}d{d}".replace("-", "m"),
        instruction="Evaluate the limit.",
        hints=(
            "As x grows, which term in each of the top and bottom actually "
            "matters?",
            "Divide every term by the highest power of x present - here x².",
            f"You get ({a} + {b}/x)/({c} + {d}/x²). Every 1/x term goes to zero.",
        ),
        steps=(
            (
                frac(
                    f"{num(a)} + {frac(num(b), 'x')}",
                    f"{num(c)} + {frac(num(d), power('x', 2))}",
                ),
                "Divide top and bottom by x².",
            ),
            (
                to_katex(answer),
                "Every 1/x term vanishes, leaving the ratio of the leading "
                "coefficients.",
            ),
        ),
        distractors=(
            (
                "constants-ratio",
                sp.Rational(b, d) if d != 0 else sp.Integer(0),
                "You used the lower-order terms. At infinity the *highest* power "
                "dominates and everything else becomes negligible.",
            ),
        ),
    )


def sinc_limit(k: int) -> Instance:
    """sin(kx)/x as x -> 0. Chapter 5's fact, doing work."""
    expr = sp.sin(k * x) / x
    answer = sp.Integer(k)
    _assert_limit(expr, 0, answer, f"sinc_limit(k={k})")

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=limit_prompt(expr, "x", "0"),
        slug=f"k{k}".replace("-", "m"),
        instruction="Evaluate the limit.",
        hints=(
            "You met the k = 1 case in chapter 5. What was it?",
            "sin(u)/u goes to 1 as u goes to 0. Can you make the inside and the "
            "denominator match?",
            f"Write it as {k} · sin({k}x)/({k}x). The fraction goes to 1, so the "
            f"limit is {k}.",
        ),
        steps=(
            (
                f"{num(k)} \\cdot " + frac(to_katex(sp.sin(k * x)), to_katex(k * x)),
                f"Multiply and divide by {k} so the argument matches the "
                f"denominator.",
            ),
            (to_katex(answer), "The fraction tends to 1."),
        ),
        distractors=(
            # Only when there IS a scaling to forget: at k = 1 this distractor
            # would BE the correct answer, and the build rightly refuses that.
            *(
                (
                    (
                        "forgot-scaling",
                        sp.Integer(1),
                        f"That's the answer for sin(x)/x. Here the argument is "
                        f"{k}x, and matching it to the denominator costs a "
                        f"factor of {k}.",
                    ),
                )
                if k != 1
                else ()
            ),
            (
                "substituted-zero",
                sp.Integer(0),
                "Substituting gives 0/0 - indeterminate, not zero. It means the "
                "answer depends on how fast each part approaches zero.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Limits that don't exist, or are infinite: choices
# ---------------------------------------------------------------------------


def one_sided_limit(root: int) -> Instance:
    """1/(x-r) approached from each side, and what that means for the limit."""
    expr = 1 / (x - root)

    choices = (
        Choice(
            id="dne",
            label=r"\text{does not exist}",
            is_latex=True,
            feedback=(
                f"From above, x − {root} is a small positive number, so the "
                f"fraction goes to +∞. From below it is small and negative, so "
                f"the fraction goes to −∞. The two sides disagree, so there is "
                f"no two-sided limit."
            ),
        ),
        Choice(
            id="plus-infinity",
            label=r"+\infty",
            is_latex=True,
            feedback=(
                "That is the limit from *above* only. Approaching from below "
                f"makes x − {root} negative, and the fraction goes to −∞ "
                "instead."
            ),
        ),
        Choice(
            id="minus-infinity",
            label=r"-\infty",
            is_latex=True,
            feedback=(
                "That is the limit from *below* only. The two one-sided limits "
                "have to agree for a two-sided limit to exist."
            ),
        ),
        Choice(
            id="zero",
            label="0",
            is_latex=True,
            feedback=(
                "The denominator is heading to zero, not the fraction. A small "
                "denominator makes the fraction large, not small."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=limit_prompt(expr, "x", num(root)),
        choices=choices,
        correct_choice="dne",
        slug=f"r{root}".replace("-", "m"),
        instruction="What is this limit?",
        hints=(
            f"Try approaching {root} from just above, then from just below. Do "
            "you get the same thing?",
            "A two-sided limit exists only when both one-sided limits exist and "
            "agree.",
        ),
        steps=(
            (
                r"\lim_{x \to " + num(root) + r"^{+}} " + to_katex(expr) + r" = +\infty",
                f"From above, x − {root} is small and positive.",
            ),
            (
                r"\lim_{x \to " + num(root) + r"^{-}} " + to_katex(expr) + r" = -\infty",
                f"From below, it is small and negative.",
            ),
            (
                r"\text{no two-sided limit}",
                "They disagree, so the two-sided limit does not exist.",
            ),
        ),
    )


def continuity_check(kind: str) -> Instance:
    """Is a piecewise function continuous at the join? Three failure modes."""
    if kind == "jump":
        # Written as prose rather than a `cases` environment: `cases` builds on
        # `array`, which latex.py forbids because KaTeX handles it inconsistently.
        prompt = (
            r"f(x) = x + 1 \text{ for } x < 2, \quad f(x) = x + 3 \text{ for } x \ge 2"
        )
        correct = "no-jump"
        detail = (
            "Approaching 2 from below gives 3; from above it gives 5. The "
            "one-sided limits disagree, so there is a jump and f is not "
            "continuous there."
        )
    elif kind == "removable":
        prompt = (
            r"f(x) = \frac{x^{2} - 4}{x - 2} \text{ for } x \ne 2, "
            r"\quad f(2) = 4"
        )
        correct = "yes"
        detail = (
            "The limit as x → 2 is 4, and f(2) is defined as 4. Limit and value "
            "agree, so f is continuous - the hole has been filled correctly."
        )
    else:  # value mismatch
        prompt = (
            r"f(x) = \frac{x^{2} - 9}{x - 3} \text{ for } x \ne 3, "
            r"\quad f(3) = 5"
        )
        correct = "no-value"
        detail = (
            "The limit as x → 3 is 6, but f(3) was defined as 5. The limit "
            "exists and the value exists - they simply don't match, which is "
            "still a failure of continuity."
        )

    choices = (
        Choice(
            id="yes",
            label=r"\text{continuous}",
            is_latex=True,
            feedback=(
                detail
                if correct == "yes"
                else "Continuity needs three things at once: the limit exists, "
                "the value exists, and they are equal. One of those fails here."
            ),
        ),
        Choice(
            id="no-jump",
            label=r"\text{not continuous - the one-sided limits disagree}",
            is_latex=True,
            feedback=(
                detail
                if correct == "no-jump"
                else "The one-sided limits do agree here, so whatever is wrong "
                "is not a jump."
            ),
        ),
        Choice(
            id="no-value",
            label=r"\text{not continuous - the limit and the value differ}",
            is_latex=True,
            feedback=(
                detail
                if correct == "no-value"
                else "The limit and the assigned value are not the problem here."
            ),
        ),
        Choice(
            id="no-undefined",
            label=r"\text{not continuous - } f \text{ is undefined there}",
            is_latex=True,
            feedback=(
                "f is defined at the point in question - the definition says so "
                "explicitly. Being undefined is a fourth way continuity can "
                "fail, but it isn't this one."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=prompt,
        choices=choices,
        correct_choice=correct,
        slug=kind,
        instruction="Is f continuous at the join?",
        hints=(
            "Continuity at a point needs three separate things to hold. What are "
            "they?",
            "The limit must exist, the value must exist, and the two must be "
            "equal. Check each.",
        ),
        steps=(
            (r"\lim_{x \to a^{-}} f(x) = \lim_{x \to a^{+}} f(x) = f(a)", detail),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="aw-removable",
        tier="easy",
        variables=VARS,
        shape="(x-r)(x-o)/(x-r) as x -> r",
        skill="0/0 limits by factoring and cancelling",
        build=removable_discontinuity,
        params=(
            {"root": 2, "other": -2},
            {"root": 3, "other": 1},
            {"root": -1, "other": 4},
        ),
    ),
    Template(
        id="aw-infinity",
        tier="easy",
        variables=VARS,
        shape="(ax²+bx)/(cx²+d) as x -> infinity",
        skill="limits at infinity by leading coefficients",
        build=rational_at_infinity,
        params=(
            {"a": 3, "b": 1, "c": 2, "d": -5},
            {"a": 5, "b": -2, "c": 4, "d": 1},
            {"a": 1, "b": 6, "c": 3, "d": 2},
        ),
    ),
    Template(
        id="aw-sinc",
        tier="medium",
        variables=VARS,
        shape="sin(kx)/x as x -> 0",
        skill="the sin(x)/x limit, rescaled",
        build=sinc_limit,
        params=({"k": 1}, {"k": 3}, {"k": -2}),
    ),
    Template(
        id="aw-one-sided",
        tier="medium",
        variables=VARS,
        shape="1/(x-r) as x -> r",
        skill="one-sided limits, and when a limit fails to exist",
        build=one_sided_limit,
        params=({"root": 2}, {"root": -3}, {"root": 5}),
    ),
    Template(
        id="aw-continuity",
        tier="medium",
        variables=VARS,
        shape="continuity at a join",
        skill="the three conditions for continuity",
        build=continuity_check,
        params=({"kind": "jump"}, {"kind": "removable"}, {"kind": "mismatch"}),
    ),
)
