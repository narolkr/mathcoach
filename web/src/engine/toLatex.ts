/**
 * A best-effort plain-text -> LaTeX conversion, for the live input preview only.
 *
 * Grading never goes through this: `grader.ts` parses the raw text with mathjs
 * instead. So an imperfect preview is cosmetic and can never cause a wrong
 * grade. Its job is to make a typo visible before you submit.
 */

import { normalise } from "./parse";

const FUNCTION_NAMES =
  /\b(sin|cos|tan|sec|csc|cot|sinh|cosh|tanh|exp|ln|log|max|min)\b/g;

export function toLatex(input: string): string {
  if (!input.trim()) return "";
  let out = normalise(input);

  // Named functions get backslashes so KaTeX sets them upright.
  out = out.replace(FUNCTION_NAMES, (name) => `\\${name}`);
  // `log(` came from `ln(` during normalise; show it as ln again.
  out = out.replace(/\\log\(/g, "\\ln(");
  out = out.replace(/\bsqrt\s*\(([^()]*)\)/g, "\\sqrt{$1}");
  out = out.replace(/\bpi\b/g, "\\pi");
  // a/b -> \frac{a}{b} for simple operands, which covers most typed answers.
  out = out.replace(
    /(\([^()]*\)|[\w.]+)\s*\/\s*(\([^()]*\)|[\w.]+)/g,
    "\\frac{$1}{$2}",
  );
  // Multi-character exponents need bracing: x^12 -> x^{12}, x^(2n) -> x^{2n}.
  out = out.replace(/\^\(([^()]*)\)/g, "^{$1}");
  out = out.replace(/\^(-?\w{2,})/g, "^{$1}");
  out = out.replace(/\*/g, " \\cdot ");

  return out;
}
