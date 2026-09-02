# Architecture

## The problem this design solves

Grading maths is the hard part of a calculus app. `6x·cos(3x²+1)` and
`2·3·x·cos(1+3x²)` are the same answer; `2x·cos(ln(3x²+1))/(x²+⅓)` is the same
answer as `6x·cos(ln(3x²+1))/(3x²+1)`. A grader that only accepts one written
form is useless, and a browser-side computer algebra system is heavy and
fragile.

**All symbolic work happens at build time, in SymPy. The browser grades by
comparing numbers.**

## How grading works

For every problem, the Python build emits a **fingerprint**: the answer
evaluated at eight fixed rational sample points, at 40 digits of precision.

At runtime the browser parses what you typed (mathjs), evaluates it at those
same points, and compares within a relative tolerance of `1e-6`. Two expressions
that agree at eight awkward points are, for these template families, the same
function — so *any* algebraically equivalent form is accepted, with no CAS in
the browser.

The same mechanism does something a plain grader can't. Each problem also
carries fingerprints for its **distractors** — specific wrong answers
corresponding to known misconceptions. A learner's answer that matches one gets
told *which mistake they made*:

> You differentiated the outer sine into a cosine correctly, but never
> multiplied by the derivative of what's inside it. The chain rule has two
> factors; you wrote one.

That is the difference between a coach and a grader.

### The limit of fingerprint grading, and what Act I does about it

Fingerprints accept anything numerically equal to the answer. That is exactly
what makes them useful for differentiation — and exactly what makes them
**useless for "simplify this"**, because a simplification prompt is numerically
equal to its own answer. A free-form input would mark the learner correct for
pasting the question straight back, having done nothing.

`x² − 4` and `(x−2)(x+2)` are the same function. No grader that evaluates your
answer can tell a factored form from the original.

So the rule is: **free-form answers are only safe where the answer differs from
the prompt.** Act I is built around it.

| Task | Grading | Why |
|---|---|---|
| Differentiate, compose, invert, condense a log | Free-form | The answer is a different expression from anything shown |
| Simplify, factor, complete the square, expand a log | **Named slots** — `k`, `p`, `q`, the roots, the coefficients | Pasting the prompt back can't fill three labelled boxes, and naming the exponents *is* the skill |
| Recall a value, pick a domain, pick an inequality | **Multiple choice** | A set isn't an expression; and typing `sin(pi/6)` back would evaluate to 0.5 and score |

The build enforces this: `test_simplification_chapters_do_not_use_free_form_answers`
fails if chapter 1 or 2 ever ships a single free-form slot.

### Multivariable fingerprints

A fingerprint declares its variables and samples tuples aligned to them, so
`ln(a²b/√c)` is gradeable in three variables at once. Two details matter:

- **Variables walk their pools at coprime strides**, and points where two
  variables coincide are discarded. Without that, `a + b` would pass as `2a` at
  any point where `a == b`.
- **`Domain`** (`ANY` / `POSITIVE`) picks the pool; `Variable.pool` overrides it
  outright for functions defined only on a narrow interval. `√(1/x − 4)` is real
  only on `(0, ¼]`, which neither default pool reaches.

`Domain.POSITIVE` deliberately does **not** put `positive=True` on the SymPy
symbol. SymPy treats `Symbol("x", positive=True)` as a *different symbol* from
`Symbol("x", real=True)`, so the assumption would make substitution silently do
nothing. Domains govern sampling, not what SymPy may assume; where a proof needs
positivity, validate numerically.

### What keeps it safe

Sample points are chosen **per problem**, and rejected where any of its
expressions is undefined, complex, or non-finite. That keeps poles, logs of
negatives and even roots of negatives out of every fingerprint. All of a
problem's expressions — answer and distractors — share one point set, so their
fingerprints are directly comparable.

That last requirement has teeth. For `f = √(x−1)`, `g = 1/x`, the compositions
`f∘g` and `g∘f` have **disjoint domains** — `(0,1]` and `(1,∞)` — so a
"wrong-order" distractor cannot be compared against the answer at any point at
all. The build refused to emit it, which is how the fact was noticed; chapter
3's concept card now teaches it.

### Tolerance, and decimals

Comparison is relative, at `1e-6`. Verified behaviour: for an answer of `−9/8`,
`−1.1249999` is accepted and `−1.12` is rejected. So the grader accepts
high-precision decimals and rejects rounded ones. A learner who types eight
significant figures has genuinely done the work; one who types three has not.
Instructions still say "exact", because surds are the better habit.

The tolerance and comparison rule in `web/src/engine/grader.ts` must stay
identical to `agrees()` in `tools/mathcoach/fingerprint.py`. If they drift, a
problem that validated at build time could still be graded wrongly.

`upToConstant` fingerprints compare *differences* between sample points rather
than absolute values, so `+C` cancels. See "Integration, and grading up to a
constant" below.

## Build-time invariants

The build fails rather than emit a questionable problem. From
`tools/mathcoach/validate.py`:

