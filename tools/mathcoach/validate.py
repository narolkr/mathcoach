"""Build-time invariants.

Every one of these is a way a generated problem could be quietly wrong in a
manner the learner would experience as the app being broken - or worse, as
themselves being wrong when they weren't. The build raises on any violation.
"""

from __future__ import annotations

import sympy as sp

from .fingerprint import Variable, agrees, choose_points, fingerprint_at
from .generator import X, Instance, Template
from .latex import assert_katex_safe
from .schema import Bundle, Diagnostic, Problem


class ValidationError(Exception):
    """A generated problem violates an invariant. Never recoverable at runtime."""


# ---------------------------------------------------------------------------
# Instance-level checks
# ---------------------------------------------------------------------------


def check_answer_is_correct(template: Template, inst: Instance) -> None:
    """The stated answer really is the derivative of the stated expression.

    Differentiation templates only. This is the check that catches an algebra
    slip in a template - the one class of bug that would otherwise teach the
    learner something false.
    """
    if inst.answer is None or not template.is_derivative:
        return

    residual = sp.simplify(sp.diff(inst.expr, X) - inst.answer)
    if residual != 0:
        raise ValidationError(
            f"{template.id}/{inst.slug}: stated answer is not the derivative.\n"
            f"  d/dx({inst.expr}) = {sp.simplify(sp.diff(inst.expr, X))}\n"
            f"  template says      = {inst.answer}\n"
            f"  difference         = {residual}"
        )


def check_antiderivative_is_correct(template: Template, inst: Instance) -> None:
    """Differentiating the stated antiderivative gives back the integrand.

    Checked this way round on purpose. SymPy's `integrate` is far less reliable
    than its `diff` - it can return unevaluated integrals, pick a different but
    equivalent form, or simply fail - whereas differentiation is mechanical and
    total. Differentiating the answer back is both cheap and complete.
    """
    if inst.answer is None or not template.integrates:
        return

    # Integration templates may use a positive-domain symbol, so differentiate
    # with respect to whichever single variable the template declared.
    if len(template.variables) != 1:
        raise ValidationError(
            f"{template.id}: integration templates must declare exactly one "
            f"variable, got {[v.name for v in template.variables]}"
        )
    variable = template.variables[0].symbol

    residual = sp.simplify(sp.diff(inst.answer, variable) - inst.expr)
    if residual != 0:
        raise ValidationError(
            f"{template.id}/{inst.slug}: the stated antiderivative is wrong.\n"
            f"  d/d{variable}({inst.answer}) = "
            f"{sp.simplify(sp.diff(inst.answer, variable))}\n"
            f"  integrand              = {inst.expr}\n"
            f"  difference             = {residual}"
        )


def check_answer_matches_prompt(template: Template, inst: Instance) -> None:
    """For algebra templates, the answer must equal the prompt it simplifies.

    Verified numerically over the template's declared domain rather than
    symbolically: `simplify` cannot prove `sqrt(x**2) == x` without knowing x is
    positive, and the whole point of `Domain.POSITIVE` is that positivity lives
    in the sampling rather than in SymPy's assumptions.
    """
    if inst.answer is None or template.is_derivative or template.integrates:
        return
    # Templates whose answer is a *transformation* rather than an equal value
    # (solving for roots, naming coefficients) opt out via slots instead.
    if "not-equal-to-prompt" in template.tags:
        return

    try:
        points = choose_points([inst.expr, inst.answer], template.variables)
    except ValueError as exc:
        raise ValidationError(
            f"{template.id}/{inst.slug}: cannot sample prompt and answer "
            f"together - {exc}"
        ) from exc

    prompt_fp = fingerprint_at(inst.expr, template.variables, points)
    answer_fp = fingerprint_at(inst.answer, template.variables, points)
    if not agrees(prompt_fp, answer_fp):
        raise ValidationError(
            f"{template.id}/{inst.slug}: the stated answer is not equal to the "
            f"expression it claims to simplify.\n"
            f"  prompt = {inst.expr}\n"
            f"  answer = {inst.answer}\n"
            f"  prompt values {[round(v, 6) for v in prompt_fp.ys[:4]]}\n"
            f"  answer values {[round(v, 6) for v in answer_fp.ys[:4]]}"
        )


def check_decomposition(template: Template, inst: Instance) -> None:
    """`inner_deriv` is the derivative of `inner`, and `inner` really is inside."""
    if inst.inner is None:
        return

    if inst.inner_deriv is None:
        raise ValidationError(f"{template.id}/{inst.slug}: inner without inner_deriv")

    residual = sp.simplify(sp.diff(inst.inner, X) - inst.inner_deriv)
    if residual != 0:
        raise ValidationError(
            f"{template.id}/{inst.slug}: inner_deriv is not d(inner)/dx "
            f"(difference {residual})"
        )

    # A "composition" whose inner function is just x is not a chain rule problem.
    if sp.simplify(inst.inner - X) == 0:
        raise ValidationError(
            f"{template.id}/{inst.slug}: inner function is x, so nothing is composed"
        )


