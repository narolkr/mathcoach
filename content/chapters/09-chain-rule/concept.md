## The one rule that matters most

Every other differentiation rule you'll learn is a convenience. This one is the
engine of machine learning, and it's worth saying plainly why before you touch a
single problem.

A neural network is a **composition**: you take an input, push it through a
layer, push that result through the next layer, and so on. Written out, a
two-layer network is nothing more exotic than

$$f(g(h(x)))$$

Training it means asking "if I nudge a weight buried inside $h$, how much does
the final loss change?" That question *is* the chain rule. Backpropagation is
not based on the chain rule or inspired by it — it is the chain rule, applied to
a composition, plus some bookkeeping so you don't recompute the same
subexpression a million times.

So the fluency you build here is the fluency you will use in Act V. Nothing else
in this roadmap pays off as directly.

## The rule

If $y$ depends on $u$, and $u$ depends on $x$, then

$$\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx}$$

In the form you'll actually use it:

$$\frac{d}{dx}\,f(u) = f'(u) \cdot \frac{du}{dx}$$

**Differentiate the outside, then multiply by the derivative of the inside.**

That "multiply by" is the whole game. Almost every mistake in this chapter is a
missing factor — someone differentiates the outer function correctly and then
simply forgets that the inside also had to be differentiated.

## Finding the inner function

Here's the reliable trick. Imagine evaluating the expression by hand for some
specific $x$, and ask **which operation you would perform last**.

For $\sin(3x^2 + 1)$ at $x = 2$, you'd compute $3 \cdot 4 + 1 = 13$ first, and
take the sine *last*. So sine is the outer function and $u = 3x^2 + 1$ is the
inner one.

That test never fails, and it scales: for a three-layer expression, apply it
again to what's left.

## Worked example, one layer

$$\frac{d}{dx}\,\sin(3x^2+1)$$

Set $u = 3x^2 + 1$, so $\dfrac{du}{dx} = 6x$.

The outer function is $\sin$, and $\dfrac{d}{du}\sin(u) = \cos(u)$. So:

$$\frac{d}{dx}\,\sin(3x^2+1) = \cos(3x^2+1) \cdot 6x = 6x\cos(3x^2+1)$$

Note what the answer is *not*: it is not $\cos(3x^2+1)$. That's the missing-factor
mistake, and it's the one you'll make most often.

## Worked example, three layers

$$\frac{d}{dx}\,\sin\!\big(\ln(3x^2+1)\big)$$

Don't try to do this in one move. Peel from the outside in, and note that **each
layer contributes exactly one factor**.

Outermost is sine, applied to $u = \ln(3x^2+1)$:

$$\cos\!\big(\ln(3x^2+1)\big) \cdot \frac{du}{dx}$$

Now $\dfrac{du}{dx}$ is its own chain rule problem. The log is applied to
$v = 3x^2+1$, and $\dfrac{d}{dv}\ln(v) = \dfrac{1}{v}$, so

$$\frac{du}{dx} = \frac{1}{3x^2+1} \cdot 6x = \frac{6x}{3x^2+1}$$

Putting it together:

$$\frac{d}{dx}\,\sin\!\big(\ln(3x^2+1)\big) = \frac{6x\cos\!\big(\ln(3x^2+1)\big)}{3x^2+1}$$

Three nested functions, three factors. If you ever finish a problem with fewer
factors than layers, you dropped one.

## What to watch for

- **The missing inner factor.** $(3x+1)^4$ differentiates to $12(3x+1)^3$, not
  $4(3x+1)^3$. The inside is $3x+1$, so $du/dx = 3$.
- **Layers you didn't notice.** $\cos^2(2x)$ is *three* deep: a square, a
  cosine, and a $2x$. Count before you start.
- **Signs.** $\dfrac{d}{dx}\cos(u) = -\sin(u) \cdot \dfrac{du}{dx}$. The minus
  sign is quietly responsible for a lot of wrong answers.
- **Multiply, don't add.** The chain rule combines the two derivatives by
  multiplication.

## How this chapter works

Four kinds of level, in escalating order:

1. **Spot the rule** — you don't differentiate anything, you just say which rule
   applies. Fast reps, because recognising the shape is a separate skill from
   executing it.
2. **Decompose** — name $u$ and $du/dx$, nothing more. This is the skill the
   chain rule actually rests on.
3. **Differentiate** — the whole thing, typed out.
4. **Unscaffolded** — mixed problems with no hint about which rule or how many
   layers.

Hints are always available and never locked, but sit with a problem for a while
first. The struggle is where the learning happens; a hint taken in the first
thirty seconds teaches you nothing.
