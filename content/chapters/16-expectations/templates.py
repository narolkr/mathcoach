"""Chapter 16 - Areas, Averages, Expectations: definite and improper integrals.

The chapter that makes probability notation legible. Every ∫p(x)dx in an ML
paper is this, and the roadmap's gate asks specifically why a density must
integrate to 1.

Improper integrals are graded free-form as numbers; the conceptual half is
choices, because "why must a density integrate to 1" has no expression as an
answer.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign, positive
from mathcoach.latex import definite_integral_prompt, num, to_katex
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol

POSITIVE_X = positive("x")
x_pos = POSITIVE_X[0].symbol


def _m(expr: sp.Expr) -> str:
    return f"${to_katex(expr)}$"


def improper_exponential(rate: int) -> Instance:
    """∫₀^∞ rate·e^(-rate·x) dx = 1. The exponential density, normalised."""
    integrand = rate * sp.exp(-rate * x_pos)
    answer = sp.Integer(1)

    from_sympy = sp.integrate(rate * sp.exp(-rate * x), (x, 0, sp.oo))
    if sp.simplify(from_sympy - answer) != 0:
        raise ValueError(
            f"improper_exponential({rate}): expected 1, SymPy says {from_sympy}"
        )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=definite_integral_prompt(integrand, "0", r"\infty"),
        slug=f"r{rate}",
        instruction="Evaluate. It converges.",
        hints=(
            "An infinite upper limit means a limit: integrate to b, then let b "
            "go to infinity.",
            f"An antiderivative is {_m(-sp.exp(-rate * x_pos))}.",
            "At the upper limit e^(−rate·b) goes to 0, so only the lower-limit "
            "term survives.",
        ),
        steps=(
            (
                r"\lim_{b \to \infty}\left[" + to_katex(-sp.exp(-rate * x_pos))
                + r"\right]_{0}^{b}",
                "An improper integral is defined as this limit - which is why "
                "chapter 6's limits at infinity were worth having.",
            ),
            (
                r"\lim_{b \to \infty}\left(-e^{-" + num(rate) + r"b} + 1\right)",
                "The first term goes to zero.",
            ),
            (
                to_katex(answer),
                f"Exactly 1 - which is not a coincidence. This is the "
                f"exponential density with rate {rate}, and the {rate} out "
                f"front is there precisely to make the total come to 1.",
            ),
        ),
        distractors=(
            (
                "diverges-guess",
                sp.Integer(0),
                "The area is not zero - the function is positive everywhere. An "
                "unbounded region can still have finite, nonzero area, which is "
                "the whole surprise of improper integrals.",
            ),
        ),
    )


def expectation_of_exponential(rate: int) -> Instance:
    """∫₀^∞ x·rate·e^(-rate·x) dx = 1/rate. The mean, as an integral."""
    integrand = rate * x_pos * sp.exp(-rate * x_pos)
    answer = sp.Rational(1, rate)

    from_sympy = sp.integrate(rate * x * sp.exp(-rate * x), (x, 0, sp.oo))
    if sp.simplify(from_sympy - answer) != 0:
        raise ValueError(
            f"expectation_of_exponential({rate}): expected {answer}, SymPy says "
            f"{from_sympy}"
        )

    return Instance(
        expr=answer,
        answer=answer,
        prompt_latex=definite_integral_prompt(integrand, "0", r"\infty"),
        slug=f"r{rate}",
        instruction="Evaluate. This is E[X] for that density.",
        hints=(
            "There's an x multiplying the density, so this needs by parts - "
            "chapter 15.",
            "Differentiate the x, integrate the exponential. The x becomes 1 and "
            "the problem reduces to the previous one.",
            f"The answer is 1/{rate}: a higher rate means events arrive sooner, "
            f"so the mean waiting time is smaller.",
        ),
        steps=(
            (
                r"\int_{0}^{\infty} x\,p(x)\,dx",
                "This is the definition of an expectation: every value x, "
                "weighted by how much probability density sits there.",
            ),
            (
                to_katex(answer),
                f"By parts, then the previous result. The mean of an exponential "
                f"with rate {rate} is 1/{rate}.",
            ),
        ),
        distractors=(
            (
                "reciprocal-flipped",
                sp.Integer(rate),
                f"Upside down. A larger rate means events arrive *sooner*, so "
                f"the average wait is 1/{rate}, not {rate}.",
            ),
        )
        if rate != 1
        else (),
    )


def why_densities_normalise(kind: str) -> Instance:
    """The roadmap's gate: why a density integrates to 1, and what E[X] is."""
    if kind == "normalise":
        prompt = r"\int_{-\infty}^{\infty} p(x)\,dx = 1"
        correct = "certainty"
        options = (
            Choice(
                id="certainty",
                label=(
                    "the outcome is certain to be somewhere, and total "
                    "probability is 1"
                ),
                feedback=(
                    "The integral over all possible values is the probability "
                    "that *something* happens, which is 1 by definition. That is "
                    "the only reason for the condition - and it is why densities "
                    "come with normalising constants like the 1/√(2π) in a "
                    "Gaussian, or softmax's denominator. Those constants exist "
                    "solely to make this integral come to 1."
                ),
            ),
            Choice(
                id="max",
                label="p(x) never exceeds 1",
                feedback=(
                    "A density may exceed 1 - a narrow spike can be very tall. "
                    "It's the *area* that is capped at 1, not the height. That "
                    "is the difference between a density and a probability."
                ),
            ),
            Choice(
                id="mean",
                label="the mean of the distribution is 1",
                feedback=(
                    "The mean is ∫x·p(x)dx, a different integral entirely, and "
                    "it can be anything at all."
                ),
            ),
            Choice(
                id="convention",
                label="it is a convention that makes the algebra tidier",
                feedback=(
                    "It isn't a convention - it's forced. Without it the "
                    "function would not describe probabilities, because the "
                    "probabilities of all outcomes would not add up to one."
                ),
            ),
        )
        hints = (
            "What does the integral of a density over *all* values represent?",
        )
        steps = (
            (
                r"P(a \le X \le b) = \int_{a}^{b} p(x)\,dx",
                "A density's integral over a region is the probability of "
                "landing in it. Over everything, that must be 1.",
            ),
        )
    else:
        prompt = r"E[X] = \int x\,p(x)\,dx"
        correct = "weighted"
        options = (
            Choice(
                id="weighted",
                label="a weighted average of x, weighted by probability density",
                feedback=(
                    "This is the continuous version of Σ x·P(x). Each possible "
                    "value contributes in proportion to how likely it is. Once "
                    "you read the integral that way, the notation in ML papers "
                    "stops being decorative: E[·] is always a weighted average, "
                    "and the weights are always the probabilities."
                ),
            ),
            Choice(
                id="area",
                label="the area under the density curve",
                feedback=(
                    "That's ∫p(x)dx without the x, and it equals 1 for every "
                    "density - so it carries no information about this "
                    "particular distribution. The x is what makes it a mean."
                ),
            ),
            Choice(
                id="mode",
                label="the most likely value of x",
                feedback=(
                    "That's the mode - where p is largest. Mean and mode differ "
                    "for any skewed distribution, and the exponential is a good "
                    "example: its mode is 0 and its mean is 1/rate."
                ),
            ),
            Choice(
                id="median",
                label="the value with half the probability either side",
                feedback=(
                    "That's the median, defined by ∫ up to it equalling 1/2. "
                    "Also not the mean, and also different whenever the "
                    "distribution is skewed."
                ),
            ),
        )
        hints = (
            "Compare it with the discrete case: E[X] = Σ x·P(x). What is the "
            "integral doing differently?",
        )
        steps = (
            (
                r"\sum_i x_i P(x_i) \;\longrightarrow\; \int x\,p(x)\,dx",
                "The sum becomes an integral, the probabilities become a "
                "density. Same idea: average the values, weighted by how likely "
                "each one is.",
            ),
        )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=prompt,
        choices=options,
        correct_choice=correct,
        slug=kind,
        instruction="What does this say?",
        hints=hints,
        steps=steps,
    )


TEMPLATES: tuple[Template, ...] = (
    Template(
        id="ae-improper",
        tier="medium",
        variables=POSITIVE_X,
        shape="∫₀^∞ λe^(-λx) dx",
        skill="improper integrals, and why they can converge",
        build=improper_exponential,
        params=({"rate": 1}, {"rate": 2}, {"rate": 3}),
    ),
    Template(
        id="ae-expectation",
        tier="hard",
        variables=POSITIVE_X,
        shape="∫₀^∞ x·λe^(-λx) dx",
        skill="an expectation computed as an integral",
        build=expectation_of_exponential,
        params=({"rate": 1}, {"rate": 2}, {"rate": 4}),
    ),
    Template(
        id="ae-why",
        tier="medium",
        variables=VARS,
        shape="why densities normalise; what E[X] is",
        skill="reading probability notation",
        build=why_densities_normalise,
        params=({"kind": "normalise"}, {"kind": "expectation"}),
    ),
)
