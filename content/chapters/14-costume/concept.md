## The chain rule, read right to left

Chapter 9 said:

$$\frac{d}{dx}f(u) = f'(u)\cdot\frac{du}{dx}$$

Read that backwards and you have substitution:

$$\int f'(u)\,\frac{du}{dx}\,dx = f(u) + C$$

**If chapter 9 is solid, this chapter is nearly free.** Whether it feels free is
a good honest check on whether chapter 9 really stuck.

## What to look for

Substitution works when the integrand contains **a function and its own
derivative**, multiplied together.

$$\int 2x\,e^{x^2}\,dx$$

The inside is $x^2$. Its derivative is $2x$ — and there it is, sitting outside
the exponential. That is the signal.

Set $u = x^2$, so $du = 2x\,dx$. The integral becomes:

$$\int e^u\,du = e^u + C = e^{x^2} + C$$

Differentiate that back and you get $2x\,e^{x^2}$. Correct.

## The one that produces a logarithm

$$\int \frac{2x}{x^2+1}\,dx$$

The numerator is exactly the derivative of the denominator. With $u = x^2+1$:

$$\int \frac{du}{u} = \ln|u| + C = \ln\left(x^2+1\right) + C$$

This pattern — **derivative on top, function underneath** — always gives a
logarithm, and it's worth learning to spot on sight. It's the shape you'll meet
constantly in maximum-likelihood work.

## When the factor is off by a constant

$$\int \frac{x}{x^2+1}\,dx$$

Now $u = x^2+1$ gives $du = 2x\,dx$, but the numerator is only $x$ — half of what
you need. Fine: the missing factor is a **constant**, and constants pull out.

$$\frac12\int\frac{du}{u} = \frac12\ln\left(x^2+1\right) + C$$

**Only constants can be fixed this way.** If what's missing is a function of $x$,
substitution has failed and you need a different technique. Trying to "pull out"
an $x$ is the single most common error here, and it is simply not allowed —
$\int x\,g(x)dx \ne x\int g(x)dx$.

## With bounds

Two valid routes, and consistency matters more than which you pick.

**Change the bounds to $u$-values.** For $\int_0^1 \tfrac{x}{x^2+1}dx$ with $u =
x^2+1$: when $x=0$, $u=1$; when $x=1$, $u=2$. So it becomes
$\tfrac12\int_1^2\tfrac{du}{u} = \tfrac12\ln 2$. No substituting back at all.

**Or substitute back to $x$** and use the original bounds.

Both are correct. The failure mode is mixing them — using $u$-bounds with an
$x$-expression. Decide which route you're taking before you start.

## Where this shows up later

- **Chapter 16** substitutes routinely inside expectations.
- **Change of variables** in probability — how a density transforms when you
  transform the random variable — is this rule, generalised. It's what the
  Jacobian determinant is doing in normalising flows.
