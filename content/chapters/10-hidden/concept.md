## When you can't solve for y

$$x^2 + xy + y^3 = 7$$

There is a curve here, and it has a slope at every point. But you cannot
rearrange this into $y = \text{something}$ — the cubic makes it hopeless.

Implicit differentiation gets the slope anyway, without ever solving for $y$.

## One idea: y is a function of x

Differentiate both sides with respect to $x$, treating $y$ as **a function of
$x$** rather than as a constant. Then every $y$ you differentiate contributes a
$\tfrac{dy}{dx}$, by the chain rule.

That's it. That's the whole technique.

$$\frac{d}{dx}y^3 = 3y^2 \cdot \frac{dy}{dx}$$

Compare it with $\tfrac{d}{dx}x^3 = 3x^2$. Same power rule, plus one extra
factor — because $y$ is not the variable you're differentiating with respect to,
so getting from $y$ to $x$ costs a chain rule step.

## Worked through

$$x^2 + xy + y^3 = 7$$

Term by term. The $x^2$ is ordinary. The $xy$ needs the **product rule** *and*
the chain rule. The $y^3$ needs the chain rule:

$$2x + \left(y + x\frac{dy}{dx}\right) + 3y^2\frac{dy}{dx} = 0$$

Now it's just algebra: collect the $\tfrac{dy}{dx}$ terms and divide.

$$\frac{dy}{dx}\left(x + 3y^2\right) = -(2x + y)$$

$$\frac{dy}{dx} = \frac{-(2x+y)}{x+3y^2}$$

**The answer contains both $x$ and $y$**, and that is not a failure. The slope of
an implicit curve genuinely depends on where you are on it, and specifying that
takes both coordinates.

## A result worth noticing

For a circle $x^2 + y^2 = r^2$:

$$2x + 2y\frac{dy}{dx} = 0 \quad\Longrightarrow\quad \frac{dy}{dx} = -\frac{x}{y}$$

The radius to the point $(x,y)$ has slope $\tfrac{y}{x}$. The tangent has slope
$-\tfrac{x}{y}$ — the negative reciprocal. So the tangent is perpendicular to the
radius, which you already knew from geometry, and here the algebra says it in one
line. When a result you know independently drops out of a new technique, that's
the technique earning your trust.

## Related rates: the same chain rule, with time underneath

A sphere's radius grows at 2 units per second. How fast is the volume growing
when $r = 3$?

Both $V$ and $r$ depend on $t$, so:

$$\frac{dV}{dt} = \frac{dV}{dr}\cdot\frac{dr}{dt} = 4\pi r^2 \cdot 2$$

At $r=3$ that is $72\pi$.

The habit worth building: **write down which quantity is changing with respect to
what.** Nearly every related-rates error is differentiating with respect to the
wrong variable, or forgetting the $\tfrac{dr}{dt}$ factor entirely and answering
the per-unit-radius question instead of the per-unit-time one.

## Where this shows up later

- **Chapter 19**'s multivariable chain rule is this generalised: several
  variables, each depending on others, all contributing factors.
- **Backpropagation** is precisely a related-rates problem. The loss depends on
  the weights through many intermediate layers, and you want
  $\tfrac{\partial L}{\partial w}$ without ever writing $L$ as an explicit
  function of $w$ — which, for a real network, you could not do. Implicit
  reasoning about dependencies is not a niche trick; it's the only way through.

## What this chapter asks of you

Free-form answers in $x$ **and** $y$. This is the first chapter where the answer
is genuinely multivariable, and the grader checks it across both — useful
practice for Act IV, where everything has several inputs.
