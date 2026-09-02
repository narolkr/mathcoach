/**
 * The insight log.
 *
 * Ordered newest first, and it shows what was *learned*, not what was scored.
 * Entries with no insight text are still listed, quietly, because the timing
 * and hint data is useful even when nothing clicked.
 */

import type { Progress } from "../engine/progress";
import { topMisconceptions } from "../engine/progress";
import { formatDuration } from "../engine/format";
import { Tex } from "./MathText";

export function Journal({
  progress,
  onExit,
}: {
  progress: Progress;
  onExit: () => void;
}) {
  const withInsight = progress.journal.filter((entry) => entry.insight);
  const recurring = topMisconceptions(progress).filter(
    (item) => item.count >= 2 && !item.id.startsWith("picked-"),
  );

  return (
    <section className="journal">
      <header className="level-head">
        <button type="button" className="btn btn-back" onClick={onExit}>
          ← Chapter
        </button>
        <div>
          <p className="eyebrow">Insight log</p>
          <h2>What you've learned</h2>
        </div>
      </header>

      {recurring.length > 0 && (
        <div className="gate-card">
          <p className="gate-label">Mistakes worth drilling</p>
          <ul className="misconceptions">
            {recurring.map((item) => (
              <li key={item.id}>
                <code>{item.id.replace(/-/g, " ")}</code>
                <span className="muted"> — {item.count} times</span>
              </li>
            ))}
          </ul>
          <p className="muted">
            These are the patterns you keep hitting. They're the best use of your
            next warm-up block.
          </p>
        </div>
      )}

      {progress.journal.length === 0 ? (
        <p className="muted">
          Nothing logged yet. Solve a problem and write one line about what
          clicked — <em>"Got 9/10"</em> is worth nothing; <em>"I can simplify
          before differentiating"</em> is worth a great deal.
        </p>
      ) : (
        <>
          <p className="muted">
            {withInsight.length} insight{withInsight.length === 1 ? "" : "s"} from{" "}
            {progress.journal.length} logged problem
            {progress.journal.length === 1 ? "" : "s"}.
          </p>
          <ol className="entries">
            {progress.journal.map((entry, index) => (
              <li key={`${entry.problemId}-${index}`}>
                <div className="entry-head">
                  <Tex latex={entry.promptLatex} />
                  <span className="muted">
                    {formatDuration(entry.seconds)} ·{" "}
                    {entry.hintsUsed === 0
                      ? "no hints"
                      : `${entry.hintsUsed} hint${entry.hintsUsed === 1 ? "" : "s"}`}
                  </span>
                </div>
                {entry.insight ? (
                  <p className="entry-insight">{entry.insight}</p>
                ) : (
                  <p className="muted entry-insight">No note.</p>
                )}
                <p className="muted entry-date">
                  {new Date(entry.at).toLocaleString()}
                </p>
              </li>
            ))}
          </ol>
        </>
      )}
    </section>
  );
}
