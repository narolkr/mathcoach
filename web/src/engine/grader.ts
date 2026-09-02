/**
 * Grading by fingerprint. The mirror of tools/mathcoach/fingerprint.py.
 *
 * The tolerance and the comparison rule here MUST match `agrees()` on the
 * Python side, or a problem that validated at build time could still be graded
 * wrongly in the browser. Fingerprints are multivariable: `points[i]` is a
 * tuple aligned to `variables`.
 */

import type { Answer, Fingerprint } from "../content/schema";
import { compileAnswer } from "./parse";

export const REL_TOL = 1e-6;

export type Verdict =
  | { kind: "correct" }
  /** A recognised mistake. The feedback names it. */
  | { kind: "misconception"; distractorId: string; feedback: string }
  /** Wrong, but not a mistake we anticipated. */
  | { kind: "wrong" }
  /** Couldn't even read it - not counted as an attempt. */
  | { kind: "invalid"; message: string };

function closeEnough(a: number, b: number): boolean {
  return Math.abs(a - b) <= REL_TOL * Math.max(1, Math.abs(a), Math.abs(b));
}

/** Sample the learner's expression at a fingerprint's points. */
function sample(
  at: (point: number[]) => number | null,
  fingerprint: Fingerprint,
): number[] | null {
  const ys: number[] = [];
  for (const point of fingerprint.points) {
    const value = at(point);
    if (value === null) return null;
    ys.push(value);
  }
  if (fingerprint.upToConstant) {
    // Compare differences, so any +C cancels. Same convention as Python.
    const base = ys[0];
    return ys.map((y) => y - base);
  }
  return ys;
}

function matches(ys: number[], fingerprint: Fingerprint): boolean {
  if (ys.length !== fingerprint.ys.length) return false;
  return ys.every((y, index) => closeEnough(y, fingerprint.ys[index]));
}

export function gradeAnswer(raw: string, answer: Answer): Verdict {
  const compiled = compileAnswer(raw, answer.fingerprint.variables);
  if (!compiled.ok) {
    return { kind: "invalid", message: compiled.message };
  }

  const ys = sample(compiled.at, answer.fingerprint);
  if (ys === null) {
    return {
      kind: "invalid",
      message:
        "That expression isn't defined everywhere I need to check it. Look for " +
        "a division by zero, or a log or square root of something negative.",
    };
  }

  if (matches(ys, answer.fingerprint)) {
    return { kind: "correct" };
  }

  for (const distractor of answer.distractors) {
    if (matches(ys, distractor.fingerprint)) {
      return {
        kind: "misconception",
        distractorId: distractor.id,
        feedback: distractor.feedback,
      };
    }
  }

  return { kind: "wrong" };
}

/** All slots of a problem must be right for it to count. */
export function gradeAll(inputs: string[], answers: Answer[]): Verdict[] {
  return answers.map((answer, index) => gradeAnswer(inputs[index] ?? "", answer));
}

export function allCorrect(verdicts: Verdict[]): boolean {
  return verdicts.length > 0 && verdicts.every((v) => v.kind === "correct");
}
