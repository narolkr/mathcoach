/**
 * "Review my working" - photograph what you wrote on paper and have the method
 * checked.
 *
 * Deliberately only available **after** the problem is solved. The learner's
 * own stated pedagogy is struggle before hints, and a camera button sitting
 * next to an unsolved problem is a hint you can reach for at thirty seconds.
 * Here it reviews the route you took to an answer you already got.
 *
 * The verdict on correctness is never shown from here - the grader owns that.
 * This says where the working went wrong, which is the thing the app cannot
 * otherwise see.
 */

import { useRef, useState } from "react";
import type { Answer, Problem } from "../content/schema";
import { prepareImage, type PreparedImage } from "../engine/image";
import { loadSettings } from "../engine/settings";
import { reviewWorking, type WorkingReview as Review } from "../engine/vision";
import { Prose } from "./MathText";

interface WorkingReviewProps {
  problem: Problem;
  /** The slot to review against. Multi-slot problems review the first. */
  answer: Answer;
  onNeedsKey: () => void;
}

type State =
  | { name: "idle" }
  | { name: "preparing" }
  | { name: "sending"; image: PreparedImage }
  | { name: "done"; image: PreparedImage; review: Review }
  | { name: "failed"; message: string; image?: PreparedImage };

export function WorkingReview({
  problem,
  answer,
  onNeedsKey,
}: WorkingReviewProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [state, setState] = useState<State>({ name: "idle" });
  const [opened, setOpened] = useState(false);

  const start = async (file: File) => {
    const settings = loadSettings();
    if (!settings.apiKey) {
      onNeedsKey();
      return;
    }

    setState({ name: "preparing" });
    let image: PreparedImage;
    try {
      image = await prepareImage(file);
    } catch (cause) {
      setState({
        name: "failed",
        message: cause instanceof Error ? cause.message : "Couldn't read that image.",
      });
      return;
    }

    if (!navigator.onLine) {
      setState({
        name: "failed",
        message:
          "You're offline. This is the one feature that needs a connection - " +
          "everything else works without one.",
        image,
      });
      return;
    }

    setState({ name: "sending", image });
    try {
      const review = await reviewWorking({
        apiKey: settings.apiKey,
        model: settings.model,
        imageBase64: image.base64,
        mimeType: image.mimeType,
        problem,
        answer,
      });
      setState({ name: "done", image, review });
    } catch (cause) {
      setState({ name: "failed", message: describeFailure(cause), image });
    }
  };

  if (!opened) {
    return (
      <div className="review-invite">
        <button
          type="button"
          className="btn btn-quiet"
          onClick={() => setOpened(true)}
        >
          📷 Review my working
        </button>
        <p className="muted">
          Wrote it out on paper? Photograph it and have the method checked —
          not the answer, which is already graded.
        </p>
      </div>
    );
  }

  return (
    <section className="review">
      <div className="review-head">
        <p className="eyebrow">Working review</p>
        <button
          type="button"
          className="btn btn-quiet"
          onClick={() => {
            setOpened(false);
            setState({ name: "idle" });
          }}
        >
          Close
        </button>
      </div>

      {state.name === "idle" && (
        <>
          <p className="muted">
            One photo of your working, reasonably lit and right way up. It gets
            downscaled on your phone before sending, and the correct answer is
            sent with it — so the model checks your route rather than solving
            anything.
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => fileRef.current?.click()}
          >
            Take or choose a photo
          </button>
        </>
      )}

      <input
        ref={fileRef}
        type="file"
        accept="image/*"
        // Opens the rear camera directly on a phone rather than the gallery.
        capture="environment"
        hidden
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) void start(file);
          event.target.value = "";
        }}
      />

      {state.name === "preparing" && <p className="muted">Preparing the image…</p>}

      {state.name === "sending" && (
        <>
          <Thumbnail image={state.image} />
          <p className="muted">Reading your working…</p>
        </>
      )}

      {state.name === "failed" && (
        <>
          {state.image && <Thumbnail image={state.image} />}
          <p className="feedback feedback-bad">{state.message}</p>
          <button
            type="button"
            className="btn"
            onClick={() => fileRef.current?.click()}
          >
            Try another photo
          </button>
        </>
      )}

      {state.name === "done" && (
        <>
          <Thumbnail image={state.image} />
          <Verdict review={state.review} answer={answer} />
          <button
            type="button"
            className="btn btn-quiet"
            onClick={() => fileRef.current?.click()}
          >
            Review another photo
          </button>
        </>
      )}
    </section>
  );
}

