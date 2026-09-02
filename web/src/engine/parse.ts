/**
 * Turning what the learner typed into something evaluable.
 *
 * Answers are entered as plain text (`6x*cos(3x^2+1)`), not LaTeX. mathjs
 * handles implicit multiplication, so `6x cos(...)` works too. The job here is
 * to forgive the differences between how people write maths and what a parser
 * accepts, and to fail with a message that says what to do differently.
 */

// The number-only build: no BigNumber, Complex or matrix support, which this
// app never uses. Measured saving: 283 kB raw / 76 kB gzipped. It also means an
// out-of-domain result (sqrt of a negative) comes back as NaN rather than a
// complex number, which the finiteness check below already rejects.
import { compile, type EvalFunction } from "mathjs/number";

export interface CompiledAnswer {
  ok: true;
  /**
   * Evaluate at one sample point. `point` is aligned to the `variables` passed
   * to compileAnswer. Returns null where the expression isn't a finite real.
   */
  at: (point: number[]) => number | null;
}

export interface ParseFailure {
  ok: false;
  message: string;
}

/** Cosmetic substitutions - things that mean what they look like. */
const NORMALISERS: Array<[RegExp, string]> = [
  [/\$/g, ""], // pasted from a maths context
  [/[−–—]/g, "-"], // minus sign, en dash, em dash
  [/[·×∗✕]/g, "*"], // middle dot, times, asterisk operator
  [/÷/g, "/"],
  [/π/g, "pi"],
  [/√/g, "sqrt"],
  [/⁄/g, "/"], // fraction slash
  [/[‘’“”]/g, ""], // stray quotes
  [/\s+/g, " "],
];

/** Leading labels people habitually write before the expression itself. */
const LABEL_PREFIX =
  /^\s*(?:dy\s*\/\s*dx|d\s*\/\s*dx|du\s*\/\s*dx|y|u|k|p|q|f\s*'\s*\(\s*x\s*\)|f\s*'|f\s*\^?\s*-?1\s*\(\s*x\s*\)|answer)\s*=\s*/i;

/** `ln` is the notation we teach; mathjs spells natural log `log`. */
const LN_CALL = /\bln\s*\(/g;

/** Inverse trig: we render \arctan, mathjs answers to `atan`. */
const ARC_CALL = /\barc(sin|cos|tan)\s*\(/g;

/**
 * A trailing constant of integration.
 *
 * Antiderivative levels invite "+ C", and mathjs would reject it as an
 * undefined symbol. Dropping it is not a fudge: those answers are graded up to
 * an additive constant anyway, so `+ C` carries no information the grader uses.
 * Only stripped at the very end, so a `C` used as a variable mid-expression
 * still errors honestly.
 */
const TRAILING_CONSTANT = /\s*[+-]\s*[Cc]\s*$/;

/** `sin^2(x)` is standard on paper and unparseable here. Catch it by name. */
const TRIG_POWER = /\b(sin|cos|tan|sec|csc|cot|log|ln)\s*\^/i;

/** Anything that looks like LaTeX rather than plain text. */
const LOOKS_LIKE_LATEX =
  /\\(?:frac|sqrt|left|right|cdot|sin|cos|tan|ln|log|exp|pi)\b|\\\\/;

export function normalise(raw: string): string {
  let out = raw;
  for (const [pattern, replacement] of NORMALISERS) {
    out = out.replace(pattern, replacement);
  }
  out = out.replace(LABEL_PREFIX, "");
  out = out.replace(LN_CALL, "log(");
  out = out.replace(ARC_CALL, "a$1(");
  out = out.replace(TRAILING_CONSTANT, "");
  return out.trim();
}

export function compileAnswer(
  raw: string,
  variables: string[],
): CompiledAnswer | ParseFailure {
  const trimmed = raw.trim();
  if (!trimmed) {
    return { ok: false, message: "Type an answer first." };
  }

  if (LOOKS_LIKE_LATEX.test(trimmed)) {
    return {
      ok: false,
      message:
        "That looks like LaTeX. Type it as plain text instead — for example " +
        "3*x^2 + sin(2*x) rather than \\frac or \\sin.",
    };
  }

  const source = normalise(trimmed);

  if (TRIG_POWER.test(source)) {
    return {
      ok: false,
      message:
        "Write the power outside the brackets — cos(2x)^2 rather than " +
        "cos^2(2x).",
    };
  }

  // Annotated explicitly: `compile` is overloaded for string and string[], and
  // ReturnType<typeof compile> resolves to the array form.
  let compiled: EvalFunction;
  try {
    compiled = compile(source);
  } catch (error) {
    return { ok: false, message: explain(error, source, variables) };
  }

  // Evaluate once up front so a symbol error surfaces as a parse failure rather
  // than as a silently wrong grade. 0.5 is inside every domain we sample.
  const probe: Record<string, number> = {};
  for (const name of variables) probe[name] = 0.5;
  try {
    compiled.evaluate(probe);
  } catch (error) {
    return { ok: false, message: explain(error, source, variables) };
  }

  return {
    ok: true,
    at: (point: number[]) => {
      const scope: Record<string, number> = {};
      variables.forEach((name, index) => {
        scope[name] = point[index];
      });
      let value: unknown;
      try {
        value = compiled.evaluate(scope);
      } catch {
        return null;
      }
      if (typeof value !== "number" || !Number.isFinite(value)) {
        // NaN from out-of-domain, or a non-number from a unit/matrix result.
        return null;
      }
      return value;
    },
  };
}

function explain(error: unknown, source: string, variables: string[]): string {
  const raw = error instanceof Error ? error.message : String(error);

  const undefinedSymbol = /Undefined symbol (\w+)/.exec(raw);
  if (undefinedSymbol) {
    const symbol = undefinedSymbol[1];
    if (symbol === "u") {
      return (
        "Your answer still contains u. Substitute the inner function back in " +
        "so the answer is written in terms of x only."
      );
    }
    const allowed = variables.length
      ? variables.join(", ")
      : "no variables at all";
    return (
      `I don't know what "${symbol}" is. This answer should use ${allowed}, ` +
      `numbers, e, pi, and functions like sin, cos, exp, sqrt and ln.`
    );
  }

  if (/Parenthes|Unexpected end|Value expected/i.test(raw)) {
    const opens = (source.match(/\(/g) ?? []).length;
    const closes = (source.match(/\)/g) ?? []).length;
    if (opens !== closes) {
      return `Unbalanced brackets — ${opens} opening, ${closes} closing.`;
    }
    return "I couldn't read that expression. Check the brackets and operators.";
  }

  return `I couldn't read that expression: ${raw}`;
}
