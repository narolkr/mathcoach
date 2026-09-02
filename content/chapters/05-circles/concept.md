## Deliberately the shortest chapter

Trigonometry matters much less for AI than it does for a physics degree. It
turns up in positional encodings and Fourier features, and then very little
else.

So this chapter is short on purpose, and the roadmap's instruction is explicit:
**resist going deeper here, and spend the time on chapter 4 instead.** You need
enough trig to survive calculus problems, not mastery of it.

Here is the enough.

## The unit circle is two coordinates

Walk anticlockwise round a circle of radius 1, starting at the right. After
turning through angle $\theta$:

- $\cos\theta$ is your **horizontal** position.
- $\sin\theta$ is your **vertical** position.

That's the definition, and it makes the values you need almost derivable rather
than memorised. At $\theta = 0$ you're at $(1, 0)$, so $\cos 0 = 1$ and
$\sin 0 = 0$. At $\theta = \tfrac{\pi}{2}$ you're at the top, $(0,1)$, so it
swaps.

## The five you must know cold

| $\theta$ | $0$ | $\tfrac{\pi}{6}$ | $\tfrac{\pi}{4}$ | $\tfrac{\pi}{3}$ | $\tfrac{\pi}{2}$ |
|---|---|---|---|---|---|
| $\sin\theta$ | $0$ | $\tfrac12$ | $\tfrac{\sqrt2}{2}$ | $\tfrac{\sqrt3}{2}$ | $1$ |
| $\cos\theta$ | $1$ | $\tfrac{\sqrt3}{2}$ | $\tfrac{\sqrt2}{2}$ | $\tfrac12$ | $0$ |

Two things make this a five-minute job rather than a ten-entry one:

- **Sine goes up, cosine comes down.** The two rows are each other reversed.
- **$\tfrac{\pi}{4}$ is the symmetric one**, where horizontal and vertical are
  equal, so both are $\tfrac{\sqrt2}{2}$.

Learn the sine row and read the cosine row backwards.

## The one identity

$$\sin^2\theta + \cos^2\theta = 1$$

It's Pythagoras on the unit circle: the two coordinates of a point at radius 1.
It holds for **any** argument — $\theta$, $2x$, $\ln(x^2+1)$, anything.

Rearranged, which is how you'll actually use it:

$$1 - \sin^2\theta = \cos^2\theta \qquad 1 - \cos^2\theta = \sin^2\theta$$

Note it swaps you to the *other* function, and does nothing at all to the
argument.

## Why radians, and not degrees

Because of this:

$$\lim_{x \to 0} \frac{\sin x}{x} = 1$$

For small $x$ measured in radians, $\sin x \approx x$. Try it: $\sin(0.01) =
0.00999983$.

That single fact is what makes

$$\frac{d}{dx}\sin x = \cos x$$

come out clean. In degrees the same derivative picks up a stray factor of
$\tfrac{\pi}{180}$, and every formula in calculus gets uglier. So calculus uses
radians, always, and you should stop thinking in degrees for the rest of this
roadmap.

## What you actually need downstream

- **Chapter 8**: $\tfrac{d}{dx}\sin x = \cos x$ and $\tfrac{d}{dx}\cos x =
  -\sin x$. Note the minus sign on the second — it causes more wrong answers
  than any other single fact in Act II.
- **Chapter 9**: $\cos^2(2x)$ appears in the chapter gate. You need to see it as
  three nested layers, which needs nothing more than knowing what $\cos$ is.
- **Chapter 14**: $\int \sin x\,dx = -\cos x$. The minus sign moves.

That is genuinely the whole list. Everything else in trigonometry — the sum
formulas, the double-angle identities, the reciprocal functions — you can look up
in the rare event you need it.

## Why this chapter is multiple choice

Recall can't be graded free-form. If the app asked you to *type* $\sin(\pi/6)$,
you could type `sin(pi/6)` and the grader would dutifully evaluate it to $0.5$
and mark you correct, having tested nothing whatsoever. Picking from the five
values in the table means actually knowing the table — and every wrong option is
a real value from it, so you can't eliminate absurdities either.