function Thumbnail({ image }: { image: PreparedImage }) {
  return (
    <figure className="review-thumb">
      <img src={image.previewUrl} alt="Your handwritten working" />
      <figcaption className="muted">
        {image.width}×{image.height}, {Math.round(image.bytes / 1024)} KB sent
      </figcaption>
    </figure>
  );
}

function Verdict({ review, answer }: { review: Review; answer: Answer }) {
  if (!review.legible) {
    return (
      <div className="feedback feedback-warn">
        <p>
          <strong>Couldn't read it.</strong>{" "}
          {review.problem ??
            "The handwriting wasn't legible enough to review."}
        </p>
        <p className="muted">
          More light, less angle, and fill the frame with just the working.
        </p>
      </div>
    );
  }

  const banner = {
    sound: {
      className: "feedback feedback-good",
      title: "Method looks sound.",
    },
    "sound-but-long": {
      className: "feedback feedback-warn",
      title: "Correct, but there was a shorter route.",
    },
    "has-an-error": {
      className: "feedback feedback-bad",
      title: "Something goes wrong in the working.",
    },
  }[review.verdict];

  // When the model recognised one of the problem's own misconceptions, show
  // the app's authored wording for it rather than the model's paraphrase -
  // that text was written deliberately and is known to be accurate.
  const matched = review.firstError?.misconceptionId
    ? answer.distractors.find((d) => d.id === review.firstError?.misconceptionId)
    : undefined;

  return (
    <div className="review-result">
      <div className={banner.className}>
        <strong>{banner.title}</strong>
      </div>

      {review.transcription.length > 0 && (
        <ol className="review-lines">
          {review.transcription.map((line, index) => {
            const isError = review.firstError?.line === index + 1;
            return (
              <li key={index} className={isError ? "review-line-error" : undefined}>
                <code>{line}</code>
              </li>
            );
          })}
        </ol>
      )}

      {review.firstError && (
        <div className="feedback feedback-bad">
          <p>
            <strong>Line {review.firstError.line}.</strong>{" "}
            {review.firstError.whatWentWrong}
          </p>
          {matched && (
            <p>
              <Prose text={matched.feedback} />
            </p>
          )}
        </div>
      )}

      {review.methodNotes.length > 0 && (
        <ul className="review-notes">
          {review.methodNotes.map((note, index) => (
            <li key={index}>{note}</li>
          ))}
        </ul>
      )}

      <p className="review-caveat muted">
        Read as a second opinion on your method. Handwriting recognition is
        imperfect — your answer was already graded exactly, and nothing here
        changes that.
      </p>
    </div>
  );
}

/**
 * Turn a thrown value into something actionable.
 *
 * `fetch` rejects with a bare TypeError ("Failed to fetch") for both a dead
 * connection and a CORS refusal, and it cannot tell them apart. On the offline
 * single-file build that is the single most likely failure - a `file://` page
 * has a null origin, which Google may refuse - so it gets named explicitly
 * rather than left as two useless words.
 */
function describeFailure(cause: unknown): string {
  if (!(cause instanceof Error)) {
    return "The request failed for an unknown reason.";
  }

  const looksLikeNetwork =
    cause instanceof TypeError || /failed to fetch|networkerror|load failed/i.test(cause.message);

  if (looksLikeNetwork) {
    const fromFile = window.location.protocol === "file:";
    return fromFile
      ? "The browser blocked the request. This page is open as a local file, " +
          "and Gemini may refuse requests from a file:// address. Everything " +
          "else works offline - for photo review, serve the app over http " +
          "instead, or open it from a hosted URL."
      : "Couldn't reach Gemini. Check your connection and try again.";
  }

  return cause.message;
}
