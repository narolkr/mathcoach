## The least obvious theorem in the roadmap

Two apparently unrelated questions:

1. **Slopes.** How fast is this function changing?
2. **Areas.** How much is under this curve?

There is no reason those should have anything to do with each other. They took
centuries to connect. The Fundamental Theorem says they are **inverse
operations**, and that connection is what makes integration computable at all.

## Part 1: differentiation undoes integration

$$\frac{d}{dx}\int_a^x f(t)\,dt = f(x)$$

Accumulate $f$ from $a$ up to $x$. Then ask how fast that running total grows as
$x$ moves. Answer: however big $f$ is right there.

The intuition is worth having. Extending the upper limit by a sliver of width
$dx$ adds a thin strip of area, roughly $f(x)\,dx$. Divide by $dx$ and you get
$f(x)$. The rate at which accumulated area grows is the height of the curve.

Note the lower limit $a$ vanishes. It contributes a constant, and constants
differentiate to zero — which is the same $+C$ freedom as chapter 12, showing up
in a different costume.

## Part 2: integration undoes differentiation

$$\int_a^b f(x)\,dx = F(b) - F(a) \qquad \text{where } F' = f$$

This is the part you compute with, and it is a genuinely remarkable shortcut.

The definition of a definite integral is a limit of sums: chop the interval into
$n$ pieces, add up $n$ rectangles, let $n \to \infty$. Doing that directly is
miserable.

Part 2 says: don't. Find **one** antiderivative, evaluate it at the two ends,
subtract. Infinitely many infinitesimal slices, replaced by two numbers.

## Using it

$$\int_0^3 x^2\,dx$$

An antiderivative is $\tfrac{x^3}{3}$. So:

$$\left[\frac{x^3}{3}\right]_0^3 = \frac{27}{3} - 0 = 9$$

Three things to keep straight.

**Top minus bottom**, in that order. Swapping the bounds negates the integral:
$\int_b^a = -\int_a^b$.

**No $+C$.** It cancels in the subtraction, so any antiderivative works — pick
the simplest one.

**Evaluate $F$, not $f$.** Substituting the bounds into the integrand is a
different (and wrong) calculation.

## A signed area

If $f$ dips below the axis, that part contributes **negatively**.

$$\int_{-1}^{1} x\,dx = 0$$

Not because there's no area, but because the area below cancels the area above.
So "the integral" and "the total area" are different questions, and if you want
the geometric area you need $\int|f|$.

This is not a technicality you can ignore. In Act III it explains cancelling
integrals; in probability it's why densities must be non-negative — a density
that went negative would produce negative probabilities.

## Where this shows up later

- **Chapter 16** relies on Part 2 for every expectation and every improper
  integral.
- **Sampling methods** in ML exist precisely because Part 2 fails in practice for
  most real integrands: no closed-form antiderivative exists, so the shortcut is
  unavailable and you approximate the sum instead. Knowing what you're falling
  back *from* makes those methods much easier to understand.
