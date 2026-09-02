"""Tests over the actual chapter content and the invariants that guard it."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import sympy as sp

from mathcoach.assemble import validated
from mathcoach.fingerprint import agrees, choose_points, fingerprint_at
from mathcoach.generator import (
    X,
    Instance,
    Template,
    any_sign,
    choice_problem,
    differentiate_problem,
    slots_problem,
    solve_problem,
)
from mathcoach.validate import (
    ValidationError,
    check_answer_is_correct,
    check_choices,
    check_distractors_are_wrong,
    check_instance,
    check_problem,
    check_slots,
    check_template_invariant,
)

ROOT = Path(__file__).resolve().parent.parent.parent
CONTENT = ROOT / "content" / "chapters"
BUNDLE_PATH = ROOT / "web" / "public" / "content" / "bundle.json"

CHAPTER_DIRS = (
    "01-rust-remover",
    "02-rearranging",
    "03-machines",
    "04-growth",
    "05-circles",
    "06-approaching",
    "07-slope",
    "08-rulebook",
    "09-chain-rule",
    "10-hidden",
    "11-bottom",
    "12-backwards",
    "13-bridge",
    "14-costume",
    "15-trading",
    "16-expectations",
)


def _load_templates(dirname: str) -> tuple[Template, ...]:
    package_dir = CONTENT / dirname
    name = f"test_src_{dirname.replace('-', '_')}"
    if name not in sys.modules:
        package_spec = importlib.util.spec_from_file_location(
            name,
            package_dir / "__init__.py",
            submodule_search_locations=[str(package_dir)],
        )
        package = importlib.util.module_from_spec(package_spec)
        sys.modules[name] = package
        package_spec.loader.exec_module(package)

    spec = importlib.util.spec_from_file_location(
        f"{name}.templates", package_dir / "templates.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{name}.templates"] = module
    spec.loader.exec_module(module)
    return getattr(module, "TEMPLATES", None) or module.ALL_TEMPLATES


ALL_PAIRS: list[tuple[str, Template, Instance]] = []
for _dirname in CHAPTER_DIRS:
    for _template in _load_templates(_dirname):
        for _params in _template.params:
            ALL_PAIRS.append((_dirname, _template, _template.build(**_params)))

IDS = [f"{d}/{t.id}/{i.slug}" for d, t, i in ALL_PAIRS]


# --- Every template's maths is right ---------------------------------------


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_instance_passes_every_invariant(dirname, template, inst):
    """The whole invariant suite: derivatives, numeric equivalence, distractors,
    choices, slots, and the template's own verify hook."""
    check_instance(template, inst)


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_instance_assembles_into_a_valid_problem(dirname, template, inst):
    """Assembly is where distractors get fingerprinted.

    check_instance alone never samples them, which is how a distractor whose
    domain was disjoint from the answer's first slipped through.
    """
    if inst.choices:
        problem = choice_problem(template, inst)
    elif inst.slots:
        problem = slots_problem(template, inst, instruction="Fill in each value.")
    elif template.rule is not None:
        problem = differentiate_problem(template, inst)
    else:
        problem = solve_problem(template, inst)
    check_problem(problem)


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_distractors_are_numerically_distinct(dirname, template, inst):
    """Symbolic inequality isn't enough - the *fingerprints* must differ, since
    that is what actually grades the answer."""
    if not inst.distractors or inst.answer is None:
        return
    exprs = [inst.answer, *(e for _, e, _ in inst.distractors)]
    points = choose_points(exprs, template.variables)
    answer_fp = fingerprint_at(inst.answer, template.variables, points)
    for did, expr, _ in inst.distractors:
        assert not agrees(
            answer_fp, fingerprint_at(expr, template.variables, points)
        ), (
            f"{template.id}/{inst.slug}: distractor {did!r} is numerically "
            f"indistinguishable from the correct answer"
        )


@pytest.mark.parametrize(
    "dirname, template, inst",
    [p for p in ALL_PAIRS if p[1].rule == "chain"],
    ids=[f"{t.id}/{i.slug}" for _, t, i in ALL_PAIRS if t.rule == "chain"],
)
def test_chain_templates_expose_a_real_composition(dirname, template, inst):
    assert inst.inner is not None, "a chain rule template needs an inner function"
    assert sp.simplify(inst.inner - X) != 0, "inner function must not be just x"
    assert sp.simplify(sp.diff(inst.inner, X) - inst.inner_deriv) == 0


