"""Tests for the grading premise itself.

If these pass, the browser can grade algebra by comparing numbers. If any of
them fail, the whole architecture is unsound - so they are the most important
tests in the project.
"""

from __future__ import annotations

import pytest
import sympy as sp

from mathcoach.fingerprint import (
    ONE_VAR,
    POSITIVE_POOL,
    SIGNED_POOL,
    Domain,
    Variable,
    agrees,
    choose_points,
    evaluate,
    fingerprint_at,
    interval_pool,
)

X = sp.Symbol("x", real=True)
A, B, C = sp.symbols("a b c", real=True)

POSITIVE_X: tuple[Variable, ...] = (Variable("x", Domain.POSITIVE),)
ABC: tuple[Variable, ...] = tuple(
    Variable(name, Domain.POSITIVE) for name in ("a", "b", "c")
)


def fp(expr, variables=ONE_VAR, up_to_constant=False):
    points = choose_points([expr], variables)
    return fingerprint_at(expr, variables, points, up_to_constant)


# --- The premise: equivalent forms must grade equal -------------------------


@pytest.mark.parametrize(
    "written_by_us, written_by_learner",
    [
        # Factored vs expanded.
        (12 * (3 * X + 1) ** 3, 324 * X**3 + 324 * X**2 + 108 * X + 12),
        # Double-angle identity: the form a learner may well produce for
        # d/dx cos^2(2x), which must be accepted.
        (-4 * sp.sin(2 * X) * sp.cos(2 * X), -2 * sp.sin(4 * X)),
        # Unsimplified chain rule output, exactly as first written down.
        (6 * X * sp.cos(3 * X**2 + 1), sp.cos(3 * X**2 + 1) * 3 * 2 * X),
        # The same fraction rescaled - a genuinely non-obvious equivalence.
        ((6 * X) / (3 * X**2 + 1), (2 * X) / (X**2 + sp.Rational(1, 3))),
        # Powers written differently.
        (sp.sqrt(X**2 + 1), (X**2 + 1) ** sp.Rational(1, 2)),
    ],
)
def test_equivalent_forms_agree(written_by_us, written_by_learner):
    points = choose_points([written_by_us, written_by_learner], ONE_VAR)
    assert agrees(
        fingerprint_at(written_by_us, ONE_VAR, points),
        fingerprint_at(written_by_learner, ONE_VAR, points),
    )


@pytest.mark.parametrize(
    "correct, wrong",
    [
        # The classic dropped inner derivative.
        (6 * X * sp.cos(3 * X**2 + 1), sp.cos(3 * X**2 + 1)),
        # Dropped inner coefficient.
        (12 * (3 * X + 1) ** 3, 4 * (3 * X + 1) ** 3),
        # Sign error.
        (-4 * sp.sin(2 * X) * sp.cos(2 * X), 4 * sp.sin(2 * X) * sp.cos(2 * X)),
        # Off by a constant, which must NOT be accepted for a derivative.
        (6 * X, 6 * X + 1),
    ],
)
def test_wrong_answers_disagree(correct, wrong):
    points = choose_points([correct, wrong], ONE_VAR)
    assert not agrees(
        fingerprint_at(correct, ONE_VAR, points),
        fingerprint_at(wrong, ONE_VAR, points),
    )


# --- Multivariable ---------------------------------------------------------


def test_multivariable_equivalence():
    """ln(a^2 b / sqrt(c)) and its expansion are the same function."""
    condensed = sp.log(A**2 * B / sp.sqrt(C))
    expanded = 2 * sp.log(A) + sp.log(B) - sp.log(C) / 2
    points = choose_points([condensed, expanded], ABC)
    assert agrees(
        fingerprint_at(condensed, ABC, points),
        fingerprint_at(expanded, ABC, points),
    )


def test_multivariable_catches_wrong_coefficient():
    condensed = sp.log(A**2 * B / sp.sqrt(C))
    wrong = 2 * sp.log(A) + sp.log(B) - sp.log(C)  # forgot the half
    points = choose_points([condensed, wrong], ABC)
    assert not agrees(
        fingerprint_at(condensed, ABC, points),
        fingerprint_at(wrong, ABC, points),
    )


def test_variables_are_decorrelated():
    """a + b must not pass as 2*a.

    If every sample gave a == b the two would agree at every point, and any
    problem in more than one variable would be gradeable by guessing.
    """
    points = choose_points([A + B], ABC)
    assert not agrees(
        fingerprint_at(A + B, ABC, points),
        fingerprint_at(2 * A, ABC, points),
    )
    # And no sample point should have two equal coordinates in the first place.
    for point in points:
        assert len(set(point)) == len(point), f"repeated value in {point}"


