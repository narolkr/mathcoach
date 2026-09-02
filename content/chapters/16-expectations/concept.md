## The chapter that makes ML notation legible

This is where Act III pays off. Every $\int p(x)\,dx$ you meet in a paper is
this chapter, and after it the notation stops looking like decoration.

## Infinite regions, finite areas

$$\int_0^\infty e^{-x}\,dx$$

The region is unbounded and the answer is **1**. That is genuinely surprising the
first time.

An improper integral is *defined* as a limit — which is what chapter 6 was for:

$$\int_0^\infty e^{-x}dx = \lim_{b\to\infty}\int_0^b e^{-x}dx = \lim_{b\to\infty}\left(1 - e^{-b}\right) = 1$$

The function decays fast enough that the tail contributes almost nothing. Some
functions do; some don't:

$$\int_1^\infty \frac{1}{x^2}dx = 1 \qquad \int_1^\infty \frac{1}{x}dx = \infty$$

Both shrink to zero. Only one shrinks fast enough. $\tfrac1x$ diverges — the tail
keeps adding area forever, just slowly. Whether an integral converges is a
question about the *rate* of decay, and there is no shortcut but to check.

## Signed area, and why densities can't be negative

A definite integral counts area below the axis as negative. So
$\int_{-1}^1 x\,dx = 0$: the halves cancel.

This is why a probability density must be **non-negative** everywhere. A density
dipping below zero would assign negative probability to some region, which means
nothing.

## Why a density integrates to 1

$$\int_{-\infty}^{\infty} p(x)\,dx = 1$$

The reason is as simple as it looks: the integral over all possible values is
the probability that *something happens*, and something does.

That single constraint explains a great deal of notation you've probably seen and
skated over. Every normalising constant exists **only** to make this integral
come out to 1:

- The $\tfrac{1}{\sqrt{2\pi\sigma^2}}$ in front of a Gaussian.
- The $\lambda$ in $\lambda e^{-\lambda x}$.
- Softmax's denominator $\sum_j e^{z_j}$ — the discrete version of exactly the
  same requirement.

None of those constants carry information about the *shape* of the distribution.
They are bookkeeping, forced by this one condition. Once you know that, they stop
being intimidating.

And note: a density may exceed 1. A narrow spike can be very tall. It is the
**area** that is capped, not the height — which is the difference between a
density and a probability, and a distinction worth being firm about.

## Expectation is a weighted average

$$E[X] = \int x\,p(x)\,dx$$

Compare the discrete case, which you already believe:

$$E[X] = \sum_i x_i\,P(x_i)$$

Same idea. Each possible value, weighted by how likely it is. The sum becomes an
integral; the probabilities become a density. Nothing else changes.

That reading generalises to everything:

$$E[f(X)] = \int f(x)\,p(x)\,dx$$

**$E[\cdot]$ is always a weighted average, and the weights are always the
probabilities.** Once that's automatic, a great deal of machine-learning
notation becomes readable on sight — because almost every loss function in the
field is an expectation:

$$\text{loss} = E_{(x,y)\sim\text{data}}\left[\ell(f(x), y)\right]$$

which says: the average of the per-example loss, over the data distribution. And
in practice you approximate it by averaging over a minibatch — which is a
*sample estimate* of that integral, and now you know what it's estimating.

## Mean, median, mode

Three different questions, easily conflated:

- **Mean** $= \int x\,p(x)dx$ — the weighted average.
- **Median**: the value with half the probability either side.
- **Mode**: where $p$ is largest.

For a symmetric distribution they coincide. For a skewed one they don't, and the
exponential density is a clean example: its mode is 0, its median is
$\tfrac{\ln 2}{\lambda}$, its mean is $\tfrac{1}{\lambda}$. All three answer
reasonable questions about "typical", and they give different numbers.

## Where this leaves you

Act III is done. You can differentiate anything, integrate the standard shapes,
and read probability notation — which was the point of it.

**Act IV is where it turns into machine learning**: several variables at once,
gradients, and the chain rule through a computation graph.

One honest note. Most integrals arising in real ML have no closed form. Chapter
13's shortcut is unavailable, and the field falls back on sampling, Monte Carlo
estimates and variational bounds. That is not a failure of what you've learned —
it's why knowing what those methods are *approximating* is the thing that makes
them comprehensible.