# --- The roadmap's gate problems are present and correct --------------------


def test_chain_rule_gate_problems_exist():
    """Chapter 9's gate names sin(ln(3x²+1)) and e^(cos²(2x))."""
    expected = {
        sp.sin(sp.log(3 * X**2 + 1)): 6
        * X
        * sp.cos(sp.log(3 * X**2 + 1))
        / (3 * X**2 + 1),
        sp.exp(sp.cos(2 * X) ** 2): -4
        * sp.exp(sp.cos(2 * X) ** 2)
        * sp.sin(2 * X)
        * sp.cos(2 * X),
    }
    found = {}
    for _, _, inst in ALL_PAIRS:
        for target in expected:
            if inst.expr.free_symbols <= {X} and sp.simplify(inst.expr - target) == 0:
                found[target] = inst.answer

    assert len(found) == 2, f"gate problems missing: {list(found)}"
    for target, answer in found.items():
        assert sp.simplify(answer - expected[target]) == 0


def test_chapter_1_gate_problem_exists():
    """Chapter 1's gate is (8x^(-2/3)y⁴)^(1/2) / (2x⁴y^(-1))."""
    matches = [
        inst
        for _, template, inst in ALL_PAIRS
        if template.id == "rr-index-quotient"
        and inst.slug.startswith("c8pm2q3py4n2")
    ]
    assert matches, "chapter 1's gate instance is missing"
    inst = matches[0]
    slots = {label: value for label, value, _ in inst.slots}
    assert sp.simplify(slots["k"] - sp.sqrt(2)) == 0
    assert slots["power of x"] == sp.Rational(-13, 3)
    assert slots["power of y"] == 3


def test_chapter_4_gate_problem_exists():
    """Chapter 4's gate is ln(a²b/√c) -> 2, 1, -1/2."""
    matches = [
        inst
        for _, template, inst in ALL_PAIRS
        if template.id == "gu-expand-log" and inst.slug == "pa2pb1rc2"
    ]
    assert matches, "chapter 4's gate instance is missing"
    slots = {label: value for label, value, _ in matches[0].slots}
    assert slots["coefficient of ln a"] == 2
    assert slots["coefficient of ln b"] == 1
    assert slots["coefficient of ln c"] == sp.Rational(-1, 2)


def test_chapter_5_gate_values_are_all_covered():
    """Chapter 5's gate asks for sin and cos of five angles - all ten."""
    values = {
        (inst.slug.split("-")[0], inst.slug)
        for _, template, inst in ALL_PAIRS
        if template.id == "jc-exact-value"
    }
    assert len(values) == 10, f"expected 10 exact-value items, got {len(values)}"


# --- Prose fields ----------------------------------------------------------


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_prose_uses_ln_not_log(dirname, template, inst):
    r"""Mathematicians read \ln; sympy emits \log by default. Any leak is a bug."""
    prose = [
        *inst.hints,
        *(note for _, note in inst.steps),
        *(latex for latex, _ in inst.steps),
        *(feedback for _, _, feedback in inst.distractors),
        *(choice.feedback for choice in inst.choices),
        *(choice.label for choice in inst.choices if choice.is_latex),
        inst.prompt_latex or "",
    ]
    for text in prose:
        assert r"\log" not in text, f"{template.id}/{inst.slug}: raw \\log in {text!r}"


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_no_double_signs_in_prompts(dirname, template, inst):
    """`7 - -2(3 - x)` is a rendering bug, not maths."""
    prompt = inst.prompt_latex or ""
    assert " - -" not in prompt, f"{template.id}/{inst.slug}: double minus in prompt"
    assert " + -" not in prompt, f"{template.id}/{inst.slug}: plus-minus in prompt"
    assert "--" not in prompt, f"{template.id}/{inst.slug}: double dash in prompt"


