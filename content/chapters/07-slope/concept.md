## The definition, once, properly

$$f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}$$

Read it as a fraction first and a limit second. $\dfrac{f(x+h)-f(x)}{h}$ is
change in output over change in input — an ordinary slope, between two points a
distance $h$ apart. The limit closes the gap.

So a derivative is a slope, at a single point, obtained by squeezing a
two-point slope until the two points coincide. And notice the shape: at $h=0$
the fraction is $\tfrac00$, undefined. That's chapter 6's indeterminate form,
and the factor-and-cancel move is what rescues it.

## Doing it once by hand

For $f(x) = 3x^2 - 2x + 5$:

$$f(x+h) = 3(x+h)^2 - 2(x+h) + 5 = 3x^2 + 6xh + 3h^2 - 2x - 2h + 5$$

Subtract $f(x)$ and everything without an $h$ cancels:

$$f(x+h) - f(x) = 6xh + 3h^2 - 2h$$

**Every surviving term has an $h$ in it.** That is not luck — it's why the
division is survivable:

$$\frac{6xh + 3h^2 - 2h}{h} = 6x + 3h - 2$$

Before dividing you had $\tfrac00$. After dividing you have a polynomial, and
letting $h \to 0$ is now just substitution:

$$f'(x) = 6x - 2$$

Do this a few times. Then use the rules for the rest of your life — but knowing
where they come from means you can reconstruct one you've forgotten instead of
guessing.

## What the number means

If $f'(3) = 6$, then near $x=3$, nudging $x$ by a small $\varepsilon$ changes
$f$ by about $6\varepsilon$:

$$f(x + \varepsilon) \approx f(x) + f'(x)\,\varepsilon$$

**The derivative is the multiplier that turns a small change in the input into
the resulting change in the output.**

That reading is the one that matters for machine learning. A gradient says: if I
nudge this weight, how much does the loss move, and in which direction? Gradient
descent is nothing more than reading that number and stepping the other way.

It is *not* the value of $f$, and *not* an average over an interval. It is a
property of one point.

## Checking your own work numerically

You can compute a derivative approximately with arithmetic alone. The **central
difference**:

$$f'(x) \approx \frac{f(x+h) - f(x-h)}{2h} \qquad h \approx 10^{-5}$$

For $f(x)=x^2$ at $x=3$ with $h=0.001$: $\tfrac{3.001^2 - 2.999^2}{0.002} =
6.000$, against an exact answer of 6.

Two reasons this matters more than it looks.

First, it catches your own algebra errors. Differentiate symbolically, then spot-
check numerically. If they disagree, one of them is wrong and you know to look.

Second — **this is the roadmap's final boss.** In Act V you'll derive
backpropagation by hand and verify it against exactly this formula. If the
hand-derived gradients and the finite differences agree to six decimal places,
your calculus is right; if not, it isn't. That check cannot be faked, and you
are meeting it here so it's familiar when it becomes the thing that proves you
learned it.

Why *central* rather than $\tfrac{f(x+h)-f(x)}{h}$? The forward difference has
error proportional to $h$; the central one cancels the first-order term and has
error proportional to $h^2$. Much more accurate for the same $h$.

## Where this shows up later

- **Chapter 8** gives you the rules, so you never have to do the difference
  quotient again.
- **Chapter 9** is what happens when the function is a composition.
- **Chapter 18**'s gradient is this same idea, one variable at a time.
- **Act V** verifies backpropagation with the central difference above.