- **The stated answer really is the derivative.** Templates write their answers
  out longhand; validation differentiates the prompt with SymPy independently
  and requires agreement. This is what catches an algebra slip in a template —
  the one bug class that would teach the learner something false.
- **No distractor equals the correct answer**, symbolically *or* by fingerprint.
  A collision would mean telling someone they were wrong when they weren't,
  which is the worst thing this app could do.
- **Every distractor has feedback**, or it's indistinguishable from a plain
  wrong answer and earns nothing.
- **`inner_deriv` really is `d(inner)/dx`**, and `inner` is not just `x` — a
  "composition" whose inner function is `x` isn't a chain rule problem.
- **Sample points are clear** of poles and branch cuts.
- **Every template that opts out of the numeric check supplies its own
  invariant.** A root-finder tagged `not-equal-to-prompt` must provide a
  `verify` hook, or the build rejects it — otherwise its slot values would ship
  checked only for uniqueness, and could contain roots that aren't roots.
- **Every LaTeX string renders under KaTeX**, checked by
  `web/scripts/check-latex.mjs` — Python can validate maths but cannot know what
  KaTeX will accept.
- **No unpaired `$` survives a concept card.** This one was added after the
  checker was caught sharing a blind spot with the renderer: both used a regex
  that forbade newlines inside `$…$`, so inline maths that wrapped across a line
  break was invisible to the check *and* rendered to the reader as a literal
  `$\sin(0.01) = 0.00999983$`. The regexes in `check-latex.mjs` and
  `Markdown.tsx` must stay identical, and leftover delimiters now fail the build.

### Prompts are authored, not rendered

SymPy evaluates as it builds. `sp.sqrt(72)` **is** `6*sqrt(2)`; `-(5 - 3*(2-x))`
**is** `1 - 3*x`. There is no unsimplified object to render.

Harmless for differentiation, where prompt and answer differ. Fatal for algebra,
where rendering the SymPy object prints the answer as the question — chapter 1's
gate first displayed as `√2·y³/x^(13/3)`, the solution.

So algebra templates set `Instance.prompt_latex` using the builders in
`latex.py`, and keep the SymPy `expr` purely for the numeric check. The check
still earns its keep: it verifies the answer against an expression derived
independently from the same parameters.

## Layout

```
content/chapters/NN-slug/
  templates.py    parameterised problem families + their misconceptions
  chapter.py      level assembly; the level order IS the pedagogy
  concept.md      the concept card (Markdown + $…$ maths)

tools/
  build.py        orchestrator -> bundle.json + generated TypeScript
  mathcoach/
    fingerprint.py  sample-point selection and evaluation
    generator.py    instance -> Problem, for each level type
    latex.py        SymPy -> KaTeX-safe LaTeX
    schema.py       the output contract; source of the TS types
    validate.py     the invariants above
  tests/          230 tests, incl. the equivalence premise itself

web/
  src/engine/     grader, parser, progress, formatters
  src/components/ level runner, hint ladder, answer input, chapter view
  src/content/schema.ts   GENERATED - do not edit
  public/content/bundle.json  GENERATED
```

`tools/build.py` emits `web/src/content/schema.ts` alongside the bundle, so a
schema change the frontend hasn't caught up with fails `tsc`, not a level at
runtime.

## Level types

| Type | What it asks | Why it exists |
|---|---|---|
| `concept` | Read | Theory, available on demand rather than up front |
| `choice` | Pick one | For answers that aren't expressions: which rule applies, what the domain is, an exact value recalled. In chapter 9's rule-recognition level, chain and non-chain items strictly alternate, so guessing "chain" scores 50% |
| `decompose` | Name `u` and `du/dx` | The skill the chain rule actually rests on. Two graded slots |
| `solve` | Type the answer — one free-form slot, or several named ones | Carrying a problem to completion. Named slots are how the simplification chapters stay gradeable (see above) |

## Consolidation tiers

Sudoku Coach interleaves its technique chapters with difficulty-graded BONUS
nodes: mixed puzzles, no scaffolding, and no hint about which technique applies.
Recognising what to reach for is a different skill from executing a named
technique, and only unscaffolded mixing trains it.

Those are separate chapters here, exactly as BONUS nodes are separate nodes.
`tools/mathcoach/consolidation.py` draws instances from the chapters already
covered, spreads them round-robin so neighbours rarely share a technique, and
strips everything that would name the method:

- **Hints go.** They exist to name the technique.
- **The instruction goes too**, for free-form answers. This is where it first
  leaked: chapter 7's "work out f'(x) from the definition, not from the rules"
  reached a consolidation problem and handed over the method as plainly as any
  hint. Slot problems keep their instruction, because there it describes the
  answer's *format* ("give p, then q") rather than the technique.
- **Worked steps stay.** They are the surrender path, taken after trying.

A test asserts no consolidation instruction contains a technique name.

Consolidation chapters share the `number` of the chapter they follow and set
`is_consolidation`, so the campaign map draws them with a star and excludes them
from missing-chapter detection.

## Integration, and grading up to a constant

An antiderivative is only defined up to an additive constant, so
`Template.integrates` makes `solve_problem` fingerprint the answer with
`up_to_constant`: the grader compares *differences* between sample points rather
than absolute values.