@pytest.mark.parametrize(
    "dirname, template, inst",
    [p for p in ALL_PAIRS if p[1].rule == "chain"],
    ids=[f"{t.id}/{i.slug}" for _, t, i in ALL_PAIRS if t.rule == "chain"],
)
def test_chain_problems_have_a_full_hint_ladder(dirname, template, inst):
    assert len(inst.hints) >= 3, "a hint ladder needs rungs to climb"
    assert len(inst.steps) >= 2
    # The first rung must not give the technique away.
    assert "du/dx" not in inst.hints[0], (
        f"{template.id}/{inst.slug}: first hint already hands over the method"
    )


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_feedback_is_a_teaching_sentence(dirname, template, inst):
    for did, _, feedback in inst.distractors:
        assert len(feedback) > 40, (
            f"{template.id}/{inst.slug}: feedback for {did!r} is too terse"
        )
        # Deliberately not checking for a capital first letter: feedback may
        # legitimately open with a lowercase symbol, as in "e^u is its own...".
        assert feedback.strip().endswith(".")
    for choice in inst.choices:
        assert len(choice.feedback) > 30, (
            f"{template.id}/{inst.slug}: option {choice.id!r} explains too little"
        )


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_correct_option_feedback_does_not_repeat_the_affirmation(
    dirname, template, inst
):
    """The UI already renders "Yes." before a correct option's feedback.

    Feedback that opens with its own "Yes."/"Correct."/"Exactly." reads as
    "Yes. Exactly. ..." - the same duplication bug that first shipped as
    "this one is the chain rule: Chain rule: ...".
    """
    if not inst.choices or inst.correct_choice is None:
        return
    correct = next(c for c in inst.choices if c.id == inst.correct_choice)
    opening = correct.feedback.strip().split(" ")[0].rstrip(".,-").lower()
    assert opening not in {"yes", "correct", "exactly", "right", "indeed"}, (
        f"{template.id}/{inst.slug}: correct-option feedback opens with "
        f"{opening!r}, which the interface already says"
    )


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_wrong_option_feedback_does_not_preempt_the_answer(dirname, template, inst):
    """A wrong pick shows its own feedback and then the correct option's.

    If the wrong-pick text already states the answer, the learner reads it
    twice. Checked only where both mention the same value verbatim.
    """
    if not inst.choices or inst.correct_choice is None:
        return
    correct = next(c for c in inst.choices if c.id == inst.correct_choice)
    tail = correct.feedback.strip()[-40:]
    for choice in inst.choices:
        if choice.id == inst.correct_choice:
            continue
        assert tail not in choice.feedback, (
            f"{template.id}/{inst.slug}: option {choice.id!r} repeats the "
            f"correct answer's closing sentence, which is shown right after it"
        )


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_slots_declare_what_they_want(dirname, template, inst):
    """Every slot needs help text, or the learner has to guess the format."""
    for label, _, help_text in inst.slots:
        assert help_text.strip(), (
            f"{template.id}/{inst.slug}: slot {label!r} has no help text"
        )


@pytest.mark.parametrize("dirname, template, inst", ALL_PAIRS, ids=IDS)
def test_templates_declare_a_skill(dirname, template, inst):
    """The diagnostic readout needs a skill label to report on."""
    assert template.skill.strip(), f"{template.id} has no skill label"


# --- Negative tests: the guards actually fire ------------------------------

VARS = any_sign("x")


def test_wrong_answer_in_a_template_is_caught():
    bad = Instance(expr=sp.sin(3 * X**2), answer=sp.cos(3 * X**2), slug="bad")
    template = Template(
        id="broken", tier="easy", rule="chain", build=lambda: bad, params=()
    )
    with pytest.raises(ValidationError, match="not the derivative"):
        check_answer_is_correct(template, bad)


def test_algebra_answer_not_equal_to_prompt_is_caught():
    """An algebra template whose answer isn't its prompt must fail."""
    from mathcoach.validate import check_answer_matches_prompt

    bad = Instance(expr=X**2 + 1, answer=X**2 + 2, slug="bad")
    template = Template(id="broken-algebra", tier="easy", build=lambda: bad, params=())
    with pytest.raises(ValidationError, match="not equal to the expression"):
        check_answer_matches_prompt(template, bad)


def test_distractor_equal_to_answer_is_caught():
    inner = 3 * X**2 + 1
    bad = Instance(
        expr=sp.sin(inner),
        answer=6 * X * sp.cos(inner),
        slug="bad",
        # Same function written differently - the sneaky case.
        distractors=(("sneaky", sp.cos(inner) * 3 * 2 * X, "feedback text here."),),
    )
    template = Template(
        id="broken", tier="easy", rule="chain", build=lambda: bad, params=()
    )
    with pytest.raises(ValidationError, match="equal to the correct answer"):
        check_distractors_are_wrong(template, bad)


