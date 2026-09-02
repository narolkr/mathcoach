"""Chapter 10 - Hidden Relations: implicit differentiation and related rates.

The first chapter whose *answer* is multivariable. dy/dx for an implicit curve
is a function of x and y together, which is exactly what the multivariable
fingerprint machinery was built for - and a useful rehearsal for Act IV, where
everything has several inputs.

Related rates are graded as numbers, and free-form is safe: the prompt is a
scenario, not an expression.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import coeff, frac, num, power, to_katex
from mathcoach.schema import Choice

# dy/dx depends on both x and y, so both are sampled.
XY = any_sign("x", "y")
x, y = (variable.symbol for variable in XY)

X_ONLY = any_sign("x")


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def _implicit_derivative(relation: sp.Expr) -> sp.Expr:
    """dy/dx from F(x,y) = 0, by the standard -F_x / F_y.

    Used to check the template's hand-written answer, not to produce it.
    """
    return -sp.diff(relation, x) / sp.diff(relation, y)


# ---------------------------------------------------------------------------
# Implicit differentiation
# ---------------------------------------------------------------------------


def implicit_polynomial(a: int, b: int, c: int, rhs: int) -> Instance:
    """a·x² + b·xy + c·y³ = rhs. The chapter gate's shape."""
    relation = a * x**2 + b * x * y + c * y**3 - rhs

    # Written out longhand: differentiate term by term treating y as y(x).
    #   2ax + b(y + x·y') + 3c·y²·y' = 0
    #   y'(bx + 3c·y²) = -(2ax + by)
    numerator = -(2 * a * x + b * y)
    denominator = b * x + 3 * c * y**2
    answer = numerator / denominator

    residual = sp.simplify(answer - _implicit_derivative(relation))
    if residual != 0:
        raise ValueError(
            f"implicit_polynomial({a},{b},{c},{rhs}): stated dy/dx is wrong; "
            f"-F_x/F_y differs by {residual}"
        )

    left = " ".join(
        piece
        for piece in (
            coeff(a, power("x", 2)),
            f"+ {coeff(b, 'xy')}" if b > 0 else f"- {coeff(abs(b), 'xy')}",
            f"+ {coeff(c, power('y', 3))}" if c > 0 else f"- {coeff(abs(c), power('y', 3))}",
        )
        if piece
    )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=f"{left} = {num(rhs)}",
        assumption="y is a function of x.",
        slug=f"a{a}b{b}c{c}r{rhs}".replace("-", "m"),
        instruction="Find dy/dx. Your answer may contain both x and y.",
        hints=(
            "Differentiate both sides with respect to x, treating y as a "
            "function of x rather than as a constant.",
            "Every y you differentiate contributes a dy/dx by the chain rule. "
            f"So {_m(c * y**3)} becomes {_m(3 * c * y**2)} times dy/dx.",
            f"The {_m(b * x * y)} term needs the *product* rule as well as the "
            f"chain rule: it gives {_m(b * y)} + {_m(b * x)}·dy/dx.",
            "Now collect every dy/dx term on one side and divide.",
        ),
        steps=(
            (
                f"{to_katex(2 * a * x)} + {to_katex(b * y)} + "
                f"{to_katex(b * x)}\\frac{{dy}}{{dx}} + "
                f"{to_katex(3 * c * y**2)}\\frac{{dy}}{{dx}} = 0",
                "Differentiate term by term. Each y brings a dy/dx with it.",
            ),
            (
                f"\\frac{{dy}}{{dx}}\\left({to_katex(denominator)}\\right) = "
                f"{to_katex(numerator)}",
                "Collect the dy/dx terms on one side, everything else on the "
                "other.",
            ),
            (to_katex(answer), "Divide."),
        ),
        distractors=(
            (
                "treated-y-as-constant",
                -(2 * a * x + b * y) / (b * x),
                "You differentiated the y³ term as if y were a constant, so it "
                "vanished. It isn't - y depends on x, so y³ differentiates to "
                "3y²·dy/dx and belongs in the denominator.",
            ),
            (
                "sign-error",
                (2 * a * x + b * y) / denominator,
                "Right structure, wrong sign. Moving the non-dy/dx terms across "
                "the equals sign negates them.",
            ),
            (
                "forgot-product-rule",
                -(2 * a * x) / denominator,
                "The xy term needs the product rule, which contributes a "
                f"{_m(b * y)} that you've dropped from the numerator.",
            ),
        ),
    )


