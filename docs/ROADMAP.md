# MathCoach Roadmap — rusty beginner → backpropagation by hand

**Target:** the calculus that actually underpins AI/ML, learned well enough to derive backpropagation for a small network without help.

**Baseline assumed:** you used differentiation and integration in college, haven't touched them in years, and want to start from the bottom.

**Budget:** ~30 min/day. That puts the final chapter roughly **5–7 months** out. There is no way to make that number much smaller without raising the daily budget — the constraint is retention, not exposure.

> **Start today.** This document is complete and self-sufficient. The app is a better delivery mechanism for the same content, not a prerequisite. If the app never gets finished, this roadmap still gets you there.

---

## 1. The daily protocol

Thirty minutes, three blocks. The shape matters more than the content.

| Block | Time | What |
|---|---|---|
| **Warm-up** | 5 min | 3 easy problems on material from *previous* chapters. Retrieval practice — this is the block that stops you forgetting, and the one you'll be tempted to skip. Don't. |
| **Main** | 15 min | One problem slightly above comfort, on the current chapter. |
| **Challenge** | 10 min | One problem you don't know how to start. Failing this block is the expected outcome and is not a problem. |

Two rules:

1. **Sit with a problem 10–20 minutes before taking a hint.** The struggle is the mechanism, not an obstacle to it. Hints taken early feel productive and teach nothing.
2. **Problems first, theory on demand.** Don't read a chapter front-to-back and then attempt exercises. Attempt a problem, hit a wall, and read only the part that dissolves that specific wall. Theory absorbed this way sticks; theory read in advance does not.

### Difficulty tiers

| Tier | Time | Purpose |
|---|---|---|
| 🟢 Easy | 2–5 min | Fluency and confidence. Should feel automatic. |
| 🔵 Medium | 10–20 min | Actual thinking. Spend most of your time here. |
| 🟠 Hard | 20–45 min | Where new technique gets discovered. |
| 🔴 Challenge | Open-ended | Mathematical creativity. Multiple sittings is normal. |

Aim to live at the **boundary of your ability**. Time spent re-solving what you already know is time spent not learning.

### The insight log

After each session, one entry. Keep it in a single append-only file.

```
Date:
Problem:
Solved: ✅ / ❌
Time:
Technique:
What I learned:
```

The last field is the only one that matters. `"Got 9/10"` is worth nothing. `"I can simplify the expression before differentiating — that turned an ugly quotient rule into a trivial power rule"` is worth a great deal. Review the log monthly; the recurring entries tell you what to drill.

---

## 2. Mastery, not completion

Each chapter below has a **✅ Gate** — a concrete thing you can do when you're actually done. Completion is passing the gate, not reading the material. If you can't pass the gate, you aren't done, regardless of how many problems you've worked.

Gates are written so that you can test yourself honestly on a blank sheet of paper.

---

## Act I — Reflexes

*Goal: make algebra automatic again so it stops consuming attention during calculus. Nearly every "I'm bad at calculus" experience is actually an algebra fluency problem.*

**Take the diagnostic first.** Skip any chapter you can already pass the gate for — you probably retain more of this than you expect. If you pass all five, go straight to Act II.