def test_distractor_without_feedback_is_caught():
    inner = 3 * X**2 + 1
    inst = Instance(
        expr=sp.sin(inner),
        answer=6 * X * sp.cos(inner),
        slug="nofeedback",
        distractors=(("silent", sp.cos(inner), "   "),),
    )
    template = Template(
        id="quiet", tier="easy", rule="chain", build=lambda: inst, params=()
    )
    with pytest.raises(ValidationError, match="no feedback"):
        check_problem(differentiate_problem(template, inst))


def test_inner_function_of_x_is_rejected():
    inst = Instance(
        expr=sp.sin(X),
        answer=sp.cos(X),
        inner=X,
        inner_deriv=sp.Integer(1),
        slug="triv",
    )
    template = Template(
        id="trivial", tier="easy", rule="chain", build=lambda: inst, params=()
    )
    with pytest.raises(ValidationError, match="nothing is composed"):
        check_instance(template, inst)


def test_opting_out_without_a_verify_hook_is_rejected():
    """A template that skips the numeric check must state its own invariant."""
    inst = Instance(expr=X, slug="s")
    template = Template(
        id="unhooked",
        tier="easy",
        build=lambda: inst,
        params=(),
        tags=("not-equal-to-prompt",),
    )
    with pytest.raises(ValidationError, match="no verify hook"):
        check_template_invariant(template, inst)


def test_verify_hook_failure_is_reported():
    def always_fails(_: Instance) -> None:
        raise ValueError("deliberate failure")

    inst = Instance(expr=X, slug="s")
    template = Template(
        id="hooked", tier="easy", build=lambda: inst, params=(), verify=always_fails
    )
    with pytest.raises(ValidationError, match="deliberate failure"):
        check_template_invariant(template, inst)


def test_ambiguous_unordered_slots_are_rejected():
    inst = Instance(
        expr=X**2,
        slug="dup",
        slots=(
            ("smaller root", sp.Integer(2), "a number"),
            ("larger root", sp.Integer(2), "a number"),
        ),
    )
    template = Template(
        id="dup", tier="easy", build=lambda: inst, params=(), tags=("unordered-slots",)
    )
    with pytest.raises(ValidationError, match="ambiguous"):
        check_slots(template, inst)


def test_labelled_slots_may_share_a_value():
    """k and p meaning different things may coincide; that isn't ambiguity."""
    inst = Instance(
        expr=X**2,
        slug="same",
        slots=(
            ("k", sp.Integer(3), "a number"),
            ("power of x", sp.Integer(3), "a number"),
        ),
    )
    template = Template(id="fine", tier="easy", build=lambda: inst, params=())
    check_slots(template, inst)  # must not raise


def test_correct_choice_must_be_among_the_options():
    from mathcoach.schema import Choice

    inst = Instance(
        expr=sp.Integer(0),
        slug="bad",
        choices=(
            Choice(id="a", label="A", feedback="x" * 40),
            Choice(id="b", label="B", feedback="y" * 40),
        ),
        correct_choice="c",
    )
    template = Template(id="badchoice", tier="easy", build=lambda: inst, params=())
    with pytest.raises(ValidationError, match="not among"):
        check_choices(template, inst)


def test_identical_option_labels_are_rejected():
    from mathcoach.schema import Choice

    inst = Instance(
        expr=sp.Integer(0),
        slug="dup",
        choices=(
            Choice(id="a", label="x > 5", feedback="x" * 40),
            Choice(id="b", label="x > 5", feedback="y" * 40),
        ),
        correct_choice="a",
    )
    template = Template(id="duplabels", tier="easy", build=lambda: inst, params=())
    with pytest.raises(ValidationError, match="read identically"):
        check_choices(template, inst)


# --- The emitted bundle ----------------------------------------------------


@pytest.fixture(scope="module")
def bundle() -> dict:
    if not BUNDLE_PATH.exists():
        pytest.skip("run `python tools/build.py` first")
    return json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))


