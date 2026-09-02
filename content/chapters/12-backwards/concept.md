## Integration is a question, not a procedure

Differentiation is mechanical. Given a function, there is a rule for every
shape, and you follow it.

Integration is not like that. The question is:

> **Which function has this as its derivative?**

You answer it by recognising the shape, or by transforming it into one you
recognise. That's why integration feels more like puzzle-solving — and why the
one check you can always perform is **differentiate your answer back**. If you
get the integrand, you were right. That check is total, cheap, and available
every single time.

## Honest expectations

Integration matters **less** for AI than differentiation does.

Differentiation is the engine of training: backpropagation is differentiation and
nothing else. Integration turns up mostly in probability — expectations,
marginalisation, normalising constants — and in practice those integrals are
usually intractable, which is precisely why sampling methods and variational
approximations exist at all.

So: get real fluency here, enough to read the notation and do the standard
manipulations. Don't chase exotic techniques. Chapter 16 is the one that pays
off.

## The power rule backwards

$$\int x^n\,dx = \frac{x^{n+1}}{n+1} + C \qquad (n \ne -1)$$

Differentiating multiplies by the power and reduces it. So integrating must
**raise** the power and divide by the new one. Exactly the reverse, in reverse
order.

Works for every $n$ except one.

## The exception, and why

$n = -1$ would give $\tfrac{x^0}{0}$ — a division by zero. The power rule simply
cannot do it.

$$\int \frac{1}{x}\,dx = \ln|x| + C$$

Chapter 8 told you $\tfrac{d}{dx}\ln x = \tfrac1x$, so this is that read
backwards. The exception exists for a boring arithmetical reason, not a deep one
— but it's the single most commonly missed integral, so it's worth knowing that
$\tfrac1x$ is *the* special case.

## The table, read backwards

$$\int e^x dx = e^x + C \qquad \int \cos x\,dx = \sin x + C$$

$$\int \sin x\,dx = -\cos x + C \qquad \int \frac{1}{1+x^2}dx = \arctan x + C$$

**The minus sign moves.** Differentiating $\cos$ gives $-\sin$; integrating
$\sin$ gives $-\cos$. Roughly half the sign errors in Act III are this one fact,
and the fix is the same as always: differentiate your answer back and look.

## Why + C, and why it stops mattering

If $F' = f$, then $(F + 7)' = f$ too — constants differentiate away. So there
isn't *an* antiderivative, there's a whole family of them differing by a
constant, and $+C$ names the family.

Two consequences worth holding onto.

For **indefinite** integrals the $C$ is genuinely part of the answer. It's not
pedantry: solving a differential equation, the $C$ is what the initial condition
pins down.

For **definite** integrals it cancels:

$$(F(b) + C) - (F(a) + C) = F(b) - F(a)$$

which is why you never write $+C$ when there are bounds. Any antiderivative
works, so pick the simplest.

> **How this chapter grades you.** The app knows an antiderivative is only
> defined up to a constant, and compares *differences* between sample points
> rather than absolute values. So $\tfrac{x^3}{3}$, $\tfrac{x^3}{3}+7$ and
> $\tfrac{x^3}{3}+C$ all count as correct — which is the mathematically right
> notion of equality for this question. But $\tfrac{x^3}{3}+x$ does not, because
> $x$ isn't constant. Write the $C$ or leave it off; it makes no difference.

## Where this shows up later

- **Chapter 13** connects antiderivatives to areas, which is not obvious and is
  the whole reason this chapter is worth anything.
- **Chapters 14 and 15** are the two techniques for turning unrecognisable
  integrands into recognisable ones.
- **Chapter 16** is where it pays off: expectations, densities, and why every
  $\int p(x)dx$ in a paper means what it means.