def check_distractors_are_wrong(template: Template, inst: Instance) -> None:
    """No distractor is secretly the right answer.

    A collision here would mean telling the learner they made a mistake when
    they hadn't - the single worst failure this app could have.
    """
    if inst.answer is None:
        return
    for did, expr, _ in inst.distractors:
        if sp.simplify(expr - inst.answer) == 0:
            raise ValidationError(
                f"{template.id}/{inst.slug}: distractor {did!r} is algebraically "
                f"equal to the correct answer ({expr})"
            )


def check_choices(template: Template, inst: Instance) -> None:
    if not inst.choices:
        return
    ids = [choice.id for choice in inst.choices]
    if len(ids) != len(set(ids)):
        raise ValidationError(f"{template.id}/{inst.slug}: duplicate choice ids {ids}")
    if inst.correct_choice not in ids:
        raise ValidationError(
            f"{template.id}/{inst.slug}: correct choice "
            f"{inst.correct_choice!r} is not among {ids}"
        )
    if len(ids) < 2:
        raise ValidationError(f"{template.id}/{inst.slug}: a choice needs options")
    labels = [choice.label for choice in inst.choices]
    if len(labels) != len(set(labels)):
        raise ValidationError(
            f"{template.id}/{inst.slug}: two options read identically {labels}"
        )


def check_slots(template: Template, inst: Instance) -> None:
    if not inst.slots:
        return
    labels = [label for label, _, _ in inst.slots]
    if len(labels) != len(set(labels)):
        raise ValidationError(
            f"{template.id}/{inst.slug}: duplicate slot labels {labels}"
        )
    # Where the slot labels are interchangeable - "the two roots" - two equal
    # values make the problem ambiguous, because either ordering would have to
    # pass and the learner cannot tell which slot wants which. Templates whose
    # labels carry distinct meanings (k, p, q) are unaffected, so this is opt-in.
    if "unordered-slots" in template.tags:
        values = [sp.simplify(expr) for _, expr, _ in inst.slots]
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                if values[i] == values[j]:
                    raise ValidationError(
                        f"{template.id}/{inst.slug}: interchangeable slots "
                        f"{labels[i]!r} and {labels[j]!r} both equal "
                        f"{values[i]}, so the problem is ambiguous"
                    )


def check_template_invariant(template: Template, inst: Instance) -> None:
    """Run the template's own `verify` hook, and insist one exists where the
    generic numeric check has been opted out of.

    Without this, a template tagged `not-equal-to-prompt` - a root finder, say -
    would have its slot values checked only for uniqueness, and could ship roots
    that aren't roots.
    """
    if template.verify is None:
        if "not-equal-to-prompt" in template.tags:
            raise ValidationError(
                f"{template.id}: opts out of check_answer_matches_prompt via "
                f"'not-equal-to-prompt' but provides no verify hook, so its "
                f"answers would ship unchecked"
            )
        return

    try:
        template.verify(inst)
    except ValidationError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ValidationError(
            f"{template.id}/{inst.slug}: template invariant failed - {exc}"
        ) from exc


def check_instance(template: Template, inst: Instance) -> None:
    """Every instance-level invariant, in one call."""
    check_answer_is_correct(template, inst)
    check_antiderivative_is_correct(template, inst)
    check_answer_matches_prompt(template, inst)
    check_decomposition(template, inst)
    check_distractors_are_wrong(template, inst)
    check_choices(template, inst)
    check_slots(template, inst)
    check_template_invariant(template, inst)


# ---------------------------------------------------------------------------
# Assembled-problem checks
# ---------------------------------------------------------------------------


