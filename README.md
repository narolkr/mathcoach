# MathCoach

Sudoku Coach, but for the calculus that underpins AI.

A campaign of chapters, each teaching one technique, with targeted practice that
forces you to use it — and unscaffolded consolidation stages in between. The
curriculum runs from rusty-beginner algebra to deriving backpropagation by hand.

- **[docs/ROADMAP.md](docs/ROADMAP.md)** — the 24-chapter study roadmap, with a
  mastery gate for every chapter. Self-sufficient: you can study from it with no
  app at all.
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — how the app works, and why.

## Status

**Acts I, II and III complete**, plus the placement diagnostic.

| Act | | Chapter | Levels | Problems |
|---|---|---|---|---|
| I | 1 | Rust Remover — index laws, roots, signs | 4 | 15 |
| I | 2 | Rearranging the Furniture — quadratics | 5 | 15 |
| I | 3 | Machines with Inputs — composition | 4 | 12 |
| I | 4 | Growth and Its Undoing — exponentials and logs | 5 | 11 |
| I | 5 | Just Enough Circles — minimal trig | 4 | 15 |
| II | 6 | Approaching Without Arriving — limits | 5 | 15 |
| II | 7 | The Slope of a Curve — the derivative itself | 4 | 8 |
| II | 8 | The Rulebook — power, product, quotient | 5 | 16 |
| II | 9 | Nesting Dolls — **the chain rule** | 6 | 43 |
| II | 10 | Hidden Relations — implicit differentiation | 3 | 9 |
| II | 11 | Finding the Bottom — optimisation, convexity | 4 | 8 |
| II | ★ | No Scaffolding — consolidation | 2 | 18 |
| III | 12 | Running the Tape Backwards — antiderivatives | 4 | 11 |
| III | 13 | The Bridge — the FTC | 3 | 6 |
| III | 14 | Change of Costume — substitution | 3 | 9 |
| III | 15 | Trading Places — by parts | 3 | 6 |
| III | 16 | Areas, Averages, Expectations | 4 | 8 |
| III | ★ | Which Technique? — consolidation | 1 | 12 |

237 problems and 227 misconception-specific responses, plus an 11-item
placement quiz that folds away the Act I chapters you already know.

★ tiers are the Sudoku Coach BONUS analogue: mixed problems with the hints
stripped and nothing naming the technique, because choosing what to reach for is
a separate skill from executing a named rule.

Chapter 9 was built first on purpose, as a stress test — it is the hardest
chapter in the roadmap and exercises every part of the engine at once.

**Acts IV and V** (multivariable calculus, then matrix calculus and
backpropagation) are written in the roadmap but not yet built.

## On your phone

Two shapes, and which one you want depends on the phone.

### iPhone — install it (the only option that works)

**Chrome on iOS cannot open `file://`, and no iOS browser can.** Apple requires
every browser on the platform to use WebKit, so Chrome, Firefox and Edge on iOS
are all Safari with different chrome, and they inherit Safari's ban on local
file access. There is no browser-side workaround.

So on iPhone, install it as a web app — which is a better result anyway: a
home-screen icon, no browser UI, offline after first load, reliable storage,
and photo review works because it gets a real `https` origin.

```bash
python tools/build.py
cd web && npm run build          # -> web/dist/
```

Put `web/dist/` on any static host (GitHub Pages, Netlify, Cloudflare Pages —
all free, and "hosting" here means uploading files, not running a server). Then
on the iPhone:

1. Open the URL **in Safari** — iOS only offers *Add to Home Screen* from
   Safari, not from Chrome.
2. Share button → **Add to Home Screen**.
3. Open it from the icon. It runs full-screen, and works offline from then on.

A service worker caches the app shell, all 237 problems and KaTeX's fonts on
first visit, so it launches with no network. Nothing is requested again unless
you redeploy.

### Android — either works

The single file is simplest:

```bash
python tools/build.py
cd web && npm run build:offline  # -> web/dist-offline/mathcoach.html
```

One file, ~2.4 MB, with the script, styles, KaTeX's fonts and all 237 problems
inlined; it makes no network requests at all. Copy it to Downloads and open it
from Files, or visit `file:///sdcard/Download/mathcoach.html` in Chrome.

