/**
 * Reviewing a photo of handwritten working, via the Gemini API.
 *
 * ## What this decides, and what it must not
 *
 * It does **not** decide whether the answer is right. The fingerprint grader
 * already did that, exactly, against a SymPy-verified answer. A vision model
 * reading handwriting will sometimes misread a 4 as a 9, and letting it
 * overrule the grader would reintroduce the one failure this whole app is built
 * to avoid: telling the learner they are wrong when they are not.
 *
 * What it does is read the *working*, which the app otherwise never sees - it
 * only ever receives a final answer. The model is handed the verified answer
 * and the problem's named misconceptions up front, so it is never solving
 * anything, only comparing the lines on the page against a known-correct result
 * and a known error vocabulary. That is a far easier and more reliable job than
 * "solve this photo", and the feedback comes back in the language the app
 * already uses.
 */

import type { Answer, Problem } from "../content/schema";

const ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models";

export interface WorkingReview {
  /** False when the handwriting cannot be read - better than a guess. */
  legible: boolean;
  /** Why, when it is not legible or not mathematics at all. */
  problem?: string;
  /** What the model believes each line says, in order. */
  transcription: string[];
  /** The first line where the working goes wrong, if any. */
  firstError: {
    line: number;
    whatWentWrong: string;
    /** Id of a known misconception, when the error matches one. */
    misconceptionId: string | null;
  } | null;
  /** Remarks on method: a longer route than needed, a risky habit, good work. */
  methodNotes: string[];
  verdict: "sound" | "sound-but-long" | "has-an-error";
}

/** The JSON shape the model is required to return. */
const RESPONSE_SCHEMA = {
  type: "object",
  properties: {
    legible: { type: "boolean" },
    problem: { type: "string" },
    transcription: { type: "array", items: { type: "string" } },
    firstError: {
      type: "object",
      nullable: true,
      properties: {
        line: { type: "integer" },
        whatWentWrong: { type: "string" },
        misconceptionId: { type: "string", nullable: true },
      },
      required: ["line", "whatWentWrong"],
    },
    methodNotes: { type: "array", items: { type: "string" } },
    verdict: {
      type: "string",
      enum: ["sound", "sound-but-long", "has-an-error"],
    },
  },
  required: ["legible", "transcription", "methodNotes", "verdict"],
};

function buildPrompt(problem: Problem, answer: Answer): string {
  const misconceptions = answer.distractors
    .map((d) => `- id "${d.id}": ${d.feedback}`)
    .join("\n");

  const lines = [
    "You are reviewing a photograph of a student's handwritten working for one calculus problem.",
    "",
    `THE PROBLEM (LaTeX): ${problem.promptLatex}`,
    `WHAT WAS ASKED: ${problem.instruction}`,
  ];

  if (problem.assumption) {
    lines.push(`STANDING ASSUMPTION: ${problem.assumption}`);
  }

  lines.push(
    `THE VERIFIED CORRECT ANSWER (LaTeX): ${answer.latex}`,
    "",
    "That answer has already been verified symbolically. It is correct. You are",
    "not being asked to solve the problem or to check the final answer.",
    "",
  );

  if (misconceptions) {
    lines.push("KNOWN MISCONCEPTIONS for this problem, with ids:", misconceptions, "");
  }

  lines.push(
    "YOUR TASK - review the METHOD, line by line:",
    "",
    "1. Transcribe what you can actually read, one array entry per line of",
    "   working. Quote only what is legible. Do not reconstruct what you think",
    "   it ought to say.",
    "2. Identify the FIRST line where the mathematics goes wrong, if any, and",
    "   report its 1-based index into your transcription. If the working is",
    "   correct throughout, set firstError to null.",
    "3. If that error matches one of the known misconceptions above, put its id",
    "   in misconceptionId. Otherwise set misconceptionId to null and describe",
    "   the error plainly in whatWentWrong.",
    "4. In methodNotes, comment on the approach: a route longer than necessary,",
    "   a habit likely to cause errors later, or a genuinely elegant step. Two",
    '   or three short notes at most. Address the student as "you".',
    '5. verdict: "sound" if the method is correct and direct,',
    '   "sound-but-long" if correct but there was a shorter route,',
    '   "has-an-error" if the mathematics is wrong somewhere.',
    "",
    "RULES:",
    "- If you cannot read the handwriting, set legible to false and explain why",
    '  in "problem". Do not guess at the content.',
    "- If the image is not handwritten mathematical working at all, set legible",
    "  to false and say so.",
    "- Never state whether the final answer is right or wrong. The app knows.",
    "- Be specific about WHERE something went wrong, not merely that it did.",
    "- Plain second-person prose. No markdown and no LaTeX in your prose;",
    "  describe expressions in words if you need to refer to them.",
  );

  return lines.join("\n");
}

