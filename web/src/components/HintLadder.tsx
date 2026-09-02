/**
 * Progressive hints, one rung at a time.
 *
 * The hint button is NEVER disabled. It shows elapsed time and, before ten
 * minutes, says so - but the learner decides. A hard lock punishes people for
 * being stuck, which is precisely when they are learning most.
 */

import { formatDuration } from "../engine/format";
import { Prose } from "./MathText";

const SUGGESTED_WAIT_SECONDS = 10 * 60;

interface HintLadderProps {
  hints: string[];
  revealed: number;
  onReveal: () => void;
  elapsedSeconds: number;
}

export function HintLadder({
  hints,
  revealed,
  onReveal,
  elapsedSeconds,
}: HintLadderProps) {
  if (hints.length === 0) return null;

  const remaining = hints.length - revealed;
  const early = elapsedSeconds < SUGGESTED_WAIT_SECONDS;

  return (
    <div className="hints">
      {revealed > 0 && (
        <ol className="hint-list">
          {hints.slice(0, revealed).map((hint, index) => (
            <li key={index}>
              <Prose text={hint} />
            </li>
          ))}
        </ol>
      )}

      {remaining > 0 ? (
        <button type="button" className="btn btn-quiet" onClick={onReveal}>
          {revealed === 0 ? "Show a hint" : "Next hint"}
          <span className="hint-count">{remaining} left</span>
        </button>
      ) : (
        <p className="hint-exhausted">
          That's every hint. If you're still stuck, reveal the worked steps —
          then come back to this problem tomorrow.
        </p>
      )}

      {remaining > 0 && early && revealed === 0 && (
        <p className="hint-nudge">
          You've been on this {formatDuration(elapsedSeconds)}. Worth sitting
          with it for ten minutes before taking a hint — but it's your call.
        </p>
      )}
    </div>
  );
}
