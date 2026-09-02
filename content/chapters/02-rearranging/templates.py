"""Chapter 2 - Rearranging the Furniture: factoring, quadratics, inequalities.

"Factor this" is the clearest case of why free-form grading cannot work here:
x² − 4 and (x − 2)(x + 2) are the *same function*, so a fingerprint cannot tell
a factored answer from the question. Every template therefore asks for the
parameters - the roots, or the p and q in (x + p)² + q - which is both gradeable
and the actual skill.

Inequalities are multiple choice, because a solution set is not an expression.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import coeff, linear, num, paren, power, signed, to_katex
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _quadratic_latex(a: int, b: int, c: int) -> str:
    """a·x² + b·x + c, with every sign and unit coefficient handled."""
    head = coeff(a, power("x", 2))
    parts = [head]
    if b:
        parts.append(f"{'+' if b > 0 else '-'} {coeff(abs(b), 'x')}")
    if c:
        parts.append(f"{'+' if c > 0 else '-'} {num(abs(c))}")
    return " ".join(parts)


# ---------------------------------------------------------------------------
# Completing the square
# ---------------------------------------------------------------------------


def complete_the_square(b: int, c: int) -> Instance:
    """x² + bx + c written as (x + p)² + q."""
    p = sp.Rational(b, 2)
    q = sp.Rational(c) - p**2
    expr = x**2 + b * x + c
    answer = (x + p) ** 2 + q

    return Instance(
        expr=expr,
        answer=answer,
        prompt_latex=_quadratic_latex(1, b, c),
        slug=f"b{b}c{c}".replace("-", "m"),
        instruction="Write it as (x + p)² + q. Give p, then q.",
        slots=(
            ("p", p, "a number, possibly a fraction"),
            ("q", q, "a number, sign included"),
        ),
        hints=(
            "Halve the coefficient of x. That is p, and it is the only thing p "
            "ever depends on.",
            f"p = {b}/2 = {_m(p)}. Now expand (x + p)² and see what it leaves "
            "over.",
            f"(x {signed(p)})² = {_m(sp.expand((x + p) ** 2))}, which overshoots "
            f"the constant by {_m(p**2)}. So q corrects it: q = {c} − {_m(p**2)}.",
        ),
        steps=(
            (
                paren(f"x {signed(p)}") + "^{2}",
                f"Halve the coefficient of x: p = {_m(p)}.",
            ),
            (
                to_katex(sp.expand((x + p) ** 2)),
                f"Expanding that gives a constant of {_m(p**2)}, which is not "
                f"the {c} we want.",
            ),
            (
                to_katex(answer),
                f"So subtract the difference: q = {c} − {_m(p**2)} = {_m(q)}.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Roots of a quadratic
# ---------------------------------------------------------------------------


def integer_roots(r1: int, r2: int) -> Instance:
    """A quadratic with integer roots. Asked for smaller root first."""
    if r1 == r2:
        raise ValueError("integer_roots needs two distinct roots")
    smaller, larger = sorted((r1, r2))
    b = -(r1 + r2)
    c = r1 * r2
    expr = x**2 + b * x + c

    return Instance(
        expr=expr,
        answer=expr,
        prompt_latex=_quadratic_latex(1, b, c),
        slug=f"r{r1}s{r2}".replace("-", "m"),
        instruction="Find both roots. Smaller one first.",
        slots=(
            ("smaller root", sp.Integer(smaller), "a number"),
            ("larger root", sp.Integer(larger), "a number"),
        ),
        hints=(
            "Look for two numbers that multiply to the constant term and add to "
            "the coefficient of x.",
            f"Which two numbers multiply to {c} and add to {b}?",
            f"They are {smaller} and {larger}, so the factors are "
            f"{paren(linear(1, -smaller))}{paren(linear(1, -larger))} - and the "
            "roots are where each factor is zero.",
        ),
        steps=(
            (
                paren(linear(1, -smaller)) + paren(linear(1, -larger)),
                f"Two numbers multiplying to {c} and adding to {b} give the "
                f"factors.",
            ),
            (
                f"x = {num(smaller)} \\quad\\text{{or}}\\quad x = {num(larger)}",
                "Each factor being zero gives a root.",
            ),
        ),
    )


def surd_roots(b: int, c: int) -> Instance:
    """A quadratic whose roots are irrational - the formula, not guesswork."""
    discriminant = b * b - 4 * c
    if discriminant <= 0 or sp.sqrt(discriminant).is_Integer:
        raise ValueError(
            f"surd_roots wants an irrational pair; b={b}, c={c} gives "
            f"discriminant {discriminant}"
        )
    expr = x**2 + b * x + c
    smaller = (-b - sp.sqrt(discriminant)) / 2
    larger = (-b + sp.sqrt(discriminant)) / 2

    return Instance(
        expr=expr,
        answer=expr,
        prompt_latex=_quadratic_latex(1, b, c),
        slug=f"b{b}c{c}".replace("-", "m"),
        instruction=(
            "Find both roots exactly - leave the surd as a surd. Smaller first."
        ),
        slots=(
            ("smaller root", smaller, "exact, e.g. (3-sqrt(5))/2"),
            ("larger root", larger, "exact"),
        ),
        hints=(
            "This one doesn't factor over the integers. Reach for the formula.",
            r"$x = \frac{-b \pm \sqrt{b^2 - 4c}}{2}$ for a monic quadratic.",
            f"The discriminant is {b}² − 4·{c} = {discriminant}, which is not a "
            f"perfect square - so the roots keep a √{discriminant} in them.",
            f"√{discriminant} = {to_katex(sp.sqrt(discriminant))}, so the roots "
            f"are {_m(smaller)} and {_m(larger)}.",
        ),
        steps=(
            (
                r"x = \frac{" + f"{-b} \\pm \\sqrt{{{discriminant}}}" + "}{2}",
                f"Substitute into the quadratic formula: discriminant = "
                f"{discriminant}.",
            ),
            (
                f"x = {to_katex(smaller)} \\quad\\text{{or}}\\quad x = "
                f"{to_katex(larger)}",
                "Simplify the surd, but don't decimalise it.",
            ),
        ),
    )


def _verify_roots(inst: Instance) -> None:
    """Every slot value really is a root of the quadratic in the prompt.

    Root-finding templates opt out of the generic answer-equals-prompt check,
    so this is the only thing standing between a sign slip and a level that
    marks correct answers wrong.
    """
    for label, value, _ in inst.slots:
        residual = sp.simplify(inst.expr.subs(x, value))
        if residual != 0:
            raise ValueError(
                f"slot {label!r} = {value} is not a root of {inst.expr} "
                f"(substituting gives {residual})"
            )
    # And they must be *both* roots, not the same one twice.
    values = [sp.simplify(value) for _, value, _ in inst.slots]
    if len(set(map(str, values))) != len(values):
        raise ValueError(f"slots repeat the same root: {values}")
    # Ordering the instruction promises: smaller first.
    if len(values) == 2 and sp.N(values[0]) > sp.N(values[1]):
        raise ValueError(
            f"slots are out of order: {values[0]} is not smaller than {values[1]}"
        )


# ---------------------------------------------------------------------------
# Inequalities - a solution set is not an expression, so: choices
# ---------------------------------------------------------------------------


def linear_inequality(a: int, b: int, c: int) -> Instance:
    """Solve a·x + b > c, where a may be negative and flip the sign."""
    if a == 0:
        raise ValueError("linear_inequality needs a nonzero coefficient")
    boundary = sp.Rational(c - b, a)
    flips = a < 0
    correct_symbol = "<" if flips else ">"
    wrong_symbol = ">" if flips else "<"

    prompt = f"{linear(a, b)} > {num(c)}"
    boundary_tex = to_katex(boundary)

    choices = (
        Choice(
            id="correct",
            label=f"x {correct_symbol} {boundary_tex}",
            is_latex=True,
            feedback=(
                f"Dividing by {a} "
                + (
                    "reverses the inequality, because multiplying or dividing by "
                    "a negative flips which side is bigger."
                    if flips
                    else "keeps the inequality the same way round, because "
                    f"{a} is positive."
                )
            ),
        ),
        Choice(
            id="unflipped",
            label=f"x {wrong_symbol} {boundary_tex}",
            is_latex=True,
            feedback=(
                f"The boundary is right, but the direction is not. You divided "
                f"by {a} without "
                + ("flipping the inequality." if flips else "keeping it as it was.")
            ),
        ),
        Choice(
            id="wrong-boundary",
            label=f"x {correct_symbol} {to_katex(sp.Rational(c + b, a))}",
            is_latex=True,
            feedback=(
                f"The direction is right, but you added {b} instead of "
                f"subtracting it when moving it across."
            ),
        ),
        Choice(
            id="no-division",
            label=f"x {correct_symbol} {num(c - b)}",
            is_latex=True,
            feedback=(
                f"You moved the {b} across correctly but never divided by {a}."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=prompt,
        choices=choices,
        correct_choice="correct",
        slug=f"a{a}b{b}c{c}".replace("-", "m"),
        instruction="Solve for x.",
        hints=(
            f"Get the {coeff(a, 'x')} on its own first, then divide.",
            "Before you divide: is the number you're dividing by positive or "
            "negative? That decides whether the inequality flips.",
        ),
        steps=(
            (
                f"{coeff(a, 'x')} > {num(c - b)}",
                f"Move {b} to the other side.",
            ),
            (
                f"x {correct_symbol} {boundary_tex}",
                f"Divide by {a}"
                + (" and flip the inequality." if flips else "."),
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="rf-complete-square",
        tier="medium",
        variables=VARS,
        shape="x² + bx + c -> (x+p)² + q",
        skill="completing the square",
        build=complete_the_square,
        params=(
            {"b": 6, "c": 5},
            {"b": -8, "c": 3},
            {"b": 5, "c": -2},
            {"b": -3, "c": 7},
        ),
    ),
    Template(
        id="rf-integer-roots",
        tier="easy",
        variables=VARS,
        shape="x² + bx + c with integer roots",
        skill="factoring a monic quadratic",
        tags=("not-equal-to-prompt", "unordered-slots"),
        verify=_verify_roots,
        build=integer_roots,
        params=(
            {"r1": 3, "r2": -2},
            {"r1": -5, "r2": 1},
            {"r1": 4, "r2": 6},
            {"r1": -3, "r2": -7},
        ),
    ),
    Template(
        id="rf-surd-roots",
        tier="hard",
        variables=VARS,
        shape="x² + bx + c with irrational roots",
        skill="the quadratic formula, kept exact",
        tags=("not-equal-to-prompt", "unordered-slots"),
        verify=_verify_roots,
        build=surd_roots,
        params=(
            {"b": -3, "c": 1},
            {"b": 5, "c": 2},
            {"b": -1, "c": -3},
        ),
    ),
    Template(
        id="rf-inequality",
        tier="easy",
        variables=VARS,
        shape="a·x + b > c",
        skill="inequalities, and when the sign flips",
        build=linear_inequality,
        params=(
            {"a": 3, "b": 4, "c": 19},
            {"a": -2, "b": 5, "c": 1},
            {"a": -4, "b": -3, "c": 9},
            {"a": 5, "b": -2, "c": 13},
        ),
    ),
)