def test_bundle_structure(bundle):
    assert bundle["schemaVersion"] == 2
    assert len(bundle["chapters"]) >= 6
    assert bundle["diagnostic"] is not None
    for chapter in bundle["chapters"]:
        assert str(chapter["act"]) in bundle["acts"]
        # Consolidation tiers deliberately have no concept card: they teach
        # nothing new, they mix what the chapters already taught.
        if chapter["isConsolidation"]:
            continue
        assert chapter["levels"][0]["type"] == "concept", (
            f"{chapter['id']} should open with its concept card"
        )


def test_bundle_ids_are_unique(bundle):
    seen: set[str] = set()
    for chapter in bundle["chapters"]:
        for level in chapter["levels"]:
            for problem in level["problems"]:
                assert problem["id"] not in seen, f"duplicate {problem['id']}"
                seen.add(problem["id"])
    for item in bundle["diagnostic"]["items"]:
        assert item["problem"]["id"] not in seen, "diagnostic collides with a chapter"
        seen.add(item["problem"]["id"])


def test_levels_are_one_sitting(bundle):
    for chapter in bundle["chapters"]:
        for level in chapter["levels"]:
            assert len(level["problems"]) <= 16, (
                f"{level['id']} has {len(level['problems'])} problems"
            )


def test_recognize_level_is_not_guessable(bundle):
    """If most items share an answer, the learner can score without looking."""
    chapter = next(c for c in bundle["chapters"] if c["id"] == "ch09-chain-rule")
    level = next(l for l in chapter["levels"] if l["id"] == "ch09-l2-recognize")
    answers = [problem["correctChoice"] for problem in level["problems"]]
    chain_share = answers.count("chain") / len(answers)
    assert 0.4 <= chain_share <= 0.6, (
        f"{chain_share:.0%} of items answer 'chain'"
    )
    longest = best = 1
    for previous, current in zip(answers, answers[1:]):
        longest = longest + 1 if current == previous else 1
        best = max(best, longest)
    assert best <= 2, f"a run of {best} identical answers is guessable"


def test_every_solve_problem_has_help(bundle):
    """A free-form problem with no hints and no steps leaves you stranded."""
    for chapter in bundle["chapters"]:
        for level in chapter["levels"]:
            if level["type"] not in {"solve", "decompose"}:
                continue
            for problem in level["problems"]:
                assert problem["hints"] or problem["steps"], (
                    f"{problem['id']} offers neither hints nor worked steps"
                )


def test_fingerprints_are_well_formed(bundle):
    for chapter in bundle["chapters"]:
        for level in chapter["levels"]:
            for problem in level["problems"]:
                for answer in problem["answers"]:
                    fingerprint = answer["fingerprint"]
                    assert len(fingerprint["points"]) >= 8
                    assert len(fingerprint["points"]) == len(fingerprint["ys"])
                    for point in fingerprint["points"]:
                        assert len(point) == len(fingerprint["variables"])


def test_no_log_leaked_into_the_bundle(bundle):
    raw = BUNDLE_PATH.read_text(encoding="utf-8")
    assert "\\\\log" not in raw, r"raw \log in the bundle; should render as \ln"


# --- The diagnostic --------------------------------------------------------


def test_consolidation_tiers_strip_their_hints(bundle):
    """A consolidation problem must not name the technique.

    That is the entire point of the tier: choosing what to reach for is a
    separate skill from executing a named rule, and a hint saying "this is the
    chain rule" would remove exactly the thing being trained.
    """
    tiers = [c for c in bundle["chapters"] if c["isConsolidation"]]
    assert tiers, "no consolidation tiers in the bundle"
    for chapter in tiers:
        for level in chapter["levels"]:
            assert level["problems"], f"{level['id']} is empty"
            for problem in level["problems"]:
                assert not problem["hints"], (
                    f"{problem['id']} carries hints, which would name the "
                    f"technique the tier exists to make you find"
                )
                # Worked steps stay: they are the surrender path, taken after
                # you have tried rather than instead of trying.
                assert problem["steps"], (
                    f"{problem['id']} has no worked steps, leaving no way out "
                    f"when genuinely stuck"
                )
                # The instruction is the other place a technique can leak, and
                # it did: chapter 7's "from the definition, not from the rules"
                # reached a consolidation problem and gave the method away.
                giveaways = (
                    "from the definition",
                    "chain rule",
                    "product rule",
                    "quotient rule",
                    "power rule",
                    "by parts",
                    "substitut",
                    "implicit",
                )
                lowered = problem["instruction"].lower()
                for phrase in giveaways:
                    assert phrase not in lowered, (
                        f"{problem['id']}: instruction names the technique "
                        f"({phrase!r}), which the tier exists to make you find"
                    )


