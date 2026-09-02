## Four facts and three rules

That is the entire chapter. Learn these and you can differentiate almost
anything that isn't a composition — and compositions are chapter 9.

## The four derivatives to know cold

$$\frac{d}{dx}e^x = e^x \qquad \frac{d}{dx}\ln x = \frac{1}{x}$$

$$\frac{d}{dx}\sin x = \cos x \qquad \frac{d}{dx}\cos x = -\sin x$$

Three notes.

$e^x$ is its own derivative. That is not a coincidence to memorise but the
*definition* of $e$ — the base for which the exponential's growth rate equals
its value. Everything else about $e$ follows.

$\ln x$ gives $\tfrac1x$. Remember this one: it's why chapter 12's
$\int \tfrac1x dx$ is a logarithm and breaks the power rule's pattern.

And **cos differentiates to minus sin.** That minus sign causes more wrong
answers than any other single fact in Act II. Not because it's hard — because
it's easy to skip.

## The power rule

$$\frac{d}{dx}x^n = n\,x^{n-1}$$

Two things happen: the power comes down as a multiplier, **and** the exponent
drops by one. Doing only one of them is the classic error.

It holds for every $n$ — negative, fractional, irrational. There is no special
case, which is precisely why chapter 1 spent time on fractional powers:

$$\frac{d}{dx}\sqrt{x} = \frac{d}{dx}x^{1/2} = \tfrac12 x^{-1/2} = \frac{1}{2\sqrt{x}}$$

If you can't move fluently between roots and fractional powers, that derivative
is unreachable. If you can, it's one line.

And differentiation is **linear**: it goes through sums and constant multiples
untouched, so you can work term by term.

## The product rule

$$(uv)' = u'v + uv'$$

**Two terms, added.** The tempting wrong answer is $u'v'$, and it's worth being
clear about why it fails: differentiation is not multiplicative. If it were, the
derivative of $x \cdot x$ would be $1 \cdot 1 = 1$ rather than $2x$. One line of
arithmetic kills the shortcut.

The two terms are there because either factor can be the one that's changing.

$$\frac{d}{dx}\left[x^2 e^x\right] = 2x\,e^x + x^2 e^x$$

## The quotient rule

$$\left(\frac{u}{v}\right)' = \frac{u'v - uv'}{v^2}$$

Three things to keep straight: it's **minus**, $u'$ comes **first**, and the
denominator is **squared**.

If you can't recall the order, reconstruct it: $\tfrac{u}{v} = uv^{-1}$ and apply
the product rule. You'll get the quotient rule out, sign and all. Being able to
rebuild a rule beats half-remembering it.

Often you needn't reach for it at all. $\tfrac{x^2+1}{x}$ is just $x +
\tfrac1x$, which the power rule handles in one line. **Simplify before you
differentiate** — it's the single most useful habit in this chapter, and it will
save you repeatedly in Act III.

## Choosing a rule

Look at how the expression is *built*, not at what it contains:

| Shape | Rule |
|---|---|
| A sum of powers | Power rule, term by term |
| Two independent factors multiplied | Product |
| One thing divided by another, $x$ in the denominator | Quotient |
| One function applied to another | **Chain** — chapter 9 |

That last row is the one that matters most, and telling it apart from the others
is the skill chapter 9 opens with. $x^2 e^x$ is a product; $e^{x^2}$ is a
composition. They look similar and are differentiated completely differently.

## Where this shows up later

- **Chapter 9** combines these with the chain rule, and combined problems are
  where they get tested properly.
- **Chapter 11** needs $f'$ and $f''$ for every optimisation problem.
- **Chapter 22** differentiates the sigmoid $\tfrac{1}{1+e^{-x}}$, which is a
  quotient wrapped around a composition — this chapter and the next, together.
