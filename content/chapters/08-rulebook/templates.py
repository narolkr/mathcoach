"""Chapter 8 - The Rulebook: power, product and quotient rules.

The chapter chapter 9 stands on. Everything here is a *single* rule applied
once; chapter 9 is what happens when rules nest.

Answers are written out longhand rather than taken from `sp.diff`, so
`validate.check_answer_is_correct` is a genuine independent check on the maths
rather than a tautology. Same discipline as chapter 9.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign, positive
from mathcoach.latex import coeff, num, root, to_katex
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol

# Roots need a positive domain: x^(1/2) has no real value for negative x.
POSITIVE_X = positive("x")


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


# ---------------------------------------------------------------------------
# The power rule, including the cases people trip on
# ---------------------------------------------------------------------------


def power_rule_terms(a: int, n: int, b: int, m: int) -> Instance:
    """a·xⁿ + b·xᵐ, where an exponent may be negative or fractional."""
    expr = a * x**sp.Rational(n) + b * x**sp.Rational(m)
    answer = a * n * x ** (sp.Rational(n) - 1) + b * m * x ** (sp.Rational(m) - 1)

    return Instance(
        expr=expr,
        answer=answer,
        slug=f"a{a}n{n}b{b}m{m}".replace("-", "m").replace("/", "_"),
        hints=(
            "Term by term. Each one is independent of the others.",
            "Bring the power down as a multiplier, then reduce it by one. That "
            "holds for negative and fractional powers too - there is no special "
            "case.",
            f"The first term gives {_m(a * n * x ** (sp.Rational(n) - 1))}.",
        ),
        steps=(
            (
                to_katex(answer),
                "Power down, power reduced, for each term separately.",
            ),
        ),
        distractors=(
            (
                "power-not-reduced",
                a * n * x ** sp.Rational(n) + b * m * x ** sp.Rational(m),
                "You brought each power down as a multiplier but left the "
                "exponent alone. Both things happen: multiply by the old power, "
                "then subtract one from it.",
            ),
            (
                "reduced-not-multiplied",
                a * x ** (sp.Rational(n) - 1) + b * x ** (sp.Rational(m) - 1),
                "You reduced the exponents but didn't multiply by the old power.",
            ),
        ),
    )


def root_power_rule(a: int, denom: int) -> Instance:
    """a·x^(1/denom) - the case where chapter 1's fractional powers pay off."""
    exponent = sp.Rational(1, denom)
    expr = a * x**exponent
    answer = a * exponent * x ** (exponent - 1)

    return Instance(
        expr=expr,
        answer=answer,
        assumption="Assume x > 0.",
        # Shown as a root, not as x^(1/n) - recognising that they are the same
        # thing is the exercise.
        prompt_latex=(
            root("x", denom) if a == 1 else f"{num(a)}{root('x', denom)}"
        ),
        slug=f"a{a}d{denom}",
        hints=(
            "A root is a fractional power. Rewrite it that way before you "
            "differentiate anything.",
            f"{_m(expr)} in index form is a·x^(1/{denom}).",
            f"Now the power rule applies unchanged: multiply by "
            f"{_m(exponent)} and reduce the exponent by one, giving "
            f"{_m(exponent - 1)}.",
        ),
        steps=(
            (
                to_katex(a * x**exponent),
                f"Rewrite the root as a fractional power.",
            ),
            (
                to_katex(answer),
                f"Power rule: multiply by {_m(exponent)}, reduce the exponent to "
                f"{_m(exponent - 1)}.",
            ),
        ),
        distractors=(
            (
                "forgot-to-reduce",
                a * exponent * x**exponent,
                "You multiplied by the fractional power but left the exponent "
                "unchanged. It still drops by one - which for 1/2 means going to "
                "−1/2, so the x ends up in a denominator.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# The product rule
# ---------------------------------------------------------------------------


def product_rule(a: int, n: int, kind: str) -> Instance:
    """a·xⁿ · g(x), with g one of exp, sin, cos."""
    if kind == "exp":
        g, g_prime, g_name = sp.exp(x), sp.exp(x), "e^x"
    elif kind == "sin":
        g, g_prime, g_name = sp.sin(x), sp.cos(x), "sin x"
    else:
        g, g_prime, g_name = sp.cos(x), -sp.sin(x), "cos x"

    u = a * x**n
    u_prime = a * n * x ** (n - 1)
    expr = u * g
    answer = u_prime * g + u * g_prime

    return Instance(
        expr=expr,
        answer=answer,
        slug=f"a{a}n{n}{kind}".replace("-", "m"),
        hints=(
            "Two factors multiplied, neither inside the other. That's the "
            "product rule, not the chain rule.",
            "(uv)' = u'v + uv'. Both terms survive - the answer has two pieces.",
            f"u = {_m(u)} so u' = {_m(u_prime)}; v = {_m(g)} so v' = {_m(g_prime)}.",
        ),
        steps=(
            (
                r"u'v + uv'",
                f"u = {_m(u)}, v = {_m(g)}.",
            ),
            (
                to_katex(answer),
                "Substitute all four pieces. Two terms, added.",
            ),
        ),
        distractors=(
            (
                "product-of-derivatives",
                u_prime * g_prime,
                "You multiplied the two derivatives together. That is the most "
                "common wrong guess, and it's wrong for a simple reason: "
                "differentiating is not multiplicative. (uv)' = u'v + uv'.",
            ),
            (
                "only-first-term",
                u_prime * g,
                "You differentiated the first factor and left the second alone. "
                "The product rule has two terms because *either* factor can be "
                "the one that changes.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# The quotient rule
# ---------------------------------------------------------------------------


def quotient_rule(a: int, b: int, n: int, c: int) -> Instance:
    """(a·x + b)/(xⁿ + c)."""
    numerator = a * x + b
    denominator = x**n + c
    expr = numerator / denominator

    num_prime = sp.Integer(a)
    den_prime = n * x ** (n - 1)
    answer = (num_prime * denominator - numerator * den_prime) / denominator**2

    return Instance(
        expr=expr,
        answer=answer,
        slug=f"a{a}b{b}n{n}c{c}".replace("-", "m"),
        hints=(
            "One expression divided by another, with x in the denominator. "
            "Quotient rule.",
            r"$(u/v)' = \frac{u'v - uv'}{v^{2}}$. The order in the numerator "
            "matters - it is minus, not plus, and u' comes first.",
            f"u = {_m(numerator)}, u' = {_m(num_prime)}; v = {_m(denominator)}, "
            f"v' = {_m(den_prime)}.",
        ),
        steps=(
            (
                r"\frac{u'v - uv'}{v^{2}}",
                f"u = {_m(numerator)}, v = {_m(denominator)}.",
            ),
            (
                to_katex(answer),
                "Substitute. Don't expand unless you need to - leaving it "
                "factored is usually more useful.",
            ),
        ),
        distractors=(
            (
                "sign-flipped",
                (numerator * den_prime - num_prime * denominator) / denominator**2,
                "Right structure, wrong order: the numerator is u'v − uv', not "
                "uv' − u'v. Your answer is the negative of the right one.",
            ),
            (
                "quotient-of-derivatives",
                num_prime / den_prime,
                "You divided the derivatives. Differentiating isn't "
                "multiplicative or divisive - the quotient rule exists precisely "
                "because that shortcut fails.",
            ),
            (
                "forgot-square",
                (num_prime * denominator - numerator * den_prime) / denominator,
                "The numerator is right but the denominator should be squared.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Which rule? - the recognition drill, one chapter before chapter 9's
# ---------------------------------------------------------------------------


def standard_derivative(which: str) -> Instance:
    """The four derivatives worth knowing cold, as a recall check."""
    table = {
        "exp": (sp.exp(x), sp.exp(x), r"e^{x}", "e^x is its own derivative - the only function that is, up to a constant multiple, and the reason e is the natural base."),
        "ln": (sp.log(x), 1 / x, r"\frac{1}{x}", "The derivative of ln x is 1/x. This is why chapter 12's integral of 1/x is a logarithm rather than a power."),
        "sin": (sp.sin(x), sp.cos(x), r"\cos x", "sin differentiates to cos, with no sign change."),
        "cos": (sp.cos(x), -sp.sin(x), r"-\sin x", "cos differentiates to MINUS sin. This minus sign causes more wrong answers than any other single fact in Act II."),
    }
    f, f_prime, correct_label, why = table[which]

    options = []
    for key, (_, candidate, label, _) in table.items():
        options.append(
            Choice(
                id=key,
                label=label,
                is_latex=True,
                feedback=(
                    why
                    if key == which
                    else f"That is the derivative of {to_katex(table[key][0])}."
                ),
            )
        )
    # A fifth option for the cos case's classic slip.
    if which == "cos":
        options.append(
            Choice(
                id="plus-sin",
                label=r"\sin x",
                is_latex=True,
                feedback=(
                    "Sign. The derivative of cos is −sin; you dropped the minus. "
                    "This is the single most common slip in the chapter."
                ),
            )
        )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=r"\frac{d}{dx}\left[" + to_katex(f) + r"\right]",
        choices=tuple(options),
        correct_choice=which,
        slug=which,
        instruction="From memory.",
        hints=(
            "These four are worth knowing without thinking. Everything in Act II "
            "is built from them.",
        ),
        steps=((correct_label, why),),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="rb-power",
        tier="easy",
        variables=VARS,
        rule="power",
        shape="a·xⁿ + b·xᵐ",
        skill="the power rule, including negative exponents",
        build=power_rule_terms,
        params=(
            {"a": 4, "n": 3, "b": -2, "m": 2},
            {"a": 3, "n": 5, "b": 1, "m": -2},
            {"a": -1, "n": 4, "b": 6, "m": -1},
        ),
    ),
    Template(
        id="rb-root",
        tier="medium",
        variables=POSITIVE_X,
        differentiates=True,
        shape="a·ⁿ√x",
        skill="differentiating a root as a fractional power",
        build=root_power_rule,
        params=({"a": 1, "denom": 2}, {"a": 3, "denom": 2}, {"a": 2, "denom": 3}),
    ),
    Template(
        id="rb-product",
        tier="medium",
        variables=VARS,
        rule="product",
        shape="a·xⁿ · g(x)",
        skill="the product rule",
        build=product_rule,
        params=(
            {"a": 1, "n": 2, "kind": "exp"},
            {"a": 3, "n": 1, "kind": "sin"},
            {"a": 2, "n": 3, "kind": "cos"},
        ),
    ),
    Template(
        id="rb-quotient",
        tier="medium",
        variables=VARS,
        rule="quotient",
        shape="(a·x + b)/(xⁿ + c)",
        skill="the quotient rule, and its sign order",
        build=quotient_rule,
        params=(
            {"a": 2, "b": 1, "n": 2, "c": 3},
            {"a": 1, "b": -4, "n": 2, "c": 1},
            {"a": 3, "b": 2, "n": 3, "c": 5},
        ),
    ),
    Template(
        id="rb-standard",
        tier="easy",
        variables=VARS,
        shape="d/dx of e^x, ln x, sin x, cos x",
        skill="the four derivatives worth knowing cold",
        build=standard_derivative,
        params=(
            {"which": "exp"},
            {"which": "ln"},
            {"which": "sin"},
            {"which": "cos"},
        ),
    ),
)