**Why it has to be one file.** A `file://` page can't fetch anything: module
scripts are blocked by CORS, `fetch()` of a sibling file is blocked, and font
files 404 — which for a maths app means KaTeX silently falls back to system
glyphs and every formula renders subtly wrong. So the offline build compiles to
a classic script rather than ES modules and inlines everything.

Or host it and install it, exactly as for iPhone, which also gets you photo
review.

### Back up your progress

Progress lives in browser storage, which phones lose — cleared data, storage
pressure, or opening the file from a different folder. The Journal tab has
**Export progress** and **Restore from file**. Use it occasionally; six months
of work is too much to leave to `localStorage`. If the browser refuses to store
anything at all, the app says so in a banner rather than losing your work
silently.

## Answering from a photo (optional)

Work the problem on paper, tap **📷 Answer from a photo**, and the app reads
your final answer into the answer box. Check it matches what you wrote, then
press Check. Needs a free [Gemini API key](https://aistudio.google.com/apikey),
pasted into the Journal tab under *Photo review*. Everything else works without
it.

**The grader still decides.** Correct or not is settled by the SymPy-verified
fingerprint, exactly as for a typed answer. The model does optical recognition
and nothing else.

**The correct answer is deliberately not sent on that call.** If the model knew
the right answer it would tend to report *that* rather than what is on your
paper, and the app would then be grading the model's knowledge instead of your
work. So the transcription call gets no ground truth, no hints, and no
correctness question — just "read this".

**You confirm before it is graded.** Handwriting recognition misreads a 4 as a 9
eventually. The transcription lands in an editable box alongside the lines it
read, so a misread is visible and fixable rather than silently marked wrong.

Separately, once a problem is solved, **Review my working** sends the photo
*with* the verified answer and the problem's named misconceptions, and comments
on the method: which line went wrong, and whether there was a shorter route.
That is safe to give ground truth to, because the answer is already locked in.
When it recognises one of the app's own misconceptions, the app shows its
authored wording rather than the model's paraphrase.

Practical notes:

- **The key lives in `localStorage`, never in the build.** Baking it into
  `mathcoach.html` would hand your key to anyone you sent that file to. A
  `grep` for it in the packed file returns nothing.
- **Photos are downscaled on-device** to 1568px on the long edge — a 3–12 MB
  phone photo becomes roughly 30 KB, which matters on mobile data and on a
  tight free quota.
- **Free tier is ample**: a few photos per session against limits in the
  hundreds-to-thousands per day. Check
  [your dashboard](https://aistudio.google.com/rate-limit) for current numbers;
  Google cut free quotas in December 2025. Free-tier requests may be used to
  improve Google's models.
- **Models change faster than this app gets rebuilt**, so Settings can ask your
  key which models it can actually use rather than trusting a hard-coded list.
- **Needs a network, and an http(s) origin.** A local `file://` page has a
  `null` origin, which Google may refuse; the app names that cause when it
  happens. The installed web app is fine.

## Setup

Python 3.12+ and Node 20+.

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r tools/requirements.txt
cd web && npm install
```

## Run

```bash
python tools/build.py
```

```bash
cd web && npm run dev
```

Then open http://localhost:5173.

## Test

```bash
python -m pytest tools/tests
```

```bash
cd web && npm test
```

`tools/tests` covers the maths itself: every template's answer is checked
against SymPy's own differentiation, and no distractor may be algebraically or
numerically equal to a correct answer. `npm test` renders every LaTeX string in
the bundle through KaTeX and typechecks the app.

Both must pass for a build to be trustworthy — the Python side cannot know what
KaTeX will accept, and the frontend cannot know whether the maths is right.

## Layout

```
content/chapters/   authored problem templates, level structure, concept cards
tools/              SymPy build pipeline + tests
web/                Vite + React + TypeScript app (static, no backend)
docs/               roadmap and architecture
```

`web/src/content/schema.ts` and `web/public/content/bundle.json` are generated
by `tools/build.py`. Don't edit them.
