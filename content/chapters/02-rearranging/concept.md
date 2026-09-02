## Three ways to look at a quadratic

The same quadratic wears three costumes, and each one hands you something
different for free.

$$x^2 - 5x + 6 \quad=\quad (x-2)(x-3) \quad=\quad \left(x - \tfrac{5}{2}\right)^2 - \tfrac{1}{4}$$

- **Expanded** is easy to differentiate and easy to add.
- **Factored** hands you the roots: $x = 2$ and $x = 3$.
- **Completed square** hands you the minimum: at $x = \tfrac{5}{2}$, the value
  is $-\tfrac{1}{4}$.

Being fluent in a quadratic means moving between these three without thinking
about it, and knowing which one answers the question in front of you.

## Factoring: two numbers

For $x^2 + bx + c$, find two numbers that **multiply to $c$** and **add to $b$**.

For $x^2 - 5x + 6$: multiply to 6, add to $-5$. That's $-2$ and $-3$. So
$(x-2)(x-3)$, and the roots are $2$ and $3$.

Note the sign flip. The factor $(x-2)$ gives the root $x = +2$. Getting that
backwards is the most common slip here.

## Completing the square: halve the middle

$$x^2 + bx + c = \left(x + \tfrac{b}{2}\right)^2 + \left(c - \tfrac{b^2}{4}\right)$$

Don't memorise that. Do this instead:

1. **Halve the coefficient of $x$.** That's $p$. It never depends on anything
   else.
2. **Expand $(x+p)^2$** and see what constant it produced.
3. **Correct it.** Whatever the difference is, that's $q$.

For $x^2 + 6x + 5$: $p = 3$. Then $(x+3)^2 = x^2 + 6x + 9$, which overshoots the
$5$ by $4$. So $q = -4$, and the answer is $(x+3)^2 - 4$.

> **Why you'll care.** The exponent of a Gaussian is
> $-\tfrac{(x-\mu)^2}{2\sigma^2}$ — a completed square. Every time you see a
> normal distribution derived, or a ridge-regression solution, someone
> completed a square to get there. It is not a school exercise.

## When it doesn't factor: the formula

$$x = \frac{-b \pm \sqrt{b^2 - 4c}}{2}$$

for a monic quadratic. The quantity under the root, $b^2 - 4c$, is the
**discriminant**, and it tells you the shape of the answer before you finish:

- **Positive and a perfect square** → two rational roots; it would have
  factored.
- **Positive, not a perfect square** → two irrational roots. Leave the surd
  alone. $\tfrac{3-\sqrt5}{2}$ is an exact answer; $0.382$ is a rounded one.
- **Zero** → one repeated root.
- **Negative** → no real roots.

## Inequalities: one rule, easily forgotten

Everything works as it does for equations, with one exception:

> **Multiplying or dividing by a negative reverses the inequality.**

$$-2x + 5 > 1 \;\Longrightarrow\; -2x > -4 \;\Longrightarrow\; x < 2$$

The final step divided by $-2$, so $>$ became $<$. Check the sign of the number
you're dividing by *before* you divide, every single time.

Sanity-check the result by testing a value. Is $x = 0$ in "$x < 2$"? Yes. Does
$-2(0) + 5 > 1$ hold? $5 > 1$, yes. That five-second check catches a flipped
inequality every time.

## What this chapter asks of you

You'll give **roots** and **the $p$ and $q$ of a completed square**, rather than
typing a factored expression. There's an honest technical reason: $x^2 - 4$ and
$(x-2)(x+2)$ are the same function, so no grader that evaluates your answer can
tell a factored form from the original question. Asking for the parameters is
both checkable and the actual work.
