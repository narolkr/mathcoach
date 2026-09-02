"""Chapter 5 - Just Enough Circles: only the trigonometry later chapters need.

Deliberately shallow. Trig matters far less for AI than for a physics degree -
positional encodings and Fourier features, and little else. The roadmap says to
resist going deeper here and spend the time on chapter 4 instead.

Almost everything is multiple choice, for a specific reason: this is a *recall*
chapter, and recall cannot be graded free-form. Asked to type sin(π/6), a
learner could type `sin(pi/6)` and the grader would evaluate it to 0.5 and mark
it correct - having tested nothing at all. Choices make the recall real.
"""

from __future__ import annotations

import sympy as sp

from mathcoach.generator import Instance, Template, any_sign
from mathcoach.latex import to_katex
from mathcoach.schema import Choice

VARS = any_sign("x")
x = VARS[0].symbol

# The only angles worth knowing cold, per the chapter gate.
ANGLES: dict[str, sp.Expr] = {
    "0": sp.Integer(0),
    r"\frac{\pi}{6}": sp.pi / 6,
    r"\frac{\pi}{4}": sp.pi / 4,
    r"\frac{\pi}{3}": sp.pi / 3,
    r"\frac{\pi}{2}": sp.pi / 2,
}

# The five values these angles produce, which is the whole point: the answers
# repeat, so the distractors are always the *other* correct-looking values.
EXACT_VALUES: tuple[sp.Expr, ...] = (
    sp.Integer(0),
    sp.Rational(1, 2),
    sp.sqrt(2) / 2,
    sp.sqrt(3) / 2,
    sp.Integer(1),
)


def exact_trig_value(angle_latex: str, function: str) -> Instance:
    """sin or cos of one of the five angles. Distractors are the other values."""
    angle = ANGLES[angle_latex]
    trig = sp.sin if function == "sin" else sp.cos
    value = sp.simplify(trig(angle))

    # Every option is a value that genuinely appears in this table, so getting
    # it right means knowing the table rather than eliminating absurdities.
    options: list[Choice] = []
    for candidate in EXACT_VALUES:
        is_correct = sp.simplify(candidate - value) == 0
        options.append(
            Choice(
                id=str(candidate).replace(" ", ""),
                label=to_katex(candidate),
                is_latex=True,
                # No "Correct." prefix: the interface already renders "Yes."
                # before this, and the wrong-pick branch does not restate the
                # answer, because the correct option's feedback follows it.
                feedback=(
                    (
                        f"On the unit circle, {function} of ${angle_latex}$ is "
                        f"the {'vertical' if function == 'sin' else 'horizontal'} "
                        f"coordinate, and that is ${to_katex(value)}$."
                    )
                    if is_correct
                    else (
                        "That is a real value from this table, but it belongs to "
                        "a different angle."
                    )
                ),
            )
        )

    correct_id = next(
        option.id
        for option, candidate in zip(options, EXACT_VALUES)
        if sp.simplify(candidate - value) == 0
    )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=rf"\{function}\left({angle_latex}\right)",
        choices=tuple(options),
        correct_choice=correct_id,
        slug=f"{function}-{angle_latex.replace(chr(92), '').replace('{', '').replace('}', '').replace('frac', '').replace('pi', 'pi')}",
        instruction="From memory. No unit circle sketch, no calculator.",
        hints=(
            "Sine is the vertical coordinate on the unit circle; cosine is the "
            "horizontal one.",
            "At 0 the point is (1, 0). At π/2 it is (0, 1). Everything else sits "
            "between those, and π/4 is the symmetric one where both match.",
        ),
        steps=(
            (
                to_katex(value),
                f"{function} of ${angle_latex}$. These five angles are the whole "
                f"list worth memorising.",
            ),
        ),
    )


def pythagorean_identity(coefficient: int, function: str) -> Instance:
    """Simplify 1 - sin²(kx) or 1 - cos²(kx). Choices, since the forms are equal."""
    inner = coefficient * x
    if function == "sin":
        given = 1 - sp.sin(inner) ** 2
        answer = sp.cos(inner) ** 2
        other = "cos"
    else:
        given = 1 - sp.cos(inner) ** 2
        answer = sp.sin(inner) ** 2
        other = "sin"

    options = (
        Choice(
            id="correct",
            label=to_katex(answer),
            is_latex=True,
            feedback=(
                f"sin² + cos² = 1 rearranges to 1 − {function}² = "
                f"{other}², and the argument comes along unchanged."
            ),
        ),
        Choice(
            id="unsquared",
            label=to_katex(sp.cos(inner) if other == "cos" else sp.sin(inner)),
            is_latex=True,
            feedback=(
                "The identity is about the *squares*. Dropping the square "
                "changes the function entirely - and it would no longer be "
                "equal to what you started with."
            ),
        ),
        Choice(
            id="same-function",
            label=to_katex(
                sp.sin(inner) ** 2 if function == "sin" else sp.cos(inner) ** 2
            ),
            is_latex=True,
            feedback=(
                f"That's {function}² again. The identity swaps you to the *other* "
                f"function: 1 − {function}² = {other}²."
            ),
        ),
        Choice(
            id="halved-argument",
            label=to_katex(
                (sp.cos(x) if other == "cos" else sp.sin(x)) ** 2
            ),
            is_latex=True,
            feedback=(
                f"Right function, but the argument changed. The identity does "
                f"nothing to the inside - it stays {coefficient}x."
            ),
        ),
    )

    return Instance(
        expr=given,
        prompt_latex=to_katex(given),
        choices=options,
        correct_choice="correct",
        slug=f"{function}k{coefficient}",
        instruction="Simplify using the one trig identity that matters.",
        hints=(
            "There is exactly one identity you need in this whole roadmap.",
            "sin²θ + cos²θ = 1, for any θ at all - including θ = "
            f"{coefficient}x.",
        ),
        steps=(
            (
                r"\sin^{2}\theta + \cos^{2}\theta = 1",
                "The identity, for any argument whatsoever.",
            ),
            (
                to_katex(answer),
                f"Rearranged, with θ = {coefficient}x.",
            ),
        ),
    )