def test_fingerprint_records_its_variables():
    fingerprint = fp(A * B, ABC)
    assert fingerprint.variables == ("a", "b", "c")
    assert all(len(point) == 3 for point in fingerprint.points)


def test_fingerprints_over_different_variables_never_agree():
    one = fp(X, ONE_VAR)
    many = fp(A, ABC)
    assert not agrees(one, many)


def test_unknown_symbol_is_a_build_error():
    """An expression mentioning an undeclared variable is a template bug."""
    with pytest.raises(ValueError, match="free symbols"):
        choose_points([X + A], ONE_VAR)


# --- Domain safety ---------------------------------------------------------


def test_evaluate_rejects_pole():
    assert evaluate(1 / X, ONE_VAR, (sp.Integer(0),)) is None


def test_evaluate_rejects_complex_result():
    assert evaluate(sp.sqrt(X), ONE_VAR, (sp.Rational(-1, 2),)) is None


def test_evaluate_rejects_log_of_negative():
    assert evaluate(sp.log(X), ONE_VAR, (sp.Rational(-1, 3),)) is None


def test_chosen_points_avoid_singularities():
    expr = 1 / (X - sp.Rational(3, 7))  # a pole exactly on a candidate value
    points = choose_points([expr], ONE_VAR)
    assert (sp.Rational(3, 7),) not in points
    for point in points:
        assert evaluate(expr, ONE_VAR, point) is not None


def test_positive_domain_only_samples_positives():
    points = choose_points([sp.log(X)], POSITIVE_X)
    assert all(point[0] > 0 for point in points)


def test_choose_points_raises_when_domain_too_narrow():
    with pytest.raises(ValueError, match="sample points"):
        choose_points([sp.log(X - 100)], ONE_VAR)


def test_shared_points_across_answer_and_distractors():
    answer = (6 * X) / (3 * X**2 + 1)
    distractor = 1 / (3 * X**2 + 1)
    points = choose_points([answer, distractor], ONE_VAR)
    assert (
        fingerprint_at(answer, ONE_VAR, points).points
        == fingerprint_at(distractor, ONE_VAR, points).points
    )


# --- Custom interval pools -------------------------------------------------


@pytest.mark.parametrize("high", [1, sp.Rational(1, 2), sp.Rational(1, 4)])
def test_interval_pool_stays_inside_its_interval(high):
    pool = interval_pool(0, high)
    assert len(pool) == len(set(pool)) == 20
    assert all(0 < value <= high for value in pool)


def test_interval_pool_rejects_empty_interval():
    with pytest.raises(ValueError, match="high > low"):
        interval_pool(1, 1)


def test_narrow_domain_becomes_sampleable_with_a_pool():
    """sqrt(1/x - 4) is real only on (0, 1/4] - unreachable from either default
    pool, which is what `Variable.pool` exists for."""
    expr = sp.sqrt(1 / X - 4)
    with pytest.raises(ValueError):
        choose_points([expr], ONE_VAR)

    narrow = (Variable("x", Domain.POSITIVE, pool=interval_pool(0, sp.Rational(1, 4))),)
    points = choose_points([expr], narrow)
    assert len(points) == 8


# --- The +C mechanism, for Act III ----------------------------------------


def test_up_to_constant_accepts_any_offset():
    antiderivative = X**3 / 3
    points = choose_points([antiderivative], ONE_VAR)
    ours = fingerprint_at(antiderivative, ONE_VAR, points, up_to_constant=True)
    for offset in (0, 1, -7, sp.Rational(5, 3)):
        theirs = fingerprint_at(
            antiderivative + offset, ONE_VAR, points, up_to_constant=True
        )
        assert agrees(ours, theirs), f"offset {offset} should be accepted"


def test_up_to_constant_still_rejects_wrong_function():
    points = choose_points([X**3 / 3, X**2 / 2], ONE_VAR)
    ours = fingerprint_at(X**3 / 3, ONE_VAR, points, up_to_constant=True)
    theirs = fingerprint_at(X**2 / 2 + 4, ONE_VAR, points, up_to_constant=True)
    assert not agrees(ours, theirs)


# --- Reproducibility -------------------------------------------------------


@pytest.mark.parametrize("pool", [SIGNED_POOL, POSITIVE_POOL])
def test_pools_are_distinct_and_nonzero(pool):
    assert len(pool) == len(set(pool))
    assert all(value != 0 for value in pool)
    # No integers: integer points make too many templates collide at nice values.
    assert all(value.q != 1 for value in pool)


def test_positive_pool_is_positive():
    assert all(value > 0 for value in POSITIVE_POOL)


def test_fingerprint_is_stable_across_runs():
    expr = 6 * X * sp.cos(3 * X**2 + 1)
    assert fp(expr).ys == fp(expr).ys
