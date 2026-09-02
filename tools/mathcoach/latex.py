"""SymPy -> KaTeX-safe LaTeX, plus helpers for authoring prompts by hand.

KaTeX is stricter than full LaTeX. Everything emitted here has to survive
`katex.renderToString(..., {strict: true, throwOnError: true})`, which the
frontend check script enforces over every string in the content bundle.

## Why prompts are sometimes authored rather than rendered

SymPy evaluates as it builds. `sp.sqrt(72)` *is* `6*sqrt(2)`, and
`-(5 - 3*(2 - x))` *is* `1 - 3*x` - there is no unsimplified object to render.
For differentiation chapters that is harmless, because the prompt and the answer
are different expressions. For algebra chapters, where the task IS the
simplification, rendering the SymPy object would print the answer as the
question.

So algebra templates set `Instance.prompt_latex` using the builders below, and
keep the SymPy `expr` purely for the numeric equivalence check. The check still
earns its keep: it verifies the answer against an expression derived
independently from the same parameters.
"""

from __future__ import annotations

import re

import sympy as sp

# sympy writes natural log as \log; mathematicians reading this app expect \ln.
# Applied as a whole-token replacement so it cannot corrupt \log_{10} or similar.
_LOG_TOKEN = re.compile(r"\\log(?![a-zA-Z])")

# SymPy emits \operatorname{atan}; mathematicians write \arctan. Same for the
# other inverse trig functions, which appear from chapter 12 onwards.
_INVERSE_TRIG = re.compile(r"\\operatorname\{a(sin|cos|tan)\}")

# Constructs KaTeX rejects outright. If a template ever produces one we want a
# loud build failure rather than a silently broken level.
_FORBIDDEN = (
    r"\begin{array}",
    r"\substack",
    r"\mathchoice",
    r"\intertext",
)


def to_katex(expr: sp.Expr) -> str:
    """Render a SymPy expression as a KaTeX-safe LaTeX string."""
    # Default mul_symbol (a thin space) reads better than \cdot everywhere.
    out = sp.latex(expr, ln_notation=True, fold_short_frac=False)
    out = _LOG_TOKEN.sub(r"\\ln", out)
    out = _INVERSE_TRIG.sub(r"\\arc\1", out)
    assert_katex_safe(out)
    return out


def derivative_prompt(expr: sp.Expr) -> str:
    """The `d/dx (...)` prompt shown at the top of a differentiation level."""
    return r"\frac{d}{dx}\left[" + to_katex(expr) + r"\right]"


def assert_katex_safe(latex: str) -> None:
    for bad in _FORBIDDEN:
        if bad in latex:
            raise ValueError(f"LaTeX contains KaTeX-hostile construct {bad!r}: {latex}")


# ---------------------------------------------------------------------------
# Authoring helpers
# ---------------------------------------------------------------------------


def num(value: int | sp.Rational | sp.Expr) -> str:
    """A number, as LaTeX. Rationals become \\frac, negatives keep their sign."""
    return to_katex(sp.nsimplify(value) if isinstance(value, int) else value)


def signed(value: int | sp.Rational, *, leading: bool = False) -> str:
    """`+ 3` / `- 3`, for joining terms. `leading=True` drops a leading plus."""
    rational = sp.Rational(value)
    if rational < 0:
        return f"- {num(abs(rational))}"
    return num(rational) if leading else f"+ {num(rational)}"


def coeff(value: int | sp.Rational, symbol: str) -> str:
    """`3x`, `-x`, `x`, or `""` when the coefficient is zero."""
    rational = sp.Rational(value)
    if rational == 0:
        return ""
    if rational == 1:
        return symbol
    if rational == -1:
        return f"-{symbol}"
    return f"{num(rational)}{symbol}"


def power(base: str, exponent: int | sp.Rational) -> str:
    """`x^{3}`, `x^{-2/3}`, or just `x` when the exponent is 1."""
    rational = sp.Rational(exponent)
    if rational == 1:
        return base
    return f"{base}^{{{num(rational)}}}"


def product(*parts: str) -> str:
    """Join non-empty factors with a thin space."""
    return r"\,".join(part for part in parts if part)


def frac(numerator: str, denominator: str) -> str:
    return rf"\frac{{{numerator}}}{{{denominator}}}"


def paren(inner: str) -> str:
    return rf"\left({inner}\right)"


def bracket(inner: str) -> str:
    return rf"\left[{inner}\right]"


def root(radicand: str, degree: int = 2) -> str:
    if degree == 2:
        return rf"\sqrt{{{radicand}}}"
    return rf"\sqrt[{degree}]{{{radicand}}}"


def linear(slope: int | sp.Rational, intercept: int | sp.Rational, symbol: str = "x") -> str:
    """`3x - 2`, handling every sign and unit-coefficient case."""
    head = coeff(slope, symbol)
    if not head:
        return num(intercept)
    if sp.Rational(intercept) == 0:
        return head
    return f"{head} {signed(intercept)}"


def limit_prompt(expr: sp.Expr, variable: str, approaching: str) -> str:
    r"""`\lim_{x \to 0} f(x)`. `approaching` is LaTeX: "0", "\infty", "2^{-}"."""
    return (
        r"\lim_{" + variable + r" \to " + approaching + "} " + to_katex(expr)
    )


def difference_quotient(f_latex: str) -> str:
    """The definition of the derivative, with a named function."""
    return (
        r"\lim_{h \to 0} \frac{" + f_latex + "(x+h) - " + f_latex + "(x)}{h}"
    )


def integral_prompt(expr: sp.Expr, variable: str = "x") -> str:
    r"""`\int f(x)\,dx` - an indefinite integral."""
    return r"\int " + to_katex(expr) + r"\,d" + variable


def definite_integral_prompt(
    expr: sp.Expr,
    lower: str,
    upper: str,
    variable: str = "x",
) -> str:
    r"""`\int_a^b f(x)\,dx`. Bounds are LaTeX, so "\infty" works."""
    return (
        r"\int_{" + lower + "}^{" + upper + "} "
        + to_katex(expr)
        + r"\,d" + variable
    )


def evaluated_at(expr_latex: str, lower: str, upper: str) -> str:
    r"""`\left[F(x)\right]_a^b`, for showing the FTC step."""
    return (
        r"\left[" + expr_latex + r"\right]_{" + lower + "}^{" + upper + "}"
    )


def second_derivative(f_latex: str = "f") -> str:
    return f_latex + "''(x)"


def polynomial_terms(terms: list[tuple[int | sp.Rational, str]]) -> str:
    """Join `(coefficient, symbol-or-power)` pairs into a signed sum."""
    pieces: list[str] = []
    for index, (value, symbol) in enumerate(terms):
        rational = sp.Rational(value)
        if rational == 0:
            continue
        body = coeff(abs(rational), symbol) if symbol else num(abs(rational))
        sign = "-" if rational < 0 else ("" if index == 0 or not pieces else "+")
        pieces.append(f"{sign} {body}".strip() if sign else body)
    return " ".join(pieces) if pieces else "0"