def derivative_relevant_fact(which: str) -> Instance:
    """The two trig facts calculus actually leans on."""
    if which == "sin-over-x":
        prompt = r"\lim_{x \to 0} \frac{\sin x}{x}"
        options = (
            Choice(
                id="one",
                label="1",
                is_latex=True,
                feedback=(
                    "This is the fact that makes d/dx sin x = cos x true. It "
                    "only works in radians, which is why calculus never uses "
                    "degrees."
                ),
            ),
            Choice(
                id="zero",
                label="0",
                is_latex=True,
                feedback=(
                    "Both top and bottom go to 0, so the limit is genuinely "
                    "unclear from inspection - but for small x, sin x is very "
                    "nearly x, so the ratio approaches 1, not 0."
                ),
            ),
            Choice(
                id="undefined",
                label=r"\text{undefined}",
                is_latex=True,
                feedback=(
                    "The *function* is undefined at x = 0, but the limit exists "
                    "anyway. That gap between 'undefined here' and 'has no "
                    "limit here' is what chapter 6 is about."
                ),
            ),
            Choice(
                id="infinity",
                label=r"\infty",
                is_latex=True,
                feedback=(
                    "For small x, sin x is slightly *less* than x, so the ratio "
                    "stays just below 1. It never grows."
                ),
            ),
        )
        correct = "one"
        hints = (
            "Try it with a small number, in radians. What is sin(0.01)/0.01?",
            "For small angles, sin x is very nearly equal to x itself.",
        )
        steps = (
            (
                r"\sin(0.01) \approx 0.00999983",
                "Divide that by 0.01 and you get 0.999983 - already almost 1.",
            ),
        )
    else:
        prompt = r"\frac{d}{dx}\sin x = ?"
        options = (
            Choice(
                id="cos",
                label=r"\cos x",
                is_latex=True,
                feedback=(
                    "And it's only this clean in radians - in degrees you'd pick "
                    "up a factor of π/180, which is the entire reason calculus "
                    "uses radians."
                ),
            ),
            Choice(
                id="minus-cos",
                label=r"-\cos x",
                is_latex=True,
                feedback=(
                    "The minus sign belongs to the other one: d/dx cos x = "
                    "−sin x. Sine differentiates cleanly to cosine."
                ),
            ),
            Choice(
                id="minus-sin",
                label=r"-\sin x",
                is_latex=True,
                feedback=(
                    "That's the *second* derivative of sin x. You went one step "
                    "too far round the cycle."
                ),
            ),
            Choice(
                id="sec",
                label=r"\sec^{2} x",
                is_latex=True,
                feedback="That is the derivative of tan x.",
            ),
        )
        correct = "cos"
        hints = (
            "Picture the sine curve. Where is its slope steepest, and where is "
            "it flat?",
            "Sine is flat at its peak (x = π/2) and steepest at x = 0. Which "
            "function is 0 at π/2 and 1 at 0?",
        )
        steps = (
            (
                r"\cos x",
                "The slope of sine, at every point, is cosine. Chapter 8 proves "
                "it; for now, know it.",
            ),
        )

    return Instance(
        expr=sp.Integer(0),
        prompt_latex=prompt,
        choices=options,
        correct_choice=correct,
        slug=which,
        instruction="One of the two trig facts calculus actually needs.",
        hints=hints,
        steps=steps,
    )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

TEMPLATES: tuple[Template, ...] = (
    Template(
        id="jc-exact-value",
        tier="easy",
        variables=VARS,
        shape="sin/cos of the five angles",
        skill="the unit circle values, from memory",
        build=exact_trig_value,
        params=tuple(
            {"angle_latex": angle, "function": function}
            for function in ("sin", "cos")
            for angle in ANGLES
        ),
    ),
    Template(
        id="jc-identity",
        tier="easy",
        variables=VARS,
        shape="1 - sin²(kx), 1 - cos²(kx)",
        skill="the Pythagorean identity",
        build=pythagorean_identity,
        params=(
            {"coefficient": 2, "function": "sin"},
            {"coefficient": 3, "function": "cos"},
            {"coefficient": 4, "function": "sin"},
        ),
    ),
    Template(
        id="jc-calculus-facts",
        tier="easy",
        variables=VARS,
        shape="the two facts calculus needs",
        skill="why radians, and the derivative of sine",
        build=derivative_relevant_fact,
        params=({"which": "sin-over-x"}, {"which": "derivative"}),
    ),
)