def check_problem(problem: Problem) -> None:
    """Fingerprint and LaTeX invariants on an assembled problem."""
    assert_katex_safe(problem.prompt_latex)

    for choice in problem.choices:
        if choice.is_latex:
            assert_katex_safe(choice.label)

    for answer in problem.answers:
        assert_katex_safe(answer.latex)

        if len(answer.fingerprint.ys) < 8:
            raise ValidationError(
                f"{problem.id}: only {len(answer.fingerprint.ys)} sample points "
                f"for answer {answer.label!r}"
            )
        if len(answer.fingerprint.points) != len(answer.fingerprint.ys):
            raise ValidationError(
                f"{problem.id}: answer {answer.label!r} has "
                f"{len(answer.fingerprint.points)} points but "
                f"{len(answer.fingerprint.ys)} values"
            )
        for point in answer.fingerprint.points:
            if len(point) != len(answer.fingerprint.variables):
                raise ValidationError(
                    f"{problem.id}: sample point {point} does not match "
                    f"variables {answer.fingerprint.variables}"
                )

        # Note: a constant fingerprint is fine. du/dx for (ax+b)^n really is the
        # constant a, and a constant fingerprint still rejects every expression
        # that isn't that constant.

        for distractor in answer.distractors:
            if agrees(distractor.fingerprint, answer.fingerprint):
                raise ValidationError(
                    f"{problem.id}: distractor {distractor.id!r} has the same "
                    f"fingerprint as the correct answer"
                )
            if distractor.fingerprint.points != answer.fingerprint.points:
                raise ValidationError(
                    f"{problem.id}: distractor {distractor.id!r} was sampled at "
                    f"different points than the answer"
                )
            if not distractor.feedback.strip():
                raise ValidationError(
                    f"{problem.id}: distractor {distractor.id!r} has no feedback, "
                    f"so it would be indistinguishable from a plain wrong answer"
                )

    if problem.choices:
        if problem.correct_choice not in {c.id for c in problem.choices}:
            raise ValidationError(
                f"{problem.id}: correct choice {problem.correct_choice!r} is not "
                f"among the options"
            )
        for choice in problem.choices:
            if not choice.feedback.strip():
                raise ValidationError(
                    f"{problem.id}: option {choice.id!r} has no feedback, so "
                    f"picking it teaches nothing"
                )
    elif not problem.answers:
        raise ValidationError(f"{problem.id}: no answers and no options")

    if not problem.instruction.strip():
        raise ValidationError(f"{problem.id}: no instruction")


# ---------------------------------------------------------------------------
# Bundle-level checks
# ---------------------------------------------------------------------------


def check_diagnostic(diagnostic: Diagnostic, chapter_ids: set[str]) -> None:
    if not diagnostic.items:
        raise ValidationError("diagnostic has no items")

    covered: dict[str, int] = {}
    for item in diagnostic.items:
        if item.chapter_id not in chapter_ids:
            raise ValidationError(
                f"diagnostic item {item.problem.id} reports on unknown chapter "
                f"{item.chapter_id!r}"
            )
        if not item.skill.strip():
            raise ValidationError(
                f"diagnostic item {item.problem.id} has no skill label, so the "
                f"results readout cannot say what was tested"
            )
        check_problem(item.problem)
        covered[item.chapter_id] = covered.get(item.chapter_id, 0) + 1

    # A chapter judged on a single question is judged by luck. Two minimum.
    thin = {cid: n for cid, n in covered.items() if n < 2}
    if thin:
        raise ValidationError(
            f"diagnostic decides these chapters on fewer than 2 items, which is "
            f"not enough to skip a chapter on: {thin}"
        )


def check_bundle(bundle: Bundle) -> None:
    """Cross-cutting checks over the whole emitted bundle."""
    seen_problems: set[str] = set()
    seen_levels: set[str] = set()
    chapter_ids = {chapter.id for chapter in bundle.chapters}

    if len(chapter_ids) != len(bundle.chapters):
        raise ValidationError("duplicate chapter ids")

    for chapter in bundle.chapters:
        for required in chapter.requires:
            if required not in chapter_ids:
                raise ValidationError(
                    f"chapter {chapter.id}: requires unknown chapter {required!r}"
                )
        if chapter.act not in bundle.acts:
            raise ValidationError(
                f"chapter {chapter.id}: act {chapter.act} has no title in the bundle"
            )
        if not chapter.levels:
            raise ValidationError(f"chapter {chapter.id}: no levels")
        if not chapter.gate.strip():
            raise ValidationError(f"chapter {chapter.id}: no mastery gate")

        for level in chapter.levels:
            if level.id in seen_levels:
                raise ValidationError(f"duplicate level id {level.id!r}")
            seen_levels.add(level.id)

            if level.type == "concept":
                if not level.body_md.strip():
                    raise ValidationError(f"{level.id}: concept level with empty body")
            elif not level.problems:
                raise ValidationError(f"{level.id}: {level.type} level with no problems")

            if len(level.problems) > 16:
                raise ValidationError(
                    f"{level.id}: {len(level.problems)} problems is more than one "
                    f"sitting"
                )

            for problem in level.problems:
                if problem.id in seen_problems:
                    raise ValidationError(f"duplicate problem id {problem.id!r}")
                seen_problems.add(problem.id)
                check_problem(problem)

    if bundle.diagnostic is not None:
        check_diagnostic(bundle.diagnostic, chapter_ids)


__all__ = [
    "ValidationError",
    "Variable",
    "check_answer_is_correct",
    "check_answer_matches_prompt",
    "check_bundle",
    "check_choices",
    "check_decomposition",
    "check_diagnostic",
    "check_distractors_are_wrong",
    "check_instance",
    "check_problem",
    "check_slots",
]
