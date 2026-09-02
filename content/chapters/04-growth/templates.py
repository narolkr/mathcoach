"""Chapter 4 - Growth and Its Undoing: exponentials and logarithms.

Weighted heavily on purpose. Softmax, cross-entropy, log-loss, log-likelihood,
logits, log-sum-exp, KL divergence and perplexity are all this chapter, and more
AI-maths confusion traces back to shaky log fluency than to anything in calculus
proper.

Two grading shapes, chosen for the same reason as elsewhere:

- **Expanding** a log asks for the *coefficients* of ln a, ln b, ln c in slots.
  A free-form answer could be satisfied by pasting the question back, since
  ln(a²b/√c) and 2ln a + ln b − ½ln c are the same number.
- **Condensing** a log asks for the argument as a free-form expression, which is
  safe: the argument is not equal to the sum of logs it came from.

This is the first chapter with three variables, all restricted to positive
values - logs of negatives aren't real.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, positive
from mathcoach.latex import coeff, frac, num, power, root, to_katex
from mathcoach.schema import Choice

ABC = positive("a", "b", "c")
a_sym, b_sym, c_sym = (variable.symbol for variable in ABC)

X_POS = positive("x")
x_pos = X_POS[0].symbol

ASSUME_ABC = "Assume a, b, c > 0."


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


# ---------------------------------------------------------------------------
# Expanding a logarithm
# ---------------------------------------------------------------------------


def expand_log(pa: int, pb: int, root_c: int) -> Instance:
    """ln(a^pa · b^pb / c^(1/root_c)) - the chapter gate's shape.

    Answered as the three coefficients, because the expanded and unexpanded
    forms are the same number.
    """
    inner = a_sym**pa * b_sym**pb / c_sym ** sp.Rational(1, root_c)
    expr = sp.log(inner)

    coeff_a = sp.Integer(pa)
    coeff_b = sp.Integer(pb)
    coeff_c = -sp.Rational(1, root_c)
    answer = coeff_a * sp.log(a_sym) + coeff_b * sp.log(b_sym) + coeff_c * sp.log(c_sym)

    numerator = power("a", pa) + power("b", pb) if pb != 1 else power("a", pa) + "b"
    prompt = (
        r"\ln\left("
        + frac(numerator, root("c") if root_c == 2 else root("c", root_c))
        + r"\right)"
    )

    return Instance(
        expr=expr,
        answer=answer,
        prompt_latex=prompt,
        assumption=ASSUME_ABC,
        slug=f"pa{pa}pb{pb}rc{root_c}",
        instruction=(
            "Expand into separate logs: k₁·ln a + k₂·ln b + k₃·ln c. "
            "Give k₁, k₂, k₃."
        ),
        slots=(
            ("coefficient of ln a", coeff_a, "a number"),
            ("coefficient of ln b", coeff_b, "a number"),
            ("coefficient of ln c", coeff_c, "a number, sign included"),
        ),
        hints=(
            "Three laws, applied in any order: a product becomes a sum, a "
            "quotient becomes a difference, and a power becomes a multiplier.",
            "The c is under a root, and a root is a fractional power. What power?",
            f"c is to the power {_m(sp.Rational(1, root_c))}, and it's in the "
            f"*denominator* - so its coefficient is negative.",
            f"So you get {_m(answer)}.",
        ),
        steps=(
            (
                r"\ln\left(" + numerator + r"\right) - \ln\left("
                + (root("c") if root_c == 2 else root("c", root_c))
                + r"\right)",
                "A quotient inside a log becomes a difference of logs.",
            ),
            (
                r"\ln\left(" + power("a", pa) + r"\right) + \ln\left("
                + power("b", pb) + r"\right) - \ln\left("
                + power("c", sp.Rational(1, root_c)) + r"\right)",
                "A product becomes a sum, and the root becomes a fractional "
                "power.",
            ),
            (
                to_katex(answer),
                "Finally, each power comes out as a multiplier.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Condensing - free-form is safe here
# ---------------------------------------------------------------------------


def condense_log(pa: int, pb: int, pc: int) -> Instance:
    """pa·ln a + pb·ln b - pc·ln c written as a single ln. Asked for the argument."""
    argument = a_sym**pa * b_sym**pb / c_sym**pc
    expr = argument

    # `coeff` drops a unit multiplier, so this reads "ln b" rather than "1 ln b".
    prompt = (
        f"{coeff(pa, r'\ln a')} + {coeff(pb, r'\ln b')} - {coeff(pc, r'\ln c')}"
        r" \;=\; \ln\left(\;?\;\right)"
    )

    return Instance(
        expr=expr,
        answer=argument,
        prompt_latex=prompt,
        assumption=ASSUME_ABC,
        slug=f"pa{pa}pb{pb}pc{pc}",
        instruction="Write the whole thing as a single logarithm. What goes inside?",
        hints=(
            "Run the three log laws backwards. A multiplier in front of a log "
            "becomes a power inside it.",
            "Sums become products; differences become quotients.",
            f"So the argument is {_m(argument)}.",
        ),
        steps=(
            (
                r"\ln\left(" + power("a", pa) + r"\right) + \ln\left("
                + power("b", pb) + r"\right) - \ln\left(" + power("c", pc)
                + r"\right)",
                "Each multiplier goes back inside as a power.",
            ),
            (
                r"\ln\left(" + to_katex(argument) + r"\right)",
                "Sum becomes product, difference becomes quotient.",
            ),
        ),
        distractors=(
            (
                "sum-not-product",
                a_sym**pa + b_sym**pb - c_sym**pc,
                "You kept the additions and subtractions. Adding logs "
                "*multiplies* their arguments - that's the whole reason logs are "
                "useful.",
            ),
            (
                "coefficients-as-factors",
                pa * a_sym * pb * b_sym / (pc * c_sym),
                "The numbers in front became multipliers instead of powers. "
                "k·ln a is ln(a^k), not k·a.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Solving with logs
# ---------------------------------------------------------------------------


def solve_exponential(k: int, target: int) -> Instance:
    """Solve e^(k·x) = target for x."""
    answer = sp.log(target) / k
    prompt = f"e^{{{coeff(k, 'x')}}} = {num(target)}"

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=prompt,
        slug=f"k{k}t{target}".replace("-", "m"),
        instruction="Solve for x. Leave the answer exact.",
        hints=(
            "The unknown is stuck in an exponent. What operation undoes an "
            "exponential?",
            "Take ln of both sides. ln(e^u) = u, exactly - that is what makes e "
            "the natural base.",
            f"So {coeff(k, 'x')} = ln {target}, and then divide.",
        ),
        steps=(
            (
                f"\\ln\\left(e^{{{coeff(k, 'x')}}}\\right) = \\ln {num(target)}",
                "Take the natural log of both sides.",
            ),
            (
                f"{coeff(k, 'x')} = \\ln {num(target)}",
                "ln and exp undo each other exactly.",
            ),
            (to_katex(answer), f"Divide by {k}."),
        ),
        distractors=_solve_exponential_distractors(k, target),
    )


def _solve_exponential_distractors(
    k: int, target: int
) -> tuple[tuple[str, sp.Expr, str], ...]:
    """The misconceptions, minus any that leave the reals.

    `log-of-quotient` is only usable when target/k is positive: for k = -1 it
    would be ln(-4), which has no real value and therefore no fingerprint to
    compare against.
    """
    distractors: list[tuple[str, sp.Expr, str]] = [
        (
            "forgot-divide",
            sp.log(target),
            f"You took the log correctly but never divided by the {k} in the "
            f"exponent.",
        )
    ]
    if sp.Rational(target, k) > 0:
        distractors.append(
            (
                "log-of-quotient",
                sp.log(sp.Rational(target, k)),
                f"ln({target})/{k} is not ln({target}/{k}). Dividing *after* the "
                f"log is not the same as dividing inside it.",
            )
        )
    return tuple(distractors)


# ---------------------------------------------------------------------------
# Why logs matter - conceptual, so: choices
# ---------------------------------------------------------------------------


def why_log_likelihood(count: int) -> Instance:
    """The reason log-likelihood exists, as a multiple-choice check."""
    choices = (
        Choice(
            id="underflow",
            label=(
                "Multiplying that many probabilities underflows to zero in "
                "floating point; summing their logs does not."
            ),
            feedback=(
                f"{count} probabilities each around 0.5 multiply to "
                f"about 10^-{int(count * 0.301)}, far below what a float64 can "
                "represent - it becomes exactly 0.0 and all information is "
                "lost. Logs turn the product into a sum of manageable numbers, "
                "and because ln is increasing, whatever maximises the "
                "likelihood also maximises its log."
            ),
        ),
        Choice(
            id="faster",
            label="Addition is faster than multiplication on a CPU.",
            feedback=(
                "Marginally true and completely beside the point. The reason is "
                "numerical range, not speed - and computing a logarithm costs "
                "far more than the multiplication it replaces."
            ),
        ),
        Choice(
            id="different-answer",
            label="The log gives a different, better maximum.",
            feedback=(
                "No - and this matters. ln is strictly increasing, so it moves "
                "the maximum nowhere at all. That is precisely why the "
                "substitution is legitimate: you get the same answer, computed "
                "safely."
            ),
        ),
        Choice(
            id="makes-linear",
            label="It makes the model linear.",
            feedback=(
                "It doesn't. Taking a log of the likelihood says nothing about "
                "whether the model is linear in its parameters."
            ),
        ),
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=(
            r"\prod_{i=1}^{" + str(count) + r"} p_i \quad\text{vs}\quad "
            r"\sum_{i=1}^{" + str(count) + r"} \ln p_i"
        ),
        choices=choices,
        correct_choice="underflow",
        slug=f"n{count}",
        instruction=(
            f"Fitting a model to {count} data points means maximising a product "
            f"of {count} probabilities. Everyone maximises the sum of their logs "
            f"instead. Why?"
        ),
        hints=(
            "Think about the actual size of the number you'd be computing.",
            f"Each p is below 1. What does multiplying {count} of them give?",
        ),
        steps=(
            (
                r"\ln\left(\prod_i p_i\right) = \sum_i \ln p_i",
                "The log of a product is the sum of the logs - chapter 4's first "
                "law, doing real work.",
            ),
        ),
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="gu-expand-log",
        tier="medium",
        variables=ABC,
        shape="ln(a^p · b^q / c^(1/n))",
        skill="expanding a logarithm",
        build=expand_log,
        params=(
            # The roadmap's gate: ln(a²b/√c).
            {"pa": 2, "pb": 1, "root_c": 2},
            {"pa": 3, "pb": 2, "root_c": 2},
            {"pa": 1, "pb": 4, "root_c": 3},
        ),
    ),
    Template(
        id="gu-condense-log",
        tier="medium",
        variables=ABC,
        shape="p·ln a + q·ln b − r·ln c",
        skill="condensing logs into one",
        build=condense_log,
        params=(
            {"pa": 2, "pb": 1, "pc": 3},
            {"pa": 4, "pb": 2, "pc": 1},
            {"pa": 1, "pb": 3, "pc": 2},
        ),
    ),
    Template(
        id="gu-solve-exponential",
        tier="easy",
        variables=X_POS,
        shape="e^(kx) = t",
        skill="undoing an exponential with a log",
        build=solve_exponential,
        params=(
            {"k": 2, "target": 7},
            {"k": 3, "target": 5},
            {"k": -1, "target": 4},
        ),
    ),
    Template(
        id="gu-why-logs",
        tier="easy",
        variables=X_POS,
        shape="why log-likelihood",
        skill="why logs appear throughout ML",
        build=why_log_likelihood,
        params=({"count": 10000}, {"count": 50000}),
    ),
)
