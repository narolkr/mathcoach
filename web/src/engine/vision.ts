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

/**
 * Transcription is optical character recognition, not reasoning, so thinking
 * is pure latency here - and worse than that on a 2.5 model, where the output
 * budget *includes* thinking tokens: thinking can eat the whole allowance and
 * return `finishReason: MAX_TOKENS` with no text at all. That is the "sometimes
 * gives no output" failure, and it is not traffic.
 *
 * `gemini-2.5-flash-lite` has thinking off by default and `gemini-2.5-flash`
 * has it on, so this is sent explicitly rather than left to the model default.
 * Older and newer families name the control differently, so a model that
 * rejects the field is retried without it - see `postGenerate`.
 */
const NO_THINKING = { thinkingConfig: { thinkingBudget: 0 } };

/** Statuses where trying again shortly is the right move, not an error. */
const RETRYABLE = new Set([429, 500, 502, 503, 504]);

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * POST to `generateContent`, retrying the transient failures and coping with
 * models that do not accept a thinking budget.
 *
 * Two distinct problems handled in one place:
 *
 * 1. **Overload.** 503 and 429 are common on the free tier and mean "ask again
 *    shortly", not "this cannot work". Failing the whole photo on the first one
 *    made the feature feel broken when it was merely busy.
 * 2. **Field compatibility.** `thinkingConfig` is accepted by the 2.5 family
 *    and rejected by others, and the newer families renamed the control. A 400
 *    naming the field is retried once without it, so this keeps working across
 *    a model change rather than needing a rebuild.
 */