def implicit_circle(radius_squared: int) -> Instance:
    """x² + y² = r². The cleanest implicit derivative there is."""
    relation = x**2 + y**2 - radius_squared
    answer = -x / y

    residual = sp.simplify(answer - _implicit_derivative(relation))
    if residual != 0:
        raise ValueError(f"implicit_circle({radius_squared}): dy/dx is wrong")

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=f"{power('x', 2)} + {power('y', 2)} = {num(radius_squared)}",
        assumption="y is a function of x.",
        slug=f"r{radius_squared}",
        instruction="Find dy/dx.",
        hints=(
            "Differentiate both sides. y² needs the chain rule because y depends "
            "on x.",
            "2x + 2y·dy/dx = 0. Now solve for dy/dx.",
        ),
        steps=(
            (
                r"2x + 2y\frac{dy}{dx} = 0",
                "Differentiate. The y² term brings a dy/dx.",
            ),
            (
                to_katex(answer),
                "Solve. Note the answer is −x/y, which is the negative "
                "reciprocal of the radius's slope y/x - the tangent to a circle "
                "is perpendicular to its radius, and the algebra says so.",
            ),
        ),
        distractors=(
            (
                "treated-y-as-constant",
                sp.Integer(0),
                "Differentiating y² as if y were constant gives 0, which loses "
                "the whole point. y is a function of x here.",
            ),
            (
                "sign-error",
                x / y,
                "Sign. From 2x + 2y·y' = 0 you get y' = −x/y; the 2x moves "
                "across and becomes negative.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Related rates
# ---------------------------------------------------------------------------


def related_rates_sphere(dr_dt: int, radius: int) -> Instance:
    """dV/dt for a sphere whose radius grows at a constant rate."""
    r = sp.Symbol("r", positive=True)
    volume = sp.Rational(4, 3) * sp.pi * r**3
    answer = 4 * sp.pi * radius**2 * dr_dt

    # Independent check: SymPy differentiates the volume formula itself.
    from_sympy = sp.diff(volume, r).subs(r, radius) * dr_dt
    if sp.simplify(answer - from_sympy) != 0:
        raise ValueError(
            f"related_rates_sphere(dr={dr_dt}, r={radius}): stated {answer} but "
            f"dV/dr·dr/dt = {from_sympy}"
        )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=(
            r"V = \tfrac{4}{3}\pi r^{3} \qquad \frac{dr}{dt} = "
            + num(dr_dt)
            + r" \qquad r = "
            + num(radius)
        ),
        slug=f"dr{dr_dt}r{radius}".replace("-", "m"),
        instruction=(
            f"A sphere's radius grows at {dr_dt} units per second. How fast is "
            f"its volume growing when r = {radius}? Give the exact value - keep "
            f"the π."
        ),
        hints=(
            "Both V and r depend on time. Differentiate the volume formula with "
            "respect to t, not r.",
            r"By the chain rule, $\frac{dV}{dt} = \frac{dV}{dr}\cdot"
            r"\frac{dr}{dt}$.",
            f"dV/dr = 4πr², which at r = {radius} is {_m(4 * sp.pi * radius**2)}. "
            f"Multiply by dr/dt = {dr_dt}.",
        ),
        steps=(
            (
                r"\frac{dV}{dt} = 4\pi r^{2}\,\frac{dr}{dt}",
                "The chain rule, with t as the underlying variable.",
            ),
            (
                to_katex(answer),
                f"Substitute r = {radius} and dr/dt = {dr_dt}.",
            ),
        ),
        distractors=(
            *(
                (
                    (
                        "forgot-dr-dt",
                        4 * sp.pi * radius**2,
                        f"That's dV/dr, the rate per unit *radius*. The question "
                        f"asks per unit *time*, so it still needs multiplying by "
                        f"dr/dt = {dr_dt}.",
                    ),
                )
                if dr_dt != 1
                else ()
            ),
            # At r = 3, (4/3)πr³ and 4πr² are both 72π - the volume and the
            # rate coincide numerically, so this distractor would BE the answer.
            # Guarded rather than sidestepped by choosing different radii,
            # because the collision depends on the parameters in a way that is
            # easy to reintroduce later.
            *(
                (
                    (
                        "used-volume",
                        sp.Rational(4, 3) * sp.pi * radius**3 * dr_dt,
                        "You used the volume rather than its derivative. The "
                        "rate of change needs dV/dr = 4πr², not V itself.",
                    ),
                )
                if radius != 3
                else ()
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="hr-implicit-poly",
        tier="hard",
        variables=XY,
        shape="a·x² + b·xy + c·y³ = k",
        skill="implicit differentiation with a product term",
        build=implicit_polynomial,
        params=(
            # The roadmap's gate: x² + xy + y³ = 7.
            {"a": 1, "b": 1, "c": 1, "rhs": 7},
            {"a": 2, "b": -3, "c": 1, "rhs": 4},
            {"a": 1, "b": 2, "c": -1, "rhs": -5},
        ),
    ),
    Template(
        id="hr-implicit-circle",
        tier="medium",
        variables=XY,
        shape="x² + y² = r²",
        skill="implicit differentiation, simplest case",
        build=implicit_circle,
        params=({"radius_squared": 25}, {"radius_squared": 9}, {"radius_squared": 4}),
    ),
    Template(
        id="hr-related-rates",
        tier="medium",
        variables=X_ONLY,
        shape="dV/dt for a growing sphere",
        skill="related rates through the chain rule",
        build=related_rates_sphere,
        params=(
            {"dr_dt": 2, "radius": 3},
            {"dr_dt": 5, "radius": 1},
            {"dr_dt": 3, "radius": 4},
        ),
    ),
)
