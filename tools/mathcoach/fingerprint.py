"""Numeric fingerprints: how the browser grades algebra without a CAS.

A fingerprint is an expression evaluated at a fixed set of sample points. Two
expressions that agree at every sample point are, for the template families we
generate, the same function - so the browser can accept *any* algebraically
equivalent form of an answer by evaluating what the user typed at the same
points and comparing numbers.

Three things make this safe rather than merely convenient:

1. Sample points are chosen per problem, and rejected if any of the problem's
   expressions is undefined, complex, or non-finite there. That keeps poles,
   negative logs and even roots of negatives out of the fingerprint.
2. Variables carry a declared domain, so a problem in log(a) samples only
   positive a rather than throwing away seven candidates in eight.
3. The build refuses to emit a problem whose distractors collide with its
   correct answer (see validate.py), so "wrong answer" feedback can never fire
   on a right answer.

Fingerprints are multivariable: a problem may be in x alone, or in a, b and c.
The sample points are tuples aligned to a declared variable order.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import sympy as sp


class Domain(str, Enum):
    """What values a variable is allowed to take when sampling."""

    # Any nonzero rational. Zero is excluded because it sits on so many
    # singularities and makes too many wrong answers accidentally agree.
    ANY = "any"
    # Strictly positive. Required wherever logs or fractional powers appear.
    POSITIVE = "positive"


# Deliberately awkward rationals: no integers, nothing at 0, nothing repeating,
# and all modest in magnitude so that exp/power templates stay in a range where
# float comparison is meaningful. Order is fixed, so builds are reproducible.
SIGNED_POOL: tuple[sp.Rational, ...] = tuple(
    sp.Rational(n, d)
    for n, d in (
        (3, 7), (-2, 5), (9, 8), (-11, 9), (5, 4), (-3, 8), (13, 11), (-7, 6),
        (17, 12), (-15, 14), (7, 5), (-19, 16), (11, 9), (-5, 12), (21, 17),
        (-13, 10), (23, 18), (-9, 7), (19, 15), (-17, 13), (25, 21), (-23, 20),
    )
)

POSITIVE_POOL: tuple[sp.Rational, ...] = tuple(
    sp.Rational(n, d)
    for n, d in (
        (3, 7), (9, 8), (5, 4), (13, 11), (17, 12), (7, 5), (11, 9), (21, 17),
        (23, 18), (19, 15), (2, 9), (25, 21), (31, 24), (4, 11), (29, 19),
        (8, 5), (37, 28), (5, 16), (41, 30), (12, 7), (3, 20), (47, 34),
    )
)

# Coprime strides, so multivariable samples don't march in lockstep (which would
# make, say, a == b at every point and let wrong answers slip through).
_STRIDES = (1, 5, 9, 13, 3, 17, 7, 11)

SAMPLES_REQUIRED = 8
PRECISION = 40
CANDIDATE_LIMIT = 64

# Anything above this is treated as "too big to compare reliably in float64".
MAGNITUDE_CEILING = 1e12
# Imaginary parts above this mean we left the real domain.
IMAG_TOLERANCE = 1e-25


@dataclass(frozen=True)
class Variable:
    name: str
    domain: Domain = Domain.ANY
    # An explicit sample pool, for functions defined only on a narrow interval.
    # `sqrt(1/x - 4)` is real only on (0, 1/4], which neither standard pool
    # reaches - so those templates supply their own values rather than having
    # the build fail for want of eight valid points.
    pool: tuple[sp.Rational, ...] | None = None

    @property
    def symbol(self) -> sp.Symbol:
        """The symbol templates must use for this variable.

        Deliberately carries only `real=True` and NOT `positive=True`, even for
        a POSITIVE domain. SymPy treats `Symbol("x", positive=True)` as a
        different symbol from `Symbol("x", real=True)`, so adding the assumption
        here would make substitution silently do nothing and every fingerprint
        come back with free symbols.

        `Domain` therefore governs which values get *sampled*, not what SymPy
        may assume. Where a proof needs positivity, validate numerically over
        the declared domain rather than symbolically.
        """
        return sp.Symbol(self.name, real=True)


@dataclass(frozen=True)
class Fingerprint:
    """Sample points and the values an expression takes there."""

    # Variable names, in the order the point tuples are laid out.
    variables: tuple[str, ...]
    # One tuple per sample, each aligned to `variables`.
    points: tuple[tuple[float, ...], ...]
    ys: tuple[float, ...]
    # True for antiderivatives, where answers are only defined up to +C and must
    # be compared by their differences rather than their absolute values.
    up_to_constant: bool = False

    def to_dict(self) -> dict:
        return {
            "variables": list(self.variables),
            "points": [list(point) for point in self.points],
            "ys": list(self.ys),
            "upToConstant": self.up_to_constant,
        }


def _pool_for(variable: Variable) -> tuple[sp.Rational, ...]:
    if variable.pool is not None:
        return variable.pool
    return POSITIVE_POOL if variable.domain is Domain.POSITIVE else SIGNED_POOL


def interval_pool(
    low: sp.Rational, high: sp.Rational, count: int = 20
) -> tuple[sp.Rational, ...]:
    """`count` distinct rationals strictly inside (low, high].

    Deliberately uneven spacing, so the points don't sit on a lattice that a
    wrong-but-periodic answer could match.
    """
    low, high = sp.Rational(low), sp.Rational(high)
    if high <= low:
        raise ValueError(f"interval_pool needs high > low, got ({low}, {high}]")
    span = high - low

    # Visit the `count` slots in a scattered order. The stride must be coprime
    # to `count` or the walk cycles early and yields duplicates - computing it
    # beats guessing, which is how this first shipped with gcd(7, 21) = 7 and
    # produced three values instead of twenty.
    stride = next(
        candidate
        for candidate in range(count // 2, count)
        if math.gcd(candidate, count) == 1
    )

    values = [
        low + span * sp.Rational((stride * index) % count + 1, count + 1)
        for index in range(count)
    ]
    unique = list(dict.fromkeys(values))
    if len(unique) != count:
        raise ValueError(
            f"interval_pool produced {len(unique)} distinct values, expected "
            f"{count}, in ({low}, {high}]"
        )
    return tuple(unique)


def candidate_points(
    variables: tuple[Variable, ...],
    limit: int = CANDIDATE_LIMIT,
) -> list[tuple[sp.Rational, ...]]:
    """Deterministic candidate tuples, one per sample index.

    Each variable walks its own pool at its own stride, so the values across
    variables stay decorrelated - two variables never take the same value at
    every sample, which would let `a + b` pass as `2*a`.
    """
    tuples: list[tuple[sp.Rational, ...]] = []
    for index in range(limit):
        point = []
        for position, variable in enumerate(variables):
            pool = _pool_for(variable)
            stride = _STRIDES[position % len(_STRIDES)]
            offset = position * 3
            point.append(pool[(index * stride + offset) % len(pool)])
        tuples.append(tuple(point))
    return tuples


def evaluate(
    expr: sp.Expr,
    variables: tuple[Variable, ...],
    point: tuple[sp.Rational, ...],
) -> float | None:
    """Evaluate `expr` at `point`, or None if it isn't a finite real there."""
    try:
        substitutions = {
            variable.symbol: value for variable, value in zip(variables, point)
        }
        value = sp.N(expr.subs(substitutions), PRECISION)
        if value.free_symbols:
            # An unsubstituted symbol means the expression mentions a variable
            # the problem never declared - a template bug, not a domain issue.
            raise ValueError(
                f"{expr} still has free symbols {value.free_symbols} after "
                f"substituting {[v.name for v in variables]}"
            )
        if value.has(sp.zoo, sp.oo, -sp.oo, sp.nan):
            return None
        as_complex = complex(value)
    except (TypeError, ZeroDivisionError, AttributeError):
        return None

    if not math.isfinite(as_complex.real) or not math.isfinite(as_complex.imag):
        return None
    if abs(as_complex.imag) > IMAG_TOLERANCE:
        return None
    if abs(as_complex.real) > MAGNITUDE_CEILING:
        return None
    return as_complex.real


