"""The placement diagnostic - "Where Are You?"

Reuses the real chapter templates rather than inventing parallel questions, so
what the quiz measures and what the chapters teach cannot drift apart.

Design decisions worth stating:

- **Two items per chapter, minimum.** `validate.check_diagnostic` enforces it.
  Skipping a chapter on the strength of one lucky answer would be worse than not
  offering the diagnostic at all.
- **The threshold is every item.** Getting one of two wrong keeps the chapter.
  The cost of a false "you know this" is real - a gap that surfaces three
  chapters later, disguised as being bad at calculus - while the cost of a false
  "study this" is one afternoon of easy revision.
- **Chapter 4 is never skipped.** Its second half is the log-likelihood
  material, which appears in no school syllabus, so school fluency is no
  evidence of knowing it. The chapter declares `skippable=False`.
- **No hints, and easy items only.** The diagnostic measures retention, not
  problem-solving under guidance. Hard items would misreport rustiness as
  ignorance.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

from mathcoach.generator import (
    Instance,
    Template,
    choice_problem,
    slots_problem,
    solve_problem,
)
from mathcoach.schema import Diagnostic, DiagnosticItem

CONTENT = Path(__file__).resolve().parent.parent


def _templates(dirname: str) -> tuple[Template, ...]:
    """Import a sibling chapter's template registry."""
    import importlib.util

    package_dir = CONTENT / dirname
    name = f"diag_src_{dirname.replace('-', '_')}"
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
    return module.TEMPLATES


def _find(templates: tuple[Template, ...], template_id: str) -> Template:
    for template in templates:
        if template.id == template_id:
            return template
    raise KeyError(f"no template {template_id!r} in {[t.id for t in templates]}")


def _strip_help(inst: Instance) -> Instance:
    """A diagnostic item offers no hints or worked steps.

    Measuring what someone retains means asking without scaffolding. Leaving the
    hints in would measure how well they follow instructions instead.
    """
    return replace(inst, hints=(), steps=())


# (chapter dir, chapter id, template id, param index, skill label, how to build)
Spec = tuple[str, str, str, int, str, str]

ITEMS: tuple[Spec, ...] = (
    # --- Chapter 1: index laws, signs, fractions ---------------------------
    (
        "01-rust-remover",
        "ch01-rust-remover",
        "rr-nested-negation",
        0,
        "expanding through nested minus signs",
        "slots",
    ),
    (
        "01-rust-remover",
        "ch01-rust-remover",
        "rr-negative-exponent",
        0,
        "subtracting negative exponents",
        "slots",
    ),
    (
        "01-rust-remover",
        "ch01-rust-remover",
        "rr-surd",
        0,
        "simplifying a surd",
        "slots",
    ),
    # --- Chapter 2: quadratics --------------------------------------------
    (
        "02-rearranging",
        "ch02-rearranging",
        "rf-integer-roots",
        0,
        "factoring a quadratic",
        "slots",
    ),
    (
        "02-rearranging",
        "ch02-rearranging",
        "rf-complete-square",
        0,
        "completing the square",
        "slots",
    ),
    (
        "02-rearranging",
        "ch02-rearranging",
        "rf-inequality",
        1,
        "inequalities, and when the sign flips",
        "choice",
    ),
    # --- Chapter 3: composition -------------------------------------------
    (
        "03-machines",
        "ch03-machines",
        "mi-compose-power",
        0,
        "composing two functions",
        "solve",
    ),
    (
        "03-machines",
        "ch03-machines",
        "mi-inverse",
        0,
        "finding an inverse",
        "solve",
    ),
    (
        "03-machines",
        "ch03-machines",
        "mi-domain",
        0,
        "the domain of a composition",
        "choice",
    ),
    # --- Chapter 5: trigonometry ------------------------------------------
    # Chapter 4 is absent on purpose: it declares skippable=False, so testing
    # it here would report a result the app must then ignore.
    (
        "05-circles",
        "ch05-circles",
        "jc-exact-value",
        3,
        "exact value of sin(pi/3)",
        "choice",
    ),
    (
        "05-circles",
        "ch05-circles",
        "jc-identity",
        0,
        "the Pythagorean identity",
        "choice",
    ),
)


def build() -> Diagnostic:
    cache: dict[str, tuple[Template, ...]] = {}
    items: list[DiagnosticItem] = []

    for dirname, chapter_id, template_id, index, skill, kind in ITEMS:
        if dirname not in cache:
            cache[dirname] = _templates(dirname)
        template = _find(cache[dirname], template_id)
        inst = _strip_help(template.build(**template.params[index]))

        if kind == "slots":
            problem = slots_problem(template, inst, instruction=inst.instruction or "Fill in each value.")
        elif kind == "choice":
            problem = choice_problem(template, inst, instruction=inst.instruction or "Pick one.")
        else:
            problem = solve_problem(
                template, inst, instruction=inst.instruction or "Answer in terms of x."
            )

        # Diagnostic problem ids must not collide with the chapter's own copies
        # of the same instance, or the bundle's uniqueness check fires.
        problem = replace(problem, id=f"diag--{problem.id}")
        items.append(
            DiagnosticItem(problem=problem, chapter_id=chapter_id, skill=skill)
        )

    return Diagnostic(
        id="diagnostic-act-1",
        title="Where Are You?",
        blurb=(
            "Eleven questions, about fifteen minutes. Every chapter you pass "
            "gets marked as known and folded away, so you only study what you "
            "actually need. Get one wrong in a chapter and it stays - a gap you "
            "skip past resurfaces three chapters later disguised as being bad "
            "at calculus. No hints here, on purpose."
        ),
        items=tuple(items),
        # Every item in a chapter, or the chapter stays. See the module docstring.
        pass_threshold=0.999,
    )


__all__ = ["build"]