export interface ReviewRequest {
  apiKey: string;
  model: string;
  imageBase64: string;
  mimeType: string;
  problem: Problem;
  answer: Answer;
}

export async function reviewWorking({
  apiKey,
  model,
  imageBase64,
  mimeType,
  problem,
  answer,
}: ReviewRequest): Promise<WorkingReview> {
  const url =
    `${ENDPOINT}/${encodeURIComponent(model)}:generateContent` +
    `?key=${encodeURIComponent(apiKey)}`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [
        {
          parts: [
            { text: buildPrompt(problem, answer) },
            { inline_data: { mime_type: mimeType, data: imageBase64 } },
          ],
        },
      ],
      generationConfig: {
        responseMimeType: "application/json",
        responseSchema: RESPONSE_SCHEMA,
        // Low, not zero: this is a reading-and-describing task, and a little
        // variation reads better without moving the judgement.
        temperature: 0.2,
      },
    }),
  });

  if (!response.ok) {
    throw new Error(await explainFailure(response));
  }

  const payload = (await response.json()) as {
    candidates?: Array<{
      content?: { parts?: Array<{ text?: string }> };
      finishReason?: string;
    }>;
    promptFeedback?: { blockReason?: string };
  };

  if (payload.promptFeedback?.blockReason) {
    throw new Error(
      `Gemini declined the request (${payload.promptFeedback.blockReason}).`,
    );
  }

  const text = payload.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) {
    const reason = payload.candidates?.[0]?.finishReason;
    throw new Error(
      reason
        ? `Gemini returned nothing usable (finish reason: ${reason}).`
        : "Gemini returned an empty response.",
    );
  }

  let parsed: Partial<WorkingReview>;
  try {
    parsed = JSON.parse(text) as Partial<WorkingReview>;
  } catch {
    throw new Error("Gemini's reply was not the JSON shape we asked for.");
  }

  // A response schema is a request, not a guarantee. Normalise rather than
  // trust, so a malformed field degrades to something harmless.
  return {
    legible: parsed.legible !== false,
    problem: parsed.problem,
    transcription: Array.isArray(parsed.transcription) ? parsed.transcription : [],
    firstError:
      parsed.firstError && typeof parsed.firstError.line === "number"
        ? {
            line: parsed.firstError.line,
            whatWentWrong: parsed.firstError.whatWentWrong ?? "",
            misconceptionId: parsed.firstError.misconceptionId ?? null,
          }
        : null,
    methodNotes: Array.isArray(parsed.methodNotes) ? parsed.methodNotes : [],
    verdict:
      parsed.verdict === "sound" ||
      parsed.verdict === "sound-but-long" ||
      parsed.verdict === "has-an-error"
        ? parsed.verdict
        : "sound",
  };
}

async function explainFailure(response: Response): Promise<string> {
  let detail = "";
  try {
    const body = (await response.json()) as { error?: { message?: string } };
    detail = body.error?.message ?? "";
  } catch {
    // Non-JSON error body; the status alone will have to do.
  }

  switch (response.status) {
    case 400:
      return detail.toLowerCase().includes("api key")
        ? "That API key is not valid. Check it in Settings."
        : `Gemini rejected the request: ${detail || "bad request"}`;
    case 403:
      return "That key is not allowed to use this model. Pick another in Settings.";
    case 404:
      return (
        "That model name does not exist. Use " +
        '"Check which models my key can use" in Settings.'
      );
    case 429:
      return (
        "You have hit the free-tier rate limit. Wait a minute, or switch to a " +
        "lighter model such as gemini-2.5-flash-lite."
      );
    case 503:
      return "Gemini is overloaded right now. Try again shortly.";
    default:
      return `Gemini returned ${response.status}${detail ? `: ${detail}` : ""}`;
  }
}

/**
 * Ask the key which models it can actually use.
 *
 * Worth doing rather than shipping a hard-coded list: Google adds and retires
 * models faster than this app will be rebuilt, and a stale default surfaces as
 * a 404 the learner has no way to diagnose.
 */
export async function listVisionModels(apiKey: string): Promise<string[]> {
  const response = await fetch(
    `${ENDPOINT}?key=${encodeURIComponent(apiKey)}&pageSize=200`,
  );
  if (!response.ok) {
    throw new Error(await explainFailure(response));
  }

  const payload = (await response.json()) as {
    models?: Array<{ name?: string; supportedGenerationMethods?: string[] }>;
  };

  return (payload.models ?? [])
    .filter((model) => model.supportedGenerationMethods?.includes("generateContent"))
    .map((model) => (model.name ?? "").replace(/^models\//, ""))
    // Image-generation, audio and embedding variants cannot review handwriting.
    .filter((name) => name && !/image|audio|embedding|tts|transcribe/i.test(name))
    .sort();
}
