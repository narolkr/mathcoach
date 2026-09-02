"""Chapter 3 - Machines with Inputs: composition, domains, inverses.

Composition is the one place in Act I where **free-form grading is safe**: the
prompt shows f and g separately, and the answer f(g(x)) is a different
expression from anything shown, so there is nothing for the learner to paste
back. Same for inverses. Domains go to multiple choice, because a set is not an
expression.

This chapter matters more than its position suggests. The chain rule is a
statement about composition, and a neural network *is* a composition - so the
fluency built here is the fluency chapter 9 spends itself on.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.fingerprint import Domain, Variable, interval_pool
from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import frac, linear, num, paren, root, to_katex
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _given(f_latex: str, g_latex: str) -> str:
    return (
        r"f(x) = " + f_latex + r"\qquad g(x) = " + g_latex
    )


# ---------------------------------------------------------------------------
# Composition
# ---------------------------------------------------------------------------


def compose_linear_into_power(a: int, b: int, n: int, c: int) -> Instance:
    """f(x) = xⁿ + c, g(x) = ax + b. Asked for f(g(x))."""
    if n < 2:
        raise ValueError("compose_linear_into_power needs a real power to substitute into")

    def f_of(t):
        return t**n + c

    def g_of(t):
        return a * t + b

    answer = f_of(g_of(x))

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=_given(to_katex(x**n + c), linear(a, b)),
        slug=f"a{a}b{b}n{n}c{c}".replace("-", "m"),
        instruction="Write f(g(x)) in terms of x. Don't expand it unless you want to.",
        hints=(
            "f(g(x)) means: work out g first, then feed the whole result into f.",
            f"Wherever f's formula has an x, put {_m(g_of(x))} instead - brackets "
            "and all.",
            f"So f(g(x)) = {_m(answer)}.",
        ),
        steps=(
            (
                to_katex(answer),
                f"Substitute g(x) = {_m(g_of(x))} into every x of f.",
            ),
        ),
        distractors=(
            (
                "wrong-order",
                g_of(f_of(x)),
                "That's g(f(x)), the other way round. Composition is not "
                "commutative: f(g(x)) feeds g's output into f, not the reverse.",
            ),
            (
                "no-bracket",
                a * x**n + b + c,
                f"You raised only the x to the power, not the whole of g(x). "
                f"The substitution is {_m(g_of(x) ** n)}, with brackets round "
                f"the entire inner function - that is exactly the structure the "
                f"chain rule will later ask you to see.",
            ),
        ),
    )


def compose_root_and_reciprocal(shift: int) -> Instance:
    """f(x) = √(x - shift), g(x) = 1/x. The chapter gate's shape.

    Note the narrow domain: sqrt(1/x - shift) is real only on (0, 1/shift], so
    this family declares its own sample pool. That the standard pools couldn't
    reach it is exactly the point of the chapter - this composition's domain is
    far smaller than either function's own.
    """
    f_of = lambda t: sp.sqrt(t - shift)  # noqa: E731
    g_of = lambda t: 1 / t  # noqa: E731
    answer = f_of(g_of(x))

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=_given(root(linear(1, -shift)), frac("1", "x")),
        slug=f"s{shift}".replace("-", "m"),
        instruction="Write f(g(x)) in terms of x.",
        hints=(
            "Substitute the whole of g(x) into f's formula.",
            "f's formula is a root of (something minus "
            f"{shift}). The something is 1/x.",
            f"f(g(x)) = {_m(answer)}.",
        ),
        steps=(
            (
                to_katex(answer),
                f"Replace f's x with 1/x, keeping the −{shift} outside it.",
            ),
        ),
        # No `wrong-order` distractor here, and the reason is worth knowing:
        # g(f(x)) = 1/sqrt(x - shift) is defined only for x > shift, while
        # f(g(x)) is defined only on (0, 1/shift]. The two compositions have
        # *disjoint* domains, so there is no point at which both can be
        # evaluated and compared. The concept card makes this a teaching point.
        distractors=(
            (
                "reciprocal-of-whole",
                1 / (sp.sqrt(x) - shift),
                "The 1/x has to go inside the root, in place of f's x. You "
                "applied the reciprocal to the whole of f instead.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Domains - a set is not an expression, so: choices
# ---------------------------------------------------------------------------


def domain_of_composition(shift: int) -> Instance:
    """The exact domain of f(g(x)) for f = √(x-shift), g = 1/x.

    The roadmap's chapter 3 gate asks for these domains, and they are the part
    people skip. Both constraints matter: g needs x != 0, and f needs its
    argument non-negative.
    """
    # sqrt(1/x - shift) >= 0 needs 1/x >= shift.
    if shift <= 0:
        raise ValueError("domain_of_composition assumes a positive shift")
    upper = sp.Rational(1, shift)

    correct = f"0 < x \\le {to_katex(upper)}"
    choices = (
        Choice(
            id="correct",
            label=correct,
            is_latex=True,
            feedback=(
                f"Both constraints bite. g(x) = 1/x needs x ≠ 0, and the root "
                f"needs 1/x − {shift} ≥ 0, which means 1/x ≥ {shift}. For "
                f"positive x that gives x ≤ {to_katex(upper)}; negative x makes "
                f"1/x negative, so it fails the root."
            ),
        ),
        Choice(
            id="forgot-zero",
            label=f"x \\le {to_katex(upper)}",
            is_latex=True,
            feedback=(
                "You handled the root but not the 1/x. x = 0 is in this set, and "
                "g isn't defined there - the inner function's own domain still "
                "applies."
            ),
        ),
        Choice(
            id="only-inner",
            label=r"x \ne 0",
            is_latex=True,
            feedback=(
                "That is g's domain alone. The composition also has to keep f "
                "happy, and f can't take a negative argument."
            ),
        ),
        Choice(
            id="wrong-direction",
            label=f"x \\ge {to_katex(upper)}",
            is_latex=True,
            feedback=(
                f"The boundary is right but the direction is inverted. As x "
                f"grows, 1/x *shrinks* - so large x makes 1/x − {shift} "
                f"negative."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=_given(root(linear(1, -shift)), frac("1", "x"))
        + r"\qquad \text{domain of } f(g(x))?",
        choices=choices,
        correct_choice="correct",
        slug=f"s{shift}",
        instruction="What is the exact domain of f(g(x))?",
        hints=(
            "Two things can go wrong. Find both before you look at the options.",
            "First: where is g itself undefined? Second: what does f refuse to "
            "accept?",
            f"So you need x ≠ 0 *and* 1/x − {shift} ≥ 0 at the same time.",
        ),
        steps=(
            (
                r"x \ne 0",
                "g(x) = 1/x rules out zero. The inner function's domain always "
                "carries through.",
            ),
            (
                f"\\frac{{1}}{{x}} - {num(shift)} \\ge 0",
                "And f needs a non-negative argument.",
            ),
            (
                correct,
                "Both at once. Only positive x can satisfy the second, which is "
                "what closes off the negative half.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Inverses
# ---------------------------------------------------------------------------


def inverse_of_linear_over_linear(a: int, b: int, c: int) -> Instance:
    """f(x) = (a·x + b)/(x + c). Asked for f inverse."""
    y = sp.Symbol("y", real=True)
    solved = sp.solve(sp.Eq((a * x + b) / (x + c), y), x)
    if len(solved) != 1:
        raise ValueError(f"expected a unique inverse, got {solved}")
    answer = sp.simplify(solved[0].subs(y, x))

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=r"f(x) = " + frac(linear(a, b), linear(1, c)),
        slug=f"a{a}b{b}c{c}".replace("-", "m"),
        instruction="Find f⁻¹(x).",
        hints=(
            "Write y = f(x), then rearrange to get x on its own. Swap the letters "
            "at the very end.",
            "Multiply both sides by the denominator first, so nothing is stuck "
            "inside a fraction.",
            f"You should reach x{paren('y - ' + num(a))} = "
            f"{num(b)} - {num(c)}y, then divide.",
            f"f⁻¹(x) = {_m(answer)}.",
        ),
        steps=(
            (
                f"y{paren(linear(1, c))} = {linear(a, b)}",
                "Clear the denominator.",
            ),
            (
                to_katex(answer),
                "Collect the x terms, divide, then rename y back to x.",
            ),
        ),
        distractors=(
            (
                "reciprocal",
                (x + c) / (a * x + b),
                "That's 1/f(x), not the inverse. An inverse undoes the function; "
                "a reciprocal divides one by it. They're different operations "
                "that unfortunately share the ⁻¹ notation.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="mi-compose-power",
        tier="easy",
        variables=VARS,
        shape="f = xⁿ + c, g = ax + b",
        skill="substituting one function into another",
        build=compose_linear_into_power,
        params=(
            {"a": 3, "b": 1, "n": 2, "c": 0},
            {"a": 2, "b": -5, "n": 3, "c": 4},
            {"a": -1, "b": 2, "n": 2, "c": -3},
        ),
    ),
    # One template per shift: each has a different domain, so each needs its own
    # sample pool inside (0, 1/shift].
    *(
        Template(
            id=f"mi-compose-root-{shift}",
            tier="medium",
            variables=(
                Variable("x", Domain.POSITIVE, pool=interval_pool(0, sp.Rational(1, shift))),
            ),
            shape=f"f = √(x-{shift}), g = 1/x",
            skill="composing a root with a reciprocal",
            build=compose_root_and_reciprocal,
            params=({"shift": shift},),
        )
        for shift in (1, 2, 4)
    ),
    Template(
        id="mi-domain",
        tier="hard",
        variables=VARS,
        shape="domain of f(g(x))",
        skill="domains of compositions",
        build=domain_of_composition,
        params=({"shift": 1}, {"shift": 2}, {"shift": 4}),
    ),
    Template(
        id="mi-inverse",
        tier="medium",
        variables=VARS,
        shape="f = (ax+b)/(x+c)",
        skill="finding an inverse by rearranging",
        build=inverse_of_linear_over_linear,
        params=(
            {"a": 2, "b": 1, "c": 3},
            {"a": 1, "b": -4, "c": 2},
            {"a": 3, "b": 2, "c": -1},
        ),
    ),
)
