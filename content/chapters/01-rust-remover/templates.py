"""Chapter 1 - Rust Remover: index laws, roots, fractions, sign discipline.

Two design constraints shape every template here.

**Slots, not free-form.** Each asks for coefficients and exponents in named
slots rather than for a simplified expression. That is a correctness
requirement, not a UI preference: fingerprint grading accepts anything
numerically equal to the answer, and a "simplify this" prompt is numerically
equal to its own answer - so a free-form input would pass when the learner typed
the question straight back, having done nothing. Asking for the exponents is
also the sharper exercise; tracking powers through a quotient of products *is*
what index laws are.

**Authored prompts.** SymPy evaluates as it builds, so `sp.sqrt(72)` already
*is* `6*sqrt(2)` and there is no unsimplified object to render. Prompts are
therefore written with the `latex` helpers, while the SymPy `expr` exists purely
so `validate.check_answer_matches_prompt` can confirm the answer numerically.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, positive
from mathcoach.latex import (
    coeff,
    frac,
    linear,
    num,
    paren,
    power,
    product,
    root,
    signed,
    to_katex,
)

XY = positive("x", "y")
X_ONLY = positive("x")

x_pos, y_pos = (variable.symbol for variable in XY)
x_only = X_ONLY[0].symbol

ASSUME_XY = "Assume x, y > 0."
ASSUME_X = "Assume x > 0."


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _q(numer: int, denom: int) -> sp.Rational:
    return sp.Rational(numer, denom)


# ---------------------------------------------------------------------------
# Index laws
# ---------------------------------------------------------------------------


def power_of_quotient(
    c: int,
    px: int,
    qx: int,
    py: int,
    n: int,
    d: int,
    dx: int,
    dy: int,
) -> Instance:
    """(c·x^(px/qx)·y^py)^(1/n) / (d·x^dx·y^dy) - the chapter gate's shape."""
    inner_x = _q(px, qx)
    expr = (c * x_pos**inner_x * y_pos**py) ** _q(1, n) / (
        d * x_pos**dx * y_pos**dy
    )

    k = sp.Rational(c) ** _q(1, n) / d
    power_x = inner_x / n - dx
    power_y = _q(py, n) - dy
    answer = k * x_pos**power_x * y_pos**power_y

    numerator = paren(product(num(c), power("x", inner_x), power("y", py)))
    prompt = frac(
        power(numerator, _q(1, n)),
        product(num(d), power("x", dx), power("y", dy)),
    )

    return Instance(
        expr=expr,
        answer=answer,
        prompt_latex=prompt,
        assumption=ASSUME_XY,
        slug=f"c{c}p{px}q{qx}py{py}n{n}d{d}dx{dx}dy{dy}".replace("-", "m"),
        instruction=(
            "Write the result in the form k·xᵖ·y^q. Give k, then the power of x, "
            "then the power of y."
        ),
        slots=(
            ("k", k, "a number - exact, so leave surds as surds"),
            ("power of x", power_x, "a number, possibly negative or fractional"),
            ("power of y", power_y, "a number"),
        ),
        hints=(
            "Deal with the outer root first. Raising a power to a power "
            "multiplies the exponents - it does not add them.",
            f"The root applies to *every* factor inside, the {c} included, so "
            f"{_m(sp.Pow(sp.Integer(c), _q(1, n), evaluate=False))} ends up in k.",
            "Now divide. Dividing powers of the same base subtracts exponents, "
            "so each power drops by whatever the denominator carries.",
            f"Power of x: {_m(inner_x)} ÷ {n} − {dx}. "
            f"Power of y: {py} ÷ {n} − {dy}.",
        ),
        steps=(
            (
                product(
                    to_katex(sp.Pow(sp.Integer(c), _q(1, n), evaluate=False)),
                    power("x", inner_x / n),
                    power("y", _q(py, n)),
                ),
                f"Apply the outer root to every factor: each exponent is "
                f"multiplied by {_m(_q(1, n))}.",
            ),
            (
                to_katex(answer),
                "Then divide, subtracting the denominator's exponents.",
            ),
        ),
    )


