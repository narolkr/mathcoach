/**
 * Answer from a photo of your paper.
 *
 * The flow: photograph your working, the model transcribes it, the transcribed
 * final answer lands in the answer box, you confirm or correct it, and the
 * ordinary fingerprint grader decides whether it is right.
 *
 * That confirmation step is the point. Handwriting recognition misreads a 4 as
 * a 9 sooner or later, and grading a misread answer would tell you you were
 * wrong when you were not - the one failure this app is built to avoid. Putting
 * the transcription in an editable box makes every misread visible and fixable
 * before anything is judged.
 *
 * The correct answer is never sent on this call. See `transcribeAnswer`.
 */

import { useRef, useState } from "react";
import type { Problem } from "../content/schema";
import { prepareImage, type PreparedImage } from "../engine/image";
import { loadSettings } from "../engine/settings";
import { transcribeAnswer, type Transcription } from "../engine/vision";

interface PhotoAnswerProps {
  problem: Problem;
  /** Called with the transcribed answer, to fill the answer box. */
  onTranscribed: (answer: string) => void;
  onNeedsKey: () => void;
  disabled?: boolean;
}

type State =
  | { name: "closed" }
  | { name: "idle" }
  | { name: "working"; note: string; image?: PreparedImage }
  | { name: "done"; image: PreparedImage; result: Transcription }
  | { name: "failed"; message: string; image?: PreparedImage };

export function PhotoAnswer({
  problem,
  onTranscribed,
  onNeedsKey,
  disabled,
}: PhotoAnswerProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<State>({ name: "closed" });

  const run = async (file: File) => {
    const settings = loadSettings();
    if (!settings.apiKey) {
      onNeedsKey();
      return;
    }

    setState({ name: "working", note: "Preparing the photo…" });
    let image: PreparedImage;
    try {
      image = await prepareImage(file);
    } catch (cause) {
      setState({
        name: "failed",
        message:
          cause instanceof Error ? cause.message : "Couldn't read that image.",
      });
      return;
    }

    if (!navigator.onLine) {
      setState({
        name: "failed",
        message:
          "You're offline. Reading a photo is the one thing here that needs a " +
          "connection — you can still type the answer.",
        image,
      });
      return;
    }

    setState({ name: "working", note: "Reading your handwriting…", image });
    try {
      const result = await transcribeAnswer({
        apiKey: settings.apiKey,
        model: settings.model,
        imageBase64: image.base64,
        mimeType: image.mimeType,
        problem,
      });
      setState({ name: "done", image, result });
      if (result.legible && result.finalAnswer) {
        onTranscribed(result.finalAnswer);
      }
    } catch (cause) {
      setState({ name: "failed", message: describeFailure(cause), image });
    }
  };

  const pick = () => fileRef.current?.click();

  return (
    <div className="photo-answer">
      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        // Opens the rear camera straight away on a phone.
        capture="environment"
        hidden
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void run(file);
          event.target.value = "";
        }}
      />

      {state.name === "closed" && (
        <button
          type="button"
          className="btn btn-photo"
          disabled={disabled}
          onClick={() => {
            setState({ name: "idle" });
            pick();
          }}
        >
          <span aria-hidden="true">📷</span> Answer from a photo
        </button>
      )}

      {state.name === "idle" && (
        <button
          type="button"
          className="btn btn-photo"
          disabled={disabled}
          onClick={pick}
        >
          <span aria-hidden="true">📷</span> Choose or take a photo
        </button>
      )}

      {state.name === "working" && (
        <p className="muted photo-status" role="status">
          {state.note}
        </p>
      )}

      {state.name === "failed" && (
        <div className="photo-result">
          <p className="feedback feedback-bad">{state.message}</p>
          <button type="button" className="btn" onClick={pick}>
            Try another photo
          </button>
        </div>
      )}

      {state.name === "done" && (
        <div className="photo-result">
          {!state.result.legible ? (
            <>
              <p className="feedback feedback-warn">
                <strong>Couldn't read it.</strong>{" "}
                {state.result.problem ??
                  "The handwriting wasn't clear enough."}{" "}
                More light, less angle, and fill the frame with just the working.
              </p>
              <button type="button" className="btn" onClick={pick}>
                Try another photo
              </button>
            </>
          ) : (
            <>
              <p className="muted">
                Read from your photo — <strong>check it matches what you
                wrote</strong>, fix it if not, then press Check.
              </p>
              {state.result.lines.length > 0 && (
                <ol className="photo-lines">
                  {state.result.lines.map((line, index) => (
                    <li key={index}>
                      <code>{line}</code>
                    </li>
                  ))}
                </ol>
              )}
              <button type="button" className="btn btn-quiet" onClick={pick}>
                Retake
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * `fetch` rejects with a bare TypeError for both a dead connection and a CORS
 * refusal, and cannot tell them apart - so name the likely cause rather than
 * showing two useless words.
 */
function describeFailure(cause: unknown): string {
  if (!(cause instanceof Error)) {
    return "The request failed for an unknown reason.";
  }
  const looksLikeNetwork =
    cause instanceof TypeError ||
    /failed to fetch|networkerror|load failed/i.test(cause.message);
  if (looksLikeNetwork) {
    return window.location.protocol === "file:"
      ? "The browser blocked the request because this page is a local file. " +
          "Open the app from its web address instead."
      : "Couldn't reach Gemini. Check your connection and try again.";
  }
  return cause.message;
}
