## The product rule, read right to left

The product rule says $(uv)' = u'v + uv'$. Integrate both sides and rearrange:

$$\int u\,dv = uv - \int v\,du$$

That's integration by parts. It does not solve an integral outright — it
**trades** one integral for another, and the whole art is making the trade
favourable.

## When to reach for it

Substitution wants a function **and its own derivative** in the integrand. By
parts is for products where that isn't true: $x\ln x$, $x^2 e^x$, $x\sin x$.

Two factors, neither the derivative of the other. Nothing to substitute.

## Choosing u

You get to pick which factor to differentiate. The choice is the whole
technique, and getting it backwards makes the problem worse rather than better.

**Differentiate the factor that gets simpler.**

$$\int x\ln x\,dx$$

Differentiate the $\ln x$: it becomes $\tfrac1x$, and the $\tfrac1x$ then cancels
a power of $x$ in the remaining integral, leaving something elementary. So $u =
\ln x$, $dv = x\,dx$:

$$= \frac{x^2}{2}\ln x - \int \frac{x^2}{2}\cdot\frac{1}{x}\,dx = \frac{x^2}{2}\ln x - \frac{x^2}{4} + C$$

Choose the other way round and you'd still have a logarithm to integrate,
multiplied by something worse. Strictly less progress.

For $\int x^2 e^x dx$ it's the opposite pick: differentiate the **power**, which
drops to $2x$, then to $2$, then vanishes. The exponential never simplifies, so
differentiating it would get you nowhere.

> Some texts teach the mnemonic LIATE for the order to prefer. It's fine, but
> the underlying question is better: *which factor gets simpler when I
> differentiate it?* Ask that and you don't need the acronym.

## Applying it more than once

$$\int x^2 e^x dx = x^2e^x - 2\int x e^x dx$$

The remaining integral still has an $x$ in it, so go again:

$$\int xe^x dx = xe^x - \int e^x dx = xe^x - e^x$$

Putting it together:

$$\int x^2e^xdx = x^2e^x - 2xe^x + 2e^x + C$$

Each pass drops the power by one, and each contributes another minus sign — hence
the alternating signs. For $x^n e^x$ you apply it $n$ times.

The mistake to avoid is stopping after one pass and calling it done. If an $x$
remains in the leftover integral, you aren't finished.

## Where the roadmap stops

By parts is the **last general technique** here. Partial fractions, trig
substitution and the rest exist, and you can look them up if you ever need them.

The reason for stopping: the integrals that matter in machine learning are
mostly not solvable in closed form at all. No technique helps, which is why the
field uses sampling and variational bounds instead. Learning six more
integration techniques would be time not spent on Act IV, where the gradients
live.

## Where this shows up later

- **Chapter 16** needs by parts for $\int x\,p(x)\,dx$ — every expectation of a
  continuous distribution.
- **Entropy** and **KL divergence** are integrals of $p\ln p$, which is this
  chapter's shape exactly.
