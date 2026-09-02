## The most load-bearing chapter in Act I

A function is a machine: something goes in, something comes out. That's the
whole idea, and it sounds too simple to spend a chapter on.

But here is why this one matters more than its position suggests.
**Composition** — feeding one machine's output into another — is the single idea
that chapter 9 is entirely about, and that Act V is built from. A neural network
*is* a composition:

$$\text{loss} = L\big(f_2(f_1(x))\big)$$

The chain rule is a statement about how to differentiate exactly that shape. So
every minute you spend here making composition automatic is a minute you don't
have to spend confused in chapter 9.

## Composition: substitute the whole thing

$$f(g(x)) \text{ means: work out } g(x) \text{ first, then feed it into } f$$

With $f(x) = x^2 + 1$ and $g(x) = 3x - 2$:

$$f(g(x)) = (3x-2)^2 + 1$$

Everywhere $f$'s formula had an $x$, the **entire** $g(x)$ goes in — brackets
and all. The brackets are not decoration. $(3x-2)^2$ and $3x^2 - 2$ are utterly
different functions.

## Order matters

$$g(f(x)) = 3(x^2+1) - 2 = 3x^2 + 1$$

Compare that with $f(g(x)) = (3x-2)^2 + 1 = 9x^2 - 12x + 5$. Not remotely the
same. Composition is **not commutative**, and mixing up the order is the most
common error in this chapter.

Read $f(g(x))$ from the inside out: $g$ acts first, even though it's written
second.

## Domains: the composition is fussier than either part

This is the part people skip, and it's the part the gate asks about.

Take $f(x) = \sqrt{x-1}$ and $g(x) = \tfrac{1}{x}$. Then:

$$f(g(x)) = \sqrt{\tfrac{1}{x} - 1}$$

Two separate things can now go wrong:

1. **$g$ must be defined.** $\tfrac1x$ needs $x \ne 0$. The inner function's own
   domain always carries through — you can't feed $f$ something $g$ couldn't
   produce.
2. **$f$ must accept what it's given.** $\sqrt{\;}$ needs a non-negative
   argument, so $\tfrac1x - 1 \ge 0$, meaning $\tfrac1x \ge 1$.

For positive $x$ that second condition gives $x \le 1$. For negative $x$,
$\tfrac1x$ is negative and fails outright. So the domain is

$$0 < x \le 1$$

Look at what happened: $f$ was defined on $[1,\infty)$ and $g$ on everything but
zero, and the composition ended up living on a tiny interval neither of them
suggested. **Composing shrinks domains.** Always check both conditions.

And now the striking part. Compose them the other way:

$$g(f(x)) = \frac{1}{\sqrt{x-1}}$$

which needs $x > 1$. So $f(g(x))$ lives on $(0, 1]$ and $g(f(x))$ lives on
$(1, \infty)$ — **the two compositions have no point in common at all.** Not
merely different functions: functions with disjoint domains, sharing not a
single input. If you ever needed convincing that order matters in composition,
that is it.

## Inverses: undo, don't reciprocate

$f^{-1}$ is the machine that undoes $f$. To find it:

1. Write $y = f(x)$.
2. Rearrange until $x$ is alone.
3. Swap the letters back.

For $f(x) = \dfrac{2x+1}{x+3}$:

$$y(x+3) = 2x+1 \;\Longrightarrow\; yx + 3y = 2x + 1 \;\Longrightarrow\; x(y-2) = 1-3y$$

$$x = \frac{1-3y}{y-2} \quad\text{so}\quad f^{-1}(x) = \frac{1-3x}{x-2}$$

> **The notation is genuinely bad.** $f^{-1}(x)$ means the inverse function.
> $f(x)^{-1}$ means $\tfrac{1}{f(x)}$. They are different things wearing the
> same superscript, and confusing them is not a sign you're bad at this — it's
> a sign the notation is poor. Read carefully.

## Where this shows up later

- **Chapter 9**: the chain rule differentiates compositions. If you can see the
  composition, you can apply the rule.
- **Chapter 19**: computation graphs are compositions with branches.
- **Act V**: $\ln$ and $\exp$ undo each other, and softmax is a composition of
  exponentials with a normalisation. Recognising the structure is most of the
  work.
