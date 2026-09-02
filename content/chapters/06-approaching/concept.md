## Read this, then move on quickly

Limits are the *logical* foundation of calculus. They are rarely the practical
one.

This is worth saying plainly, because the standard treatment gets people stuck.
Beginners open a calculus book, meet epsilon-delta proofs on page 30, spend a
month there, and quit before ever differentiating anything. The formal machinery
is beautiful and you do not need it — not for chapter 9, not for
backpropagation, not for any of Act V.

What you need is the intuition and a handful of mechanics. That's this chapter.
It is deliberately short.

## What a limit actually says

$$\lim_{x \to a} f(x) = L$$

means: as $x$ gets close to $a$, $f(x)$ gets close to $L$.

The crucial part is what it **doesn't** say. It says nothing about $f(a)$. The
function needn't be defined at $a$ at all. The limit is about the neighbourhood,
not the point — and that gap is exactly what makes derivatives possible, because
the difference quotient is undefined at $h = 0$ and has a limit there anyway.

## 0/0 is a question, not an answer

$$\lim_{x \to 2} \frac{x^2-4}{x-2}$$

Substitute and you get $\tfrac{0}{0}$. That is an **indeterminate form**: it
tells you substitution won't work, and nothing else. It does not mean the limit
is 0, and it does not mean the limit fails to exist.

Factor instead:

$$\frac{x^2-4}{x-2} = \frac{(x-2)(x+2)}{x-2} = x+2 \quad \text{for } x \ne 2$$

So the limit is 4.

Note the honesty of that "for $x \ne 2$". The two functions are genuinely
different — one has a hole — but they agree everywhere near 2, and a limit only
cares about *near*.

## Limits at infinity: only the biggest term matters

$$\lim_{x \to \infty} \frac{3x^2+x}{2x^2-5}$$

Divide everything by the highest power present:

$$\frac{3 + \tfrac1x}{2 - \tfrac{5}{x^2}} \longrightarrow \frac{3}{2}$$

Every $\tfrac1x$ term dies. So the answer is just the **ratio of the leading
coefficients** — the lower-order terms are irrelevant at infinity, however large
they look.

## When a limit doesn't exist

$$\lim_{x \to 2} \frac{1}{x-2}$$

From above, $x-2$ is small and positive, so the fraction runs to $+\infty$.
From below it is small and negative, and the fraction runs to $-\infty$.

The two **one-sided limits** disagree, so there is no two-sided limit. Written:

$$\lim_{x \to 2^{+}} = +\infty \qquad \lim_{x \to 2^{-}} = -\infty$$

A two-sided limit exists only when both sides exist and agree. Checking both
sides is a habit worth having.

## Continuity is three conditions, not one

$f$ is continuous at $a$ when **all three** hold:

1. $\lim_{x \to a} f(x)$ exists,
2. $f(a)$ is defined,
3. they are **equal**.

Each can fail separately, which is why "is it continuous?" has more than one
possible answer:

- A **jump**: the one-sided limits disagree. Condition 1 fails.
- A **hole**: $f$ isn't defined there. Condition 2 fails.
- A **mismatch**: the limit is 6, someone defined $f(3) = 5$. Conditions 1 and 2
  both hold and it's still discontinuous.

That third case is the one people miss.

## L'Hôpital, briefly

When substitution gives $\tfrac00$ or $\tfrac\infty\infty$, you may
differentiate top and bottom **separately**:

$$\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}$$

Only for those indeterminate forms. It is not the quotient rule and looks
nothing like it.

Useful, and genuinely a shortcut — but it needs derivatives, which arrive next
chapter. Come back to it after chapter 8 if you like.

## Where this shows up later

- **Chapter 7** defines the derivative as a limit, and it is precisely a $\tfrac00$
  form: the difference quotient is undefined at $h=0$ and has a limit there. The
  factor-and-cancel move you practised here is the move that makes it work.
- **Chapter 16** needs limits at infinity for improper integrals — how
  $\int_0^\infty e^{-x}dx$ can be finite.
- **Vanishing gradients**, in Act V, are a limit statement about repeated
  multiplication by numbers below 1.
