## Spend longer here than the chapter length suggests

Softmax. Cross-entropy. Log-loss. Log-likelihood. Logits. Log-sum-exp. KL
divergence. Perplexity. Every one of those is **this chapter**, wearing a
different hat.

More confusion about the mathematics of machine learning traces back to shaky
log fluency than to anything in calculus proper. Trigonometry, two chapters from
now, matters far less. Weight your time accordingly.

## Two operations that undo each other

$$e^{\ln x} = x \qquad \ln\left(e^x\right) = x$$

That's the entire relationship. $\ln$ is the inverse of $e^x$, in exactly the
sense chapter 3 meant by inverse: it undoes it.

So whenever an unknown is stuck in an exponent, take a log. Whenever it's stuck
inside a log, exponentiate. That single move solves most equations in this
chapter.

$$e^{2x} = 7 \;\Longrightarrow\; 2x = \ln 7 \;\Longrightarrow\; x = \tfrac{1}{2}\ln 7$$

Leave it as $\tfrac12 \ln 7$. That is the answer; $0.973$ is a rounded version
of it.

## The three laws

$$\ln(ab) = \ln a + \ln b$$

$$\ln\!\left(\frac{a}{b}\right) = \ln a - \ln b$$

$$\ln\left(a^k\right) = k \ln a$$

**Products become sums. Quotients become differences. Powers become
multipliers.** All three run in both directions, and the reverse direction is
just as important.

Worth being explicit about what is *not* true, because these are the errors that
actually happen:

$$\ln(a+b) \ne \ln a + \ln b \qquad \frac{\ln a}{\ln b} \ne \ln\!\left(\frac{a}{b}\right)$$

There is no law for the log of a sum. If you find yourself wanting one, the
step before it went wrong.

## Roots are fractional powers, again

Chapter 1's point, cashing in:

$$\ln\left(\frac{a^2 b}{\sqrt{c}}\right) = 2\ln a + \ln b - \tfrac{1}{2}\ln c$$

The $\sqrt{c}$ is $c^{1/2}$, so it contributes $\tfrac12 \ln c$ — and it's in
the *denominator*, so it comes in negative. Two things to keep straight at once,
which is why this is the gate.

## Why every loss function has a log in it

This is the part that makes the rest of AI notation legible.

Fitting a model to $n$ data points means maximising the probability of seeing the
data you actually saw — a product:

$$\prod_{i=1}^{n} p_i$$

With $n = 10{,}000$ and each $p_i$ around $0.5$, that product is roughly
$10^{-3010}$. A float64 bottoms out around $10^{-308}$. So the number you're
trying to maximise **is exactly zero** in floating point, and every gradient
with it. The computation is not merely imprecise; it has no information left in
it at all.

Take logs and the product becomes a sum:

$$\ln\left(\prod_i p_i\right) = \sum_i \ln p_i$$

Now you're adding ten thousand numbers around $-0.69$, getting about $-6931$ — a
perfectly ordinary number.

And the substitution is free. $\ln$ is **strictly increasing**, so whatever
maximises the likelihood also maximises its log. You give up nothing and gain a
computation that works.

That is the whole reason "log-likelihood" and "log-loss" exist. Not tradition,
not convenience — floating point.

## Where this shows up later

- **Chapter 12**: $\int x^{-1}dx = \ln|x|$, the one antiderivative that breaks
  the power rule's pattern.
- **Chapter 22**: the softmax is $e^{z_i}/\sum_j e^{z_j}$, and cross-entropy is
  $-\sum y_i \ln \hat{y}_i$. Both are this chapter with subscripts.
- **Log-sum-exp**, which you'll meet in any serious implementation, is a trick
  for computing $\ln\sum e^{z_i}$ without the exponentials overflowing. Same
  problem as above, opposite direction.

## What this chapter asks of you

**Expanding** a log asks for the three coefficients rather than the expanded
expression — because $\ln(a^2b/\sqrt c)$ and $2\ln a + \ln b - \tfrac12\ln c$
are the same number, so a grader that evaluates your answer can't tell them
apart. **Condensing** asks for the argument as an expression, which is safe,
since the argument is genuinely different from the sum you started with.