def choose_points(
    exprs: list[sp.Expr],
    variables: tuple[Variable, ...],
    count: int = SAMPLES_REQUIRED,
) -> tuple[tuple[sp.Rational, ...], ...]:
    """Pick sample points where *every* given expression is a finite real.

    All of a problem's expressions - the answer and every distractor - share one
    set of points, so their fingerprints are directly comparable.
    """
    usable: list[tuple[sp.Rational, ...]] = []
    for point in candidate_points(variables):
        # Reject points where two variables happen to coincide. The strides keep
        # them decorrelated overall, but they still collide periodically, and a
        # point where a == c cannot distinguish a*c from a^2. Cheap to skip.
        if len(set(point)) != len(point):
            continue
        if all(evaluate(expr, variables, point) is not None for expr in exprs):
            usable.append(point)
        if len(usable) == count:
            return tuple(usable)

    raise ValueError(
        f"only {len(usable)} of {count} sample points are valid for all of "
        f"{[str(e)[:50] for e in exprs]} over "
        f"{[(v.name, v.domain.value) for v in variables]} - widen the pools or "
        f"declare a narrower domain"
    )


def fingerprint_at(
    expr: sp.Expr,
    variables: tuple[Variable, ...],
    points: tuple[tuple[sp.Rational, ...], ...],
    up_to_constant: bool = False,
) -> Fingerprint:
    """Fingerprint `expr` at pre-chosen points."""
    ys: list[float] = []
    for point in points:
        value = evaluate(expr, variables, point)
        if value is None:
            raise ValueError(f"{expr} is not a finite real at {point}")
        ys.append(value)

    if up_to_constant:
        # Store differences from the first sample, so any constant offset - the
        # +C - cancels on both sides of the comparison.
        base = ys[0]
        ys = [y - base for y in ys]

    return Fingerprint(
        variables=tuple(variable.name for variable in variables),
        points=tuple(tuple(float(value) for value in point) for point in points),
        ys=tuple(ys),
        up_to_constant=up_to_constant,
    )


def agrees(a: Fingerprint, b: Fingerprint, rel_tol: float = 1e-6) -> bool:
    """Whether two fingerprints describe the same function. Mirrors grader.ts."""
    if a.variables != b.variables or a.points != b.points:
        return False
    if len(a.ys) != len(b.ys):
        return False
    return all(
        abs(x - y) <= rel_tol * max(1.0, abs(x), abs(y))
        for x, y in zip(a.ys, b.ys)
    )


# Convenience for the common single-variable case.
VAR_X = Variable("x", Domain.ANY)
ONE_VAR: tuple[Variable, ...] = (VAR_X,)