async function postGenerate(
  url: string,
  body: Record<string, unknown>,
  attempts = 3,
): Promise<Response> {
  let withoutThinking = false;

  for (let attempt = 1; ; attempt += 1) {
    const payload = { ...body };
    if (withoutThinking && payload.generationConfig) {
      const config = { ...(payload.generationConfig as Record<string, unknown>) };
      delete config.thinkingConfig;
      payload.generationConfig = config;
    }

    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (response.ok) return response;

    // A rejected thinking budget is worth exactly one retry without it, and
    // the body has to be read to know - so clone rather than consume, leaving
    // the original readable by `explainFailure` if the retry is not taken.
    if (response.status === 400 && !withoutThinking) {
      const text = await response.clone().text();
      if (/thinking/i.test(text)) {
        withoutThinking = true;
        continue;
      }
    }

    if (RETRYABLE.has(response.status) && attempt < attempts) {
      // 1s then 3s. Long enough for a transient overload to clear, short
      // enough that someone holding a phone does not give up.
      await wait(attempt === 1 ? 1000 : 3000);
      continue;
    }

    return response;
  }
}

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

  // Thinking is left on here, unlike transcription: reviewing a method is the
  // one genuinely analytical call in the app, and it is not on the critical
  // path - the answer is already graded by the time it runs.
  const response = await postGenerate(url, {
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

/**
 * Turn a failed response into something both readable and diagnosable.
 *
 * Every branch now ends with Gemini's own message. An earlier version replaced
 * it with our prose on 403 and 404, which made one class of failure impossible
 * to diagnose from the app: a region block reports as a plain 400 whose only
 * distinguishing feature is the sentence "User location is not supported for
 * the API use", and swallowing that sentence left "it says my model is not
 * supported, but the model is listed" with nowhere to go.
 *
 * The two calls differ in that respect: `ListModels` is not region-gated but
 * `generateContent` is, so a model can genuinely appear in the list and still
 * refuse to run.
 */
async function explainFailure(response: Response): Promise<string> {
  let detail = "";
  try {
    const body = (await response.json()) as { error?: { message?: string } };
    detail = body.error?.message ?? "";
  } catch {
    // Non-JSON error body; the status alone will have to do.
  }

  const said = detail ? ` Gemini said: "${detail}"` : "";
  const lower = detail.toLowerCase();

  // Checked before the status switch, because this one arrives as a 400 that
  // otherwise reads like a request we built wrongly.
  if (lower.includes("user location is not supported")) {
    return (
      "Google is refusing the request because of where it thinks you are, not " +
      "because of the model or the photo. If you have a VPN or private relay " +
      "on, turn it off and try again — iCloud Private Relay does this. " +
      "Otherwise the Gemini API is not available from your region yet." +
      said
    );
  }

  if (lower.includes("api key not valid") || lower.includes("api_key_invalid")) {
    return "That API key is not valid. Re-paste it in the Journal tab." + said;
  }

  switch (response.status) {
    case 400:
      return `Gemini rejected the request.${said || " No reason given."}`;
    case 403:
      return (
        "That key is not allowed to use this model. Pick another in the " +
        "Journal tab." + said
      );
    case 404:
      return (
        "That model name does not exist for this API version. Use " +
        '"Check which models my key can use" in the Journal tab.' + said
      );
    case 429:
      return (
        "You have hit the free-tier rate limit. Wait a minute, or switch to a " +
        "lighter model such as gemini-2.5-flash-lite." + said
      );
    case 503:
      return "Gemini is overloaded right now. Try again shortly." + said;
    default:
      return `Gemini returned ${response.status}.${said}`;
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

// ---------------------------------------------------------------------------
// Answering from a photo
// ---------------------------------------------------------------------------

export interface Transcription {
  /** False when the handwriting cannot be read - better than a guess. */
  legible: boolean;
  /** Why, when it is not legible or not mathematics at all. */
  problem?: string;
  /** Each line of working, as read. Shown so a misread is visible. */
  lines: string[];
  /**
   * The final answer, rewritten in the app's input syntax so it can be typed
   * straight into the answer box: `6*x*cos(3*x^2+1)`, not LaTeX.
   */
  finalAnswer: string;
}

const TRANSCRIBE_SCHEMA = {
  type: "object",
  properties: {
    legible: { type: "boolean" },
    problem: { type: "string" },
    lines: { type: "array", items: { type: "string" } },
    finalAnswer: { type: "string" },
  },
  required: ["legible", "lines", "finalAnswer"],
};

/**
 * Read a photo of handwritten working and pull out the final answer.
 *
 * **The correct answer is deliberately NOT sent.** That is the whole integrity
 * of this path. If the model knew the right answer it would tend to report
 * that rather than what is actually on the paper, and the app would then
 * cheerfully grade the model's knowledge instead of the learner's work.
 *
 * So this call does optical recognition and nothing else - no correctness
 * judgement, no hints, no ground truth. The extracted answer goes into the
 * answer box for the learner to confirm, and the existing fingerprint grader
 * decides whether it is right, exactly as it does for a typed answer. A misread
 * is visible and editable before it is ever graded.
 */
export async function transcribeAnswer({
  apiKey,
  model,
  imageBase64,
  mimeType,
  problem,
}: Omit<ReviewRequest, "answer">): Promise<Transcription> {
  const variables = problem.variables.length
    ? problem.variables.join(", ")
    : "x";

  const prompt = [
    "You are reading a photograph of handwritten mathematical working.",
    "",
    "Your ONLY job is optical recognition. Do not solve anything, do not check",
    "anything, and do not correct anything. Report what is on the paper.",
    "",
    "1. Transcribe each line of working into `lines`, in order, as written.",
    "2. Put the writer's FINAL answer in `finalAnswer`, rewritten in this",
    "   plain-text syntax so it can be typed into a computer:",
    "     - multiplication explicit: 6*x, not 6x",
    "     - powers with ^: x^2",
    "     - functions with brackets: sin(2*x), cos(x), ln(x), sqrt(x), exp(x)",
    "     - fractions with /: (2*x+1)/(x^2-3)",
    `     - use only these variables: ${variables}`,
    "     - no LaTeX, no unicode symbols, no equals sign, no 'dy/dx ='",
    "3. If the final answer is wrong, transcribe it wrong. Faithfulness to the",
    "   page matters more than producing something plausible.",
    "",
    "If you cannot read it, set legible to false and say why in `problem`.",
    "If the image is not handwritten mathematics, set legible to false.",
    "Never invent a line you cannot see.",
    "",
    `For context only, the question was: ${problem.instruction}`,
    `The expression under discussion, in LaTeX: ${problem.promptLatex}`,
  ].join("\n");

  const url =
    `${ENDPOINT}/${encodeURIComponent(model)}:generateContent` +
    `?key=${encodeURIComponent(apiKey)}`;

  const response = await postGenerate(url, {
    contents: [
      {
        parts: [
          { text: prompt },
          { inline_data: { mime_type: mimeType, data: imageBase64 } },
        ],
      },
    ],
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: TRANSCRIBE_SCHEMA,
      // Zero, unlike the method review: transcription has one right answer
      // and creativity is purely a liability.
      temperature: 0,
      ...NO_THINKING,
    },
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
    // MAX_TOKENS with no text means the budget went on thinking rather than
    // the answer. Naming it beats "empty response", which sends you looking
    // at your handwriting for a fault that is in the request.
    if (reason === "MAX_TOKENS") {
      throw new Error(
        "The model spent its whole output budget before answering. Switch to " +
          "gemini-2.5-flash-lite in the Journal tab - it does not do that.",
      );
    }
    throw new Error(
      reason
        ? `Gemini returned nothing usable (finish reason: ${reason}).`
        : "Gemini returned an empty response.",
    );
  }

  let parsed: Partial<Transcription>;
  try {
    parsed = JSON.parse(text) as Partial<Transcription>;
  } catch {
    throw new Error("Gemini's reply was not the JSON shape we asked for.");
  }

  return {
    legible: parsed.legible !== false,
    problem: parsed.problem,
    lines: Array.isArray(parsed.lines) ? parsed.lines : [],
    finalAnswer: typeof parsed.finalAnswer === "string" ? parsed.finalAnswer.trim() : "",
  };
}

// ---------------------------------------------------------------------------
// Diagnosing a key
// ---------------------------------------------------------------------------

export interface VisionTest {
  ok: boolean;
  /** What to show the learner: the failure, or what the model read back. */
  message: string;
}

/**
 * Send one tiny generated image down the exact path a real photo takes.
 *
 * Worth its own button because `ListModels` succeeding proves almost nothing:
 * it is not region-gated and does not take an image, so it happily lists a
 * model that `generateContent` will refuse. Without this, diagnosing "the
 * model is listed but the photo fails" means guessing between a region block,
 * a key restriction, a model that cannot see, and a broken image encode.
 *
 * It draws its own image rather than shipping a fixture, so the canvas encode
 * is under test too - that step is where a blank JPEG would come from.
 */
export async function testVision(
  apiKey: string,
  model: string,
): Promise<VisionTest> {
  let base64: string;
  try {
    base64 = drawTestImage();
  } catch (cause) {
    return {
      ok: false,
      message:
        "This browser could not encode an image at all, so the photo feature " +
        `cannot work here. ${cause instanceof Error ? cause.message : ""}`,
    };
  }

  const url =
    `${ENDPOINT}/${encodeURIComponent(model)}:generateContent` +
    `?key=${encodeURIComponent(apiKey)}`;

  const started = Date.now();
  let response: Response;
  try {
    // The same path a photo takes, thinking budget included, so the elapsed
    // time it reports is comparable to what a real transcription will cost.
    response = await postGenerate(url, {
      contents: [
        {
          parts: [
            { text: "Reply with only the characters written in this image." },
            { inline_data: { mime_type: "image/jpeg", data: base64 } },
          ],
        },
      ],
      generationConfig: { temperature: 0, ...NO_THINKING },
    });
  } catch (cause) {
    return {
      ok: false,
      message:
        window.location.protocol === "file:"
          ? "The browser blocked the request because this page is a local file. " +
            "Open the app from its web address instead."
          : "Couldn't reach Gemini at all. Check your connection." +
            (cause instanceof Error ? ` (${cause.message})` : ""),
    };
  }

  if (!response.ok) {
    return { ok: false, message: await explainFailure(response) };
  }

  const payload = (await response.json()) as {
    candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }>;
  };
  const read = payload.candidates?.[0]?.content?.parts?.[0]?.text?.trim();

  if (!read) {
    return {
      ok: false,
      message:
        `${model} accepted the image but returned no text. It may not be a ` +
        "model that can see images — try gemini-2.5-flash.",
    };
  }

  // Not an assertion about accuracy: reading anything back proves the whole
  // path works. Whether it read it *correctly* is the learner's to judge.
  // The timing is the useful part when the complaint is slowness - it turns
  // "feels slow" into a number you can compare between models.
  const seconds = ((Date.now() - started) / 1000).toFixed(1);
  return {
    ok: true,
    message:
      `Working, in ${seconds}s. ${model} read the test image as "${read}" ` +
      '(it says "dy/dx"). A real photo is larger, so expect somewhat longer.',
  };
}

/** A small white image with `dy/dx` drawn on it, encoded as JPEG. */
function drawTestImage(): string {
  const canvas = document.createElement("canvas");
  canvas.width = 320;
  canvas.height = 120;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("No 2D canvas available.");
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "#000000";
  context.font = "48px serif";
  context.fillText("dy/dx", 40, 78);

  const dataUrl = canvas.toDataURL("image/jpeg", 0.9);
  const base64 = dataUrl.slice(dataUrl.indexOf(",") + 1);
  if (base64.length < 100) {
    throw new Error("The canvas encoded to an empty image.");
  }
  return base64;
}