def negative_exponent_quotient(a: int, m: int, n: int) -> Instance:
    """a·x^(-m) / x^(-n) - where sign slips are near-universal."""
    expr = a * x_only ** (-m) / x_only ** (-n)
    exponent = sp.Integer(n - m)
    answer = a * x_only**exponent

    prompt = frac(
        product(num(a), power("x", -m)),
        power("x", -n),
    )

    return Instance(
        expr=expr,
        answer=answer,
        prompt_latex=prompt,
        assumption=ASSUME_X,
        slug=f"a{a}m{m}n{n}".replace("-", "m"),
        instruction="Write the result as k·xᵖ. Give k, then the power of x.",
        slots=(
            ("k", sp.Integer(a), "a number"),
            ("power of x", exponent, "a number, possibly negative"),
        ),
        hints=(
            "Dividing powers of the same base subtracts the exponents. Watch "
            "carefully what subtracting a negative does.",
            f"The exponent is ({-m}) − ({-n}), which is {n} − {m}.",
        ),
        steps=(
            (
                power("x", 1).replace("x", "x") + f"^{{({-m}) - ({-n})}}",
                "Subtract the denominator's exponent from the numerator's.",
            ),
            (
                to_katex(answer),
                f"Two minus signs make a plus, so the power is {n - m}.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Fraction arithmetic
# ---------------------------------------------------------------------------


def fraction_chain(a: int, b: int, c: int, d: int, e: int, f: int) -> Instance:
    """(a/b) ÷ (c/d) − (e/f), answered as a fraction in lowest terms."""
    value = sp.Rational(a, b) / sp.Rational(c, d) - sp.Rational(e, f)

    prompt = (
        f"{frac(num(a), num(b))} \\div {frac(num(c), num(d))} - "
        f"{frac(num(e), num(f))}"
    )

    return Instance(
        expr=value,
        answer=value,
        prompt_latex=prompt,
        slug=f"a{a}b{b}c{c}d{d}e{e}f{f}".replace("-", "m"),
        instruction=(
            "Give the answer as a fraction in its lowest terms: numerator, then "
            "denominator."
        ),
        slots=(
            ("numerator", sp.Integer(value.p), "a whole number, sign included"),
            ("denominator", sp.Integer(value.q), "a positive whole number"),
        ),
        hints=(
            "Dividing by a fraction is multiplying by its reciprocal. Do that "
            "before you go anywhere near the subtraction.",
            f"So {_m(sp.Rational(a, b))} ÷ {_m(sp.Rational(c, d))} becomes "
            f"{_m(sp.Rational(a, b))} × {_m(sp.Rational(d, c))}.",
            f"That gives {_m(sp.Rational(a, b) / sp.Rational(c, d))}. Now put it "
            f"over a common denominator with {_m(sp.Rational(e, f))}.",
        ),
        steps=(
            (
                f"{frac(num(a), num(b))} \\times {frac(num(d), num(c))} - "
                f"{frac(num(e), num(f))}",
                "Turn the division into multiplication by the reciprocal.",
            ),
            (
                f"{to_katex(sp.Rational(a, b) * sp.Rational(d, c))} - "
                f"{to_katex(sp.Rational(e, f))}",
                "Do the multiplication.",
            ),
            (to_katex(value), "Common denominator, subtract, then cancel."),
        ),
    )


# ---------------------------------------------------------------------------
# Sign discipline
# ---------------------------------------------------------------------------


def nested_negation(a: int, b: int, c: int) -> Instance:
    """-(a - b(c - x)) expanded, answered by its coefficients."""
    expr = -(a - b * (c - x_only))
    expanded = sp.expand(expr)
    poly = sp.Poly(expanded, x_only)
    slope = poly.coeff_monomial(x_only)
    constant = poly.coeff_monomial(1)

    inner = f"{num(c)} - x"
    # The middle term is written `- b(...)`, so a negative b has to flip to a
    # plus rather than printing "7 - -2(3 - x)".
    bracket_term = coeff(abs(b), paren(inner))
    joiner = "-" if b > 0 else "+"
    prompt = "-" + paren(f"{num(a)} {joiner} {bracket_term}")

    return Instance(
        expr=expr,
        answer=expanded,
        prompt_latex=prompt,
        slug=f"a{a}b{b}c{c}".replace("-", "m"),
        instruction=(
            "Expand and collect. Give the coefficient of x, then the constant term."
        ),
        slots=(
            ("coefficient of x", slope, "a number, sign included"),
            ("constant term", constant, "a number, sign included"),
        ),
        hints=(
            "Work from the inside out. Deal with the bracket before you touch "
            "the leading minus sign.",
            "The leading minus sign applies to *both* terms inside the outer "
            "bracket, not just the first one.",
            f"Inside the outer bracket you get "
            f"{_m(sp.expand(a - b * (c - x_only)))}. Now negate all of it.",
        ),
        steps=(
            (
                "-" + paren(to_katex(sp.expand(a - b * (c - x_only)))),
                f"Expand the inner bracket first. Note that "
                f"{_m(sp.Integer(-b))} × (−x) is {_m(sp.Integer(b))}x.",
            ),
            (
                to_katex(expanded),
                "Negate every term of that, the constant included.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Roots
# ---------------------------------------------------------------------------


def surd_simplification(k: int, radicand: int) -> Instance:
    """k·√n written as p·√q with q square-free."""
    # Largest square factor first, so `inside` really is as small as possible -
    # the instruction promises that, and a smaller factor would leave a second
    # answer defensible.
    inside = sp.Integer(radicand)
    outside = sp.Integer(k)
    square_factor = 1
    for candidate in range(int(radicand**0.5), 1, -1):
        if radicand % (candidate * candidate) == 0:
            inside = sp.Integer(radicand // (candidate * candidate))
            outside = sp.Integer(k * candidate)
            square_factor = candidate
            break
    if square_factor == 1:
        raise ValueError(
            f"surd_simplification: {radicand} has no square factor, so there is "
            f"nothing to simplify"
        )

    expr = k * sp.sqrt(radicand)
    prompt = root(num(radicand)) if k == 1 else product(num(k), root(num(radicand)))

    return Instance(
        expr=expr,
        answer=outside * sp.sqrt(inside),
        prompt_latex=prompt,
        slug=f"k{k}n{radicand}",
        instruction="Write it as p·√q with q as small as possible. Give p, then q.",
        slots=(
            ("p", outside, "a whole number"),
            ("q", inside, "the smallest whole number left under the root"),
        ),
        hints=(
            "There is a square factor hiding inside the root.",
            f"What is the largest perfect square that divides {radicand}?",
            f"{radicand} = {square_factor**2} × {inside}, and "
            f"√{square_factor**2} = {square_factor} comes out.",
        ),
        steps=(
            (
                product(
                    num(k) if k != 1 else "",
                    root(num(square_factor**2)),
                    root(num(inside)),
                ),
                f"Split {radicand} into {square_factor**2} × {inside}, then split "
                f"the root across the product.",
            ),
            (
                to_katex(outside * sp.sqrt(inside)),
                "The perfect square leaves the root.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="rr-index-quotient",
        tier="medium",
        variables=XY,
        shape="(c·x^r·y^s)^(1/n) / (d·x^t·y^u)",
        skill="index laws with roots and negative powers",
        build=power_of_quotient,
        params=(
            # The roadmap's gate problem for this chapter.
            {"c": 8, "px": -2, "qx": 3, "py": 4, "n": 2, "d": 2, "dx": 4, "dy": -1},
            {"c": 27, "px": 3, "qx": 2, "py": 6, "n": 3, "d": 3, "dx": 2, "dy": 1},
            {"c": 16, "px": -1, "qx": 2, "py": 8, "n": 4, "d": 2, "dx": 1, "dy": -2},
        ),
    ),
    Template(
        id="rr-negative-exponent",
        tier="easy",
        variables=X_ONLY,
        shape="a·x^(-m) / x^(-n)",
        skill="subtracting negative exponents",
        build=negative_exponent_quotient,
        params=(
            {"a": 3, "m": 4, "n": 7},
            {"a": 5, "m": 2, "n": -3},
            {"a": 2, "m": -5, "n": -1},
        ),
    ),
    Template(
        id="rr-fraction-chain",
        tier="easy",
        variables=X_ONLY,
        shape="(a/b) ÷ (c/d) − e/f",
        skill="dividing and subtracting fractions",
        build=fraction_chain,
        params=(
            {"a": 2, "b": 3, "c": 4, "d": 9, "e": 1, "f": 6},
            {"a": 5, "b": 8, "c": 15, "d": 4, "e": 2, "f": 3},
            {"a": 7, "b": 10, "c": 21, "d": 5, "e": 1, "f": 4},
        ),
    ),
    Template(
        id="rr-nested-negation",
        tier="easy",
        variables=X_ONLY,
        shape="-(a - b(c - x))",
        skill="sign discipline through nested brackets",
        build=nested_negation,
        params=(
            {"a": 5, "b": 3, "c": 2},
            {"a": -4, "b": 6, "c": -1},
            {"a": 7, "b": -2, "c": 3},
        ),
    ),
    Template(
        id="rr-surd",
        tier="easy",
        variables=X_ONLY,
        shape="k·√n",
        skill="pulling square factors out of a root",
        build=surd_simplification,
        params=(
            {"k": 1, "radicand": 72},
            {"k": 3, "radicand": 50},
            {"k": 2, "radicand": 98},
        ),
    ),
)