That is not laxity, it is the correct notion of equality for the question.
Verified in the app: `x⁴/4 + 7` is accepted and `x⁴/4 + x` is rejected, because
7 is constant and x is not. `+ C` typed literally is stripped by the parser
before mathjs sees it, since it carries no information the grader uses.

Definite integrals must *not* be graded this way — their value is exact — and a
test asserts both halves of that.

Antiderivatives are validated by **differentiating the answer back**, never by
integrating the prompt. SymPy's `integrate` can return unevaluated integrals,
pick a different equivalent form, or simply fail; its `diff` is mechanical and
total. Checking the easy direction is both cheaper and complete.

## Which check applies to which chapter

Three kinds of template, three different notions of "the answer is right":

| Template declares | Invariant checked |
|---|---|
| `rule` or `differentiates` | `d/dx(prompt) == answer` |
| `integrates` | `d/dx(answer) == prompt`, and grading is up to a constant |
| neither | `prompt == answer` numerically, over the declared domain |
| `tags=("not-equal-to-prompt",)` | none of the above — **must** supply a `verify` hook, or the build refuses it |

`rule` and `differentiates` are separate because chapters 7 and 8 differentiate
without being *about* a named rule, and `rule` also labels the recognition
options.

Where none of these fit — limits, related rates, critical points — the template
asserts its own invariant at build time against an independent SymPy
computation: `sp.limit` for chapter 6, `-F_x/F_y` for implicit derivatives, a
finite difference for chapter 7's numeric derivative. Without that, a template
whose `expr` is its own `answer` would have a vacuous check and could ship a
wrong limit unnoticed.

## The placement diagnostic

Eleven items, reusing the **real chapter templates** rather than parallel
questions, so what the quiz measures and what the chapters teach can't drift.

- **Two items per chapter minimum**, enforced by `check_diagnostic`. Skipping a
  chapter on one lucky answer would be worse than offering no diagnostic.
- **Threshold is every item.** One wrong keeps the chapter. A false "you know
  this" becomes a gap that resurfaces three chapters later disguised as being
  bad at calculus; a false "study this" costs one easy afternoon.
- **No hints or worked steps** — the pipeline strips them. Hints would measure
  how well you follow guidance, not what you retain.
- **Chapter 4 is never tested**, because it declares `skippable=False`: its
  log-likelihood half appears in no school syllabus, so school fluency is no
  evidence of knowing it. Testing it would produce a result the app must discard.
- Passing marks a chapter as *folded away*, not deleted. Every fold is
  reversible from the campaign map.

## Design decisions worth not re-litigating

**Plain-text answers, not a maths keyboard.** `6x*cos(3x^2+1)` is faster to type
than to click for someone who writes code all day. A live KaTeX preview renders
what you typed, so a typo is visible before submitting. The preview's
text→LaTeX conversion is cosmetic only — grading parses the raw text, so an
imperfect preview can never cause a wrong grade.

**Hints are never locked.** The button shows elapsed time and suggests waiting
ten minutes, then lets you decide. A hard lock punishes people for being stuck,
which is exactly when they're learning.

**No streaks.** This runs alongside a full-time job; streak pressure turns it
into a chore.

**Levels complete at 80%, not 100%.** Demanding every last problem turns
practice into a completionist grind. The roadmap's mastery gate is the real
measure.

**Nothing is hard-locked.** Level order is a recommendation. The planned
diagnostic exists precisely so chapters can be skipped.

**mathjs number-only build** (`mathjs/number`): no BigNumber, Complex or matrix
support, none of which this app uses. Saves 283 kB raw / 76 kB gzipped, and
out-of-domain results arrive as `NaN` rather than complex numbers — which the
finiteness check rejects anyway.

## Known limitations

- **Progress is `localStorage`.** No cross-device sync. JSON export/import is
  not built yet.
- **Bundle is 882 kB / 264 kB gzipped**, still mostly mathjs. Acceptable for a
  page the browser caches, but the obvious win if it ever matters is replacing
  mathjs with a small purpose-built expression parser.
- **Google Fonts (Spectral, IBM Plex Sans/Mono) could not be verified rendering**
  in the dev preview pane, which appears to block the font files. The fallback
  stacks — Georgia, system sans, Consolas — are what you see there, and they
  hold up.
- **A step-by-step solver for arbitrary user input** is the one planned feature
  that genuinely needs runtime symbolic computation. Build-time generation
  cannot cover it; it would need Pyodide (~10 MB) or a curated input set.

## Commands

```bash
python tools/build.py          # generate bundle.json + schema.ts
python -m pytest tools/tests   # 230 tests: maths, invariants, bundle
cd web && npm test             # KaTeX render check + typecheck
cd web && npm run dev          # dev server on :5173
cd web && npm run build        # static output in web/dist
```

Adding a chapter: create `content/chapters/NN-slug/` with `templates.py`,
`chapter.py`, `concept.md` and an `__init__.py`, then add the directory name to
`CHAPTER_DIRS` in `tools/build.py`.
