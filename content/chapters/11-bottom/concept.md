## This chapter is gradient descent

Training a model means **finding the minimum of a loss function**. Once you see
that, this chapter stops being a school exercise about hills and valleys and
becomes the mathematical content of machine learning.

Everything here reappears in Act V with more variables: learning rates, local
minima, saddle points, and why "convex" is the word that separates easy
optimisation from hard.

## Where the flat points are

At a maximum or minimum, the slope is zero. So:

$$f'(x) = 0$$

Solutions are **critical points**. For $f(x) = x^3 - 3x^2 + 4$:

$$f'(x) = 3x^2 - 6x = 3x(x-2) \quad\Longrightarrow\quad x = 0 \text{ or } x = 2$$

Two flat points. Zero slope alone doesn't tell you *which kind* — that needs the
second derivative.

## Which kind: curvature decides

$f''(x)$ measures how the slope is changing — the curvature.

- $f'' > 0$: the curve bends **upwards**. Zero slope means you're at the bottom
  of a bowl — a **local minimum**.
- $f'' < 0$: bends **downwards**. Zero slope means the top of a hill — a **local
  maximum**.
- $f'' = 0$: the test is silent. Could be an inflection, could be either — look
  at the function directly.

For our cubic, $f''(x) = 6x - 6$. At $x=0$ that's $-6$, a maximum. At $x=2$ it's
$+6$, a minimum.

## Local is all you get

Read that word carefully. The second-derivative test looks at the immediate
neighbourhood and **nothing beyond it**.

Our cubic has a local minimum at $x=2$, and no global minimum whatsoever — it
runs to $-\infty$ as $x \to -\infty$. A method that only inspects the
neighbourhood cannot tell the difference.

**That limitation is why non-convex optimisation is hard.** Gradient descent on a
neural network's loss surface stops when the gradient hits zero. It has no way of
knowing whether it stopped in the best valley or a mediocre one.

## Convexity, and why everyone wants it

If $f'' > 0$ **everywhere**, the function is (strictly) convex, and something
strong follows.

$f'' > 0$ means $f'$ is strictly increasing. A strictly increasing function
crosses zero **at most once**. So there is at most one critical point, it must be
a minimum, and — with nothing able to bend the curve back down — it is the
**global** minimum.

$$f'' > 0 \text{ everywhere} \;\Longrightarrow\; \text{at most one minimum, and it is global}$$

For a convex problem, gradient descent cannot get stuck in the wrong place,
because there is no wrong place. Local and global coincide.

Note the careful *at most*: $e^x$ is convex and never attains a minimum at all.

Linear regression and logistic regression are convex, which is why they train
reliably and reproducibly. Neural networks are emphatically not, which is why
training them involves random restarts, learning-rate schedules, momentum, and a
great deal of empirical taste.

## Step size: what the curvature buys you

Gradient descent:

$$x \leftarrow x - \eta\,f'(x)$$

$\eta$ is the **learning rate**. Take $f(x) = x^2$, so $f'(x) = 2x$:

$$x_{n+1} = x_n - \eta\cdot 2x_n = (1 - 2\eta)\,x_n$$

That shrinks only when $|1-2\eta| < 1$, i.e. $0 < \eta < 1$.

- $\eta = 0.1$: converges quickly.
- $\eta = 1$: jumps straight to the minimum in one step. Exactly right, by luck.
- $\eta = 1.5$: overshoots, oscillates, but still converges.
- $\eta = 2$: $1 \to -1 \to 1 \to -1$ forever. Never settles.
- $\eta = 3$: diverges outright.

So "too large a learning rate diverges" isn't folklore — it's the condition
$|1-\eta f''| < 1$. **The curvature sets the safe range.** That is precisely why
second-order information is valuable, and why Act IV's Hessian matters: in many
variables the curvature differs by direction, so one $\eta$ has to work for all
of them at once.

Too small, meanwhile, converges — just slowly. That is the real trade-off, and it
is the whole reason learning-rate schedules exist.

## Where this shows up later

- **Chapter 18**: the gradient is this in many variables, and descent steps
  against it.
- **Chapter 20**: the Hessian is the multivariable second derivative, and
  positive-definiteness is multivariable convexity.
- **Chapter 24** returns to step size with all of Act IV available.
- **Saddle points** — flat, minimum in one direction, maximum in another — cannot
  exist in one variable. They're the characteristic obstacle in high dimensions,
  and they need chapter 20.
