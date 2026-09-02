## Why bother with algebra at all

Almost every "I'm bad at calculus" experience is actually an algebra fluency
problem. Not a conceptual gap — a working-memory one.

When you differentiate $\sin(3x^2+1)$, you have to hold the chain rule in mind
*and* track exponents *and* watch signs, all at once. If the algebra costs you
attention, there isn't enough left for the calculus, and the whole thing feels
impossibly hard. Make the algebra automatic and calculus becomes what it
actually is: a small number of ideas, applied carefully.

So this chapter is not revision for its own sake. It is clearing the desk.

## Index laws, the only four that matter

$$x^a \cdot x^b = x^{a+b} \qquad \frac{x^a}{x^b} = x^{a-b}$$

$$\left(x^a\right)^b = x^{ab} \qquad x^{-a} = \frac{1}{x^a}$$

Multiplying **adds** exponents. Dividing **subtracts** them. A power of a power
**multiplies** them. That third one is the most commonly mangled: $(x^2)^3$ is
$x^6$, not $x^5$.

And roots are just fractional powers:

$$\sqrt{x} = x^{1/2} \qquad \sqrt[n]{x} = x^{1/n} \qquad \sqrt[n]{x^m} = x^{m/n}$$

Once you genuinely believe that, roots stop being a separate topic. There is
nothing to remember about $\sqrt[3]{x^{3/2}}$ beyond $\frac{3}{2} \cdot
\frac{1}{3}$.

## A root applies to everything inside

This is where most marks get lost:

$$\left(8x^{-2/3}y^4\right)^{1/2} = 8^{1/2} \cdot x^{-1/3} \cdot y^{2} = 2\sqrt{2}\,x^{-1/3}y^{2}$$

The $\tfrac{1}{2}$ hits the **8** as well as the $x$ and the $y$. Forgetting the
coefficient is the single most common error in this chapter.

## Subtracting a negative

$$\frac{x^{-4}}{x^{-7}} = x^{(-4)-(-7)} = x^{3}$$

Write the subtraction out with its brackets before you evaluate it. Every time.
$(-4) - (-7)$ is unambiguous; "minus four minus minus seven" is how sign errors
happen.

## The leading minus sign

$$-\left(5 - 3(2 - x)\right)$$

Two traps, one after the other.

Inside, $-3 \times (-x) = +3x$, so the bracket becomes $5 - 6 + 3x = -1 + 3x$.
Then the leading minus applies to **both** terms, giving $1 - 3x$.

The mistake is negating only the first term. If you find yourself writing an
answer where one sign changed and another didn't, that's this.

## Roots: pull out the squares

$$\sqrt{72} = \sqrt{36 \cdot 2} = 6\sqrt{2}$$

Find the **largest** square factor. $\sqrt{72} = 2\sqrt{18}$ is true but not
finished — 18 still has a square factor in it.

## Where this shows up later

- **Chapter 4** treats $\ln$ and $e^x$ as inverse operations, which only makes
  sense if fractional and negative exponents are comfortable.
- **Chapter 8**'s power rule turns $\sqrt{x}$ into $\tfrac{1}{2}x^{-1/2}$. If
  you can't move fluently between roots and fractional powers, that derivative
  is unreachable.
- **Act V** is dense with $W^{-1}$, transposes and exponents on matrices. Sign
  and exponent discipline is the whole game there.

## How this chapter grades you

You'll be asked for **coefficients and exponents**, not for a tidied-up
expression. Partly because that's what index laws actually are, and partly for
an honest technical reason: the app grades algebra by evaluating what you type
at sample points, and a simplified expression is numerically identical to the
unsimplified one. If it accepted a free-form answer, pasting the question back
would score. Naming the exponents can't be faked.