def test_antiderivative_problems_grade_up_to_a_constant(bundle):
    """Integration levels must compare differences, not absolute values.

    Without `upToConstant`, x³/3 + 7 would be marked wrong - and it isn't
    wrong. This is the one place where the grader's notion of equality has to
    differ from plain numeric equality.
    """
    integration_chapters = {
        "ch12-backwards",
        "ch14-costume",
        "ch15-trading",
    }
    checked = 0
    for chapter in bundle["chapters"]:
        if chapter["id"] not in integration_chapters:
            continue
        for level in chapter["levels"]:
            for problem in level["problems"]:
                # Definite integrals evaluate to numbers and must NOT be graded
                # up to a constant - the value is the value.
                if "int_{" in problem["promptLatex"]:
                    continue
                for answer in problem["answers"]:
                    checked += 1
                    assert answer["fingerprint"]["upToConstant"], (
                        f"{problem['id']} is an antiderivative but is graded on "
                        f"absolute values, so + C would be marked wrong"
                    )
    assert checked > 0, "no antiderivative problems found to check"


def test_definite_integrals_are_not_graded_up_to_a_constant(bundle):
    """The mirror image: a definite integral has one right number."""
    for chapter in bundle["chapters"]:
        if chapter["act"] != 3:
            continue
        for level in chapter["levels"]:
            for problem in level["problems"]:
                if "int_{" not in problem["promptLatex"]:
                    continue
                for answer in problem["answers"]:
                    assert not answer["fingerprint"]["upToConstant"], (
                        f"{problem['id']} has bounds, so its value is exact - "
                        f"grading it up to a constant would accept anything"
                    )


def test_diagnostic_decides_no_chapter_on_one_item(bundle):
    counts: dict[str, int] = {}
    for item in bundle["diagnostic"]["items"]:
        counts[item["chapterId"]] = counts.get(item["chapterId"], 0) + 1
    thin = {cid: n for cid, n in counts.items() if n < 2}
    assert not thin, f"chapters judged on a single item: {thin}"


def test_diagnostic_offers_no_help(bundle):
    """Hints would measure how well you follow guidance, not what you retain."""
    for item in bundle["diagnostic"]["items"]:
        assert not item["problem"]["hints"], f"{item['problem']['id']} has hints"
        assert not item["problem"]["steps"], f"{item['problem']['id']} has steps"


def test_diagnostic_only_tests_skippable_chapters(bundle):
    """Testing an unskippable chapter would report a result the app must ignore."""
    skippable = {c["id"] for c in bundle["chapters"] if c["skippable"]}
    for item in bundle["diagnostic"]["items"]:
        assert item["chapterId"] in skippable, (
            f"{item['problem']['id']} reports on {item['chapterId']}, which "
            f"cannot be skipped - the result would be discarded"
        )


def test_diagnostic_threshold_demands_every_item(bundle):
    """Skipping a chapter on a partial score risks a gap that resurfaces later."""
    assert bundle["diagnostic"]["passThreshold"] > 0.99


def test_diagnostic_items_name_their_skill(bundle):
    for item in bundle["diagnostic"]["items"]:
        assert item["skill"].strip()


# --- Act I's grading design -----------------------------------------------


def test_simplification_chapters_do_not_use_free_form_answers(bundle):
    """The core Act I design constraint.

    A "simplify this" prompt is numerically equal to its own answer, so a
    single free-form slot would accept the question pasted straight back. Those
    chapters must therefore ask for named parts, or offer choices.
    """
    at_risk = {"ch01-rust-remover", "ch02-rearranging"}
    for chapter in bundle["chapters"]:
        if chapter["id"] not in at_risk:
            continue
        for level in chapter["levels"]:
            for problem in level["problems"]:
                if problem["choices"] if "choices" in problem else False:
                    continue
                assert len(problem["answers"]) != 1, (
                    f"{problem['id']} has a single free-form answer; the prompt "
                    f"could be pasted back and would grade correct"
                )