### 1. Rust Remover — arithmetic and index laws
Fractions, negative and fractional exponents, roots, sign discipline.
- Khan Academy → [Algebra basics](https://www.khanacademy.org/math/algebra-basics)
- Paul's Online Math Notes → *Algebra*, Preliminaries ([tutorial.math.lamar.edu](https://tutorial.math.lamar.edu))

**✅ Gate:** simplify `(8x⁻²ʹ³ · y⁴)ᵛ² / (2x⁴ y⁻¹)` with no calculator and no sign errors, twice in a row.

### 2. Rearranging the Furniture — algebraic manipulation
Factoring, quadratics, completing the square, partial-fraction shapes, inequalities.
- Khan Academy → [Algebra 1](https://www.khanacademy.org/math/algebra) and [Algebra 2](https://www.khanacademy.org/math/algebra2)

**✅ Gate:** complete the square on any quadratic in under 60 seconds. (This is not busywork — it's how you'll read the Gaussian's exponent and how ridge regression gets solved.)

### 3. Machines with Inputs — functions
Domain and range, composition, inverses, graph transformations, piecewise functions.
- Khan Academy → [Precalculus](https://www.khanacademy.org/math/precalculus)

**✅ Gate:** given `f(x) = √(x−1)` and `g(x) = 1/x`, write `f∘g` and `g∘f` with their exact domains. **Composition is the single most load-bearing idea in this entire roadmap** — the chain rule is a statement about composition, and a neural network *is* a composition. Do not move on until this is effortless.

### 4. Growth and Its Undoing — exponentials and logarithms
`eˣ`, `ln x`, all the log laws, change of base, exponential growth/decay.
- Khan Academy → [Precalculus](https://www.khanacademy.org/math/precalculus), exponential & logarithmic units
- 3Blue1Brown → *Essence of Calculus* ep. 5, "What's so special about Euler's number e?"

**✅ Gate:** expand `ln(a²b/√c)` into separate logs and reverse it, instantly. Explain why `log` turns a product of probabilities into a sum, and why that matters when you multiply 10,000 of them together.

> **Weight this chapter heavily.** Softmax, cross-entropy, log-loss, log-likelihood, logits, log-sum-exp, KL divergence, perplexity — every one of them is this chapter. More AI math confusion traces back to shaky log fluency than to anything in calculus proper.

### 5. Just Enough Circles — trigonometry
Unit circle, the values you must know cold, `sin² + cos² = 1`, derivatives-relevant identities only.
- Khan Academy → [Trigonometry](https://www.khanacademy.org/math/trigonometry)

**✅ Gate:** state `sin` and `cos` of 0, π/6, π/4, π/3, π/2 from memory.

> Deliberately shallow. Trig matters much less for AI than for a physics degree — it shows up in positional encodings and Fourier features and little else. You need enough to survive calculus problems, not mastery. Resist the urge to go deeper here; spend that time on chapter 4.

**★ Consolidation — Easy tier.** Mixed Act I problems, no hint about which chapter they're from.

---

## Act II — Change

*Goal: differentiate anything, and understand what a derivative means well enough to reason about gradients later.*

Watch **3Blue1Brown, [Essence of Calculus](https://www.3blue1brown.com/topics/calculus)** episodes 1–4 before starting. Ninety minutes, and it will make this entire act feel inevitable rather than arbitrary. This is the single highest-leverage 90 minutes in the roadmap.

### 6. Approaching Without Arriving — limits and continuity
Limits, one-sided limits, limits at infinity, continuity, indeterminate forms, L'Hôpital.
- 3B1B ep. 7 · Khan Academy → [Differential calculus](https://www.khanacademy.org/math/differential-calculus), limits unit

**✅ Gate:** evaluate `lim(x→0) sin(x)/x` and `lim(x→∞) (3x²+x)/(2x²−5)` and explain why each technique applies.

> Go light here. Limits are the *logical* foundation of calculus but rarely the practical one, and beginners routinely burn a month on epsilon-delta and quit before reaching derivatives. Get the intuition, get the mechanics, move on. You can return if you ever need real analysis.

### 7. The Slope of a Curve — the derivative itself
The difference quotient, the derivative as a limit, as a slope, as an instantaneous rate of change. Numeric differentiation.
- 3B1B ep. 2 · Khan Academy → Differential calculus, derivative intro

**✅ Gate:** derive `f'(x)` for `f(x) = x²` from the difference quotient, on paper, without looking. Then explain in one sentence what the number `f'(3)` *means*.

> Also: compute a derivative numerically as `(f(x+h) − f(x−h)) / 2h` for small `h`. This is not a toy — it is exactly the finite-difference gradient check you'll use to verify your backprop derivation in Act V, and it's how you'll catch your own algebra errors from here on.

### 8. The Rulebook — differentiation rules
Power, constant multiple, sum, product, quotient rules. Derivatives of `eˣ`, `ln x`, `sin`, `cos`.
- 3B1B ep. 3–4 · Paul's Online Math Notes → *Calculus I*, Derivatives

**✅ Gate:** differentiate `x³ln x`, `(2x+1)/(x²−3)`, and `x·eˣ·sin x` correctly on the first attempt.

### 9. Nesting Dolls — **the chain rule**
Composite functions, `u`-substitution thinking, nested compositions three and four deep, chain rule combined with product and quotient rules.
- 3B1B ep. 4 · Khan Academy → Differential calculus, chain rule unit

**✅ Gate:** differentiate `sin(ln(3x²+1))` and `e^(cos²(2x))` with no errors, and — crucially — **explain what you're doing at each layer**, not just execute it.

> **This is the most important chapter in the roadmap. Spend twice as long here as anywhere else.**
>
> Backpropagation *is* the chain rule. Not "uses" it, not "is based on" it — it is the chain rule applied to a composition of functions, plus bookkeeping to avoid recomputing shared subexpressions. A neural network is `f(g(h(x)))` with learnable parameters at each layer. Training it means differentiating that composition.
>
> If you get genuinely fluent at the chain rule — to the point where you see a nested expression and instinctively peel it layer by layer — then Act V is bookkeeping and notation. If you stay shaky here, every later chapter compounds the weakness. Overtrain this one deliberately.

### 10. Hidden Relations — implicit differentiation
Implicit differentiation, related rates.
- 3B1B ep. 6 · Khan Academy → Differential calculus

**✅ Gate:** find `dy/dx` for `x² + xy + y³ = 7`.

**★ Consolidation — Medium tier.** Mixed differentiation, technique not named. This is where you find out whether chapter 9 stuck.

### 11. Finding the Bottom — optimization
Critical points, first and second derivative tests, concavity, convexity, global vs local minima.
- 3B1B ep. 10 · Khan Academy → Differential calculus, applications

**✅ Gate:** find and classify all critical points of `f(x) = x³ − 3x² + 4`, and explain why a convex function has exactly one minimum.

> This is gradient descent in one dimension. Everything about learning rates, local minima, saddle points and why convex problems are "easy" starts here. When you understand that "training a model" means "find the minimum of a loss function," this chapter is the whole idea.

**★ Consolidation — Hard tier.** All of Act II.

---

## Act III — Accumulation

*Goal: integration fluency, and enough understanding of integrals-as-accumulation to read probability notation.*

Watch **3B1B ep. 8–9** first.

Honest expectation-setting: integration is **less** central to AI than differentiation. Differentiation is the engine of training; integration mostly appears in probability theory (expectations, marginalization, normalizing constants) and is usually intractable in practice — which is exactly why sampling and variational methods exist. So: get real fluency, but don't chase exotic techniques.

### 12. Running the Tape Backwards — antiderivatives
Antiderivatives, `+C` and why it's there, basic integral table, power rule in reverse.
- Khan Academy → [Integral calculus](https://www.khanacademy.org/math/integral-calculus)

**✅ Gate:** integrate `x⁻¹`, `x³`, `eˣ`, `sin x`, `1/(1+x²)` from memory, with the `x⁻¹` case correct (it's the one everyone gets wrong).

### 13. The Bridge — the Fundamental Theorem of Calculus
Definite integrals, FTC parts 1 and 2, the derivative–integral inverse relationship.
- 3B1B ep. 8 · Khan Academy → Integral calculus

**✅ Gate:** state both parts of the FTC in your own words and explain why differentiation and integration are inverse operations.

### 14. Change of Costume — substitution
`u`-substitution, recognising the pattern, changing limits on definite integrals.

**✅ Gate:** evaluate `∫ 2x·e^(x²) dx` and `∫₀¹ x/(x²+1) dx`.

> Substitution is the chain rule read right-to-left. If chapter 9 is solid this chapter is nearly free — a good check on whether it really is.

### 15. Trading Places — integration by parts
By parts, choosing `u` and `dv`, cyclic cases.

**✅ Gate:** evaluate `∫ x·ln x dx` and `∫ x²eˣ dx`.

### 16. Areas, Averages, Expectations — definite and improper integrals
Area between curves, average value, improper integrals, convergence.
- Khan Academy → Integral calculus, applications

**✅ Gate:** show `∫₀^∞ e⁻ˣ dx = 1`, and explain why `E[X] = ∫ x·p(x) dx` is a weighted average — and why a probability density must integrate to 1.

> This is the chapter that makes probability notation stop looking like hieroglyphics. Every `∫ p(x) dx` you'll meet in an ML paper is this.

**★ Consolidation — Hard tier.** All of Act III.

---

## Act IV — Many Directions

*Goal: calculus with many inputs. This is where it starts looking like machine learning, because real models have millions of parameters, not one.*

Khan Academy's [Multivariable calculus](https://www.khanacademy.org/math/multivariable-calculus) course was authored by Grant Sanderson (3Blue1Brown) — it's unusually good and the best single resource for this act.

### 17. One Knob at a Time — partial derivatives
Functions of several variables, partial derivatives, higher-order partials.

**✅ Gate:** compute both partials of `f(x,y) = x²y + sin(xy)` and say in words what `∂f/∂x` measures.

> Genuinely easy if Act II is solid: hold every other variable constant and differentiate normally. Loss functions have millions of inputs, and this is how you differentiate with respect to one of them.

### 18. Downhill — the gradient
Gradient vector, directional derivatives, level sets, why the gradient points along steepest ascent.
- 3Blue1Brown → [Neural Networks](https://www.3blue1brown.com/topics/neural-networks) ep. 2, "Gradient descent, how neural networks learn"

**✅ Gate:** compute `∇f` for `f(x,y) = x² + 3xy`, and explain why gradient *descent* steps in the direction `−∇f`.

> The central object of the entire field. "Training" = repeatedly computing this vector and stepping against it.

### 19. Chains in Many Dimensions — the multivariable chain rule
Multivariable chain rule, total derivatives, computation graphs, paths through a graph.

**✅ Gate:** given `z = f(x,y)` with `x = g(t)`, `y = h(t)`, write `dz/dt` — and draw it as a graph where you sum over every path from `t` to `z`.

> **The second most important chapter, after chapter 9.** The "sum over all paths" picture *is* backpropagation through a network with branches and shared weights. Get the graph picture, not just the formula.

### 20. The Full Table — Jacobians and Hessians
Jacobian matrix, Hessian matrix, second-order behaviour, positive definiteness.
- Deisenroth et al., *[Mathematics for Machine Learning](https://mml-book.github.io/)*, ch. 5

**✅ Gate:** write the Jacobian of a function `ℝ² → ℝ²` and explain the difference between a gradient, a Jacobian and a Hessian in one sentence each.

**★ Consolidation — Challenge tier.** All of Act IV.

---

## Act V — The Payoff

*Goal: derive backpropagation by hand and verify it numerically.*

Primary resource for this act: **Parr & Howard, "[The Matrix Calculus You Need For Deep Learning](https://explained.ai/matrix-calculus/)"** — free, and precisely scoped to this target. Supplement with **3B1B Neural Networks ep. 3–4** and *Mathematics for Machine Learning* ch. 5 and 7.

### 21. Calculus on Matrices — matrix calculus
Numerator vs denominator layout (and why the conventions fight each other), `∂(Wx)/∂W`, `∂(Wx)/∂x`, gradients of scalar-valued matrix functions, element-wise operations, the useful identities.

**✅ Gate:** derive `∂(wᵀx)/∂w = x` and `∂(xᵀAx)/∂x = (A + Aᵀ)x` from scratch.

> Mostly notation and bookkeeping over what you already know. Pick **one** layout convention, write it at the top of every page, and stick to it — inconsistent conventions cause more errors here than the calculus does.

### 22. Loss Landscapes — gradients of real loss functions
MSE gradient, sigmoid derivative, softmax Jacobian, cross-entropy gradient, and the softmax + cross-entropy simplification.

**✅ Gate:** derive `∂L/∂z` for softmax + cross-entropy and get the famous `ŷ − y`. Then explain why that startling simplicity is not a coincidence.

> One of the genuinely delightful results in ML. A page of messy Jacobian algebra collapses to "predicted minus actual."

### 23. Backpropagation, By Hand
Forward pass, backward pass, per-layer gradients, weight sharing, and why you cache intermediate activations.
- 3B1B Neural Networks ep. 3–4 · Parr & Howard, later sections

**✅ Gate:** on blank paper, derive every gradient for a 2-layer MLP — `x → W₁ → ReLU → W₂ → softmax → cross-entropy` — including `∂L/∂W₁`, `∂L/∂W₂`, `∂L/∂b₁`, `∂L/∂b₂`.

### 24. Descent — optimization in practice
Gradient descent, learning rate, why it diverges or stalls, momentum intuition, convexity, stochastic vs batch, vanishing gradients.
- *Mathematics for Machine Learning* ch. 7

**✅ Gate:** explain why a too-large learning rate diverges and a too-small one stalls, in terms of the second derivative.

### ★ Final Boss — numerical verification

Implement the 2-layer network from chapter 23 in NumPy. Compute the gradients using **your hand-derived formulas**. Then compute them again by finite differences:

```
∂L/∂θᵢ ≈ (L(θ + h·eᵢ) − L(θ − h·eᵢ)) / 2h        with h ≈ 1e-5
```

If they agree to ~6 decimal places, you're done. **This is the real gate on the whole roadmap** — it cannot be faked, cannot be passed by recognition, and cannot be passed by having read something. Either your calculus is right or the numbers disagree.

---

## 3. Resource stack

Keep it small. Five resources used properly beats twenty owned.

| Purpose | Resource | Cost |
|---|---|---|
| **Intuition — watch first, always** | [3Blue1Brown, *Essence of Calculus*](https://www.3blue1brown.com/topics/calculus) | Free |
| **Structured practice + diagnostics** | [Khan Academy](https://www.khanacademy.org/math) | Free |
| **Reference and problem sets** | [Paul's Online Math Notes](https://tutorial.math.lamar.edu) | Free |
| **The AI-specific payoff** | [Parr & Howard, *The Matrix Calculus You Need For Deep Learning*](https://explained.ai/matrix-calculus/) | Free |
| **The bridge to ML proper** | [Deisenroth, Faisal & Ong, *Mathematics for Machine Learning*](https://mml-book.github.io/) | Free PDF |
| **Backprop intuition** | [3Blue1Brown, *Neural Networks*](https://www.3blue1brown.com/topics/neural-networks) ep. 1–4 | Free |

Everything on the critical path is free. Buy nothing until you've hit a wall that a free resource demonstrably failed to get you over.

**On AoPS and Spivak:** *Art of Problem Solving* and Spivak's *Calculus* are both excellent, and both are off this path. AoPS is competition training aimed at strong middle- and high-schoolers; Spivak is proof-based real analysis. They build genuine mathematical maturity, and they will add months before you reach anything AI-relevant. If you find you *enjoy* the mathematics for its own sake — a real possibility — come back to them as a parallel hobby. Don't put them on the critical path to backprop.

---

## 4. Milestones

| Milestone | At ~30 min/day | Meaning |
|---|---|---|
| Act I complete | Weeks 1–5 *(less if the diagnostic skips chapters)* | Algebra is automatic again |
| Chain rule fluent (ch. 9) | ~Month 2–3 | **The hinge of the whole roadmap** |
| Act II complete | ~Month 3–4 | You can differentiate anything |
| Act III complete | ~Month 4–5 | Probability notation is readable |
| Act IV complete | ~Month 5–6 | Gradients and Jacobians are comfortable |
| Final boss passed | ~Month 6–7 | You derived backprop and verified it numerically |

Slower than this is fine. Skipping the warm-up block is not — that's how you end up back where you started, having "done calculus" twice.

---

## 5. What this roadmap deliberately omits

So you know what you're *not* getting, and don't mistake finishing this for being done:

- **Linear algebra.** Vectors, matrices, eigenvalues, SVD, decompositions. **This matters as much as calculus for AI, arguably more.** Not included because you asked for calculus, and mixing both at once triples the load. Do it next — *Mathematics for Machine Learning* ch. 2–4, or 3Blue1Brown's *Essence of Linear Algebra*.
- **Probability and statistics.** Distributions, Bayes, expectation, variance, maximum likelihood. The third leg. Also next.
- **Series and Taylor expansion.** Genuinely useful (linearization, Newton's method, second-order optimization) but not required for backprop. Available as an optional side branch; 3B1B ep. 11 if you're curious.
- **Real analysis, proof technique, number theory, combinatorics.** Off-path. Enrichment only.

Calculus is one of three legs. Finishing this roadmap makes you comfortable with the calculus in AI — it does not by itself make you an AI specialist. It does remove the largest single obstacle, and it's the right leg to do first, because the other two are easier to learn once the chain rule is second nature.
