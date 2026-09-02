/**
 * A chapter's levels as a vertical path.
 *
 * The cross-chapter map lives in Campaign.tsx; this is the within-chapter view,
 * where the order is linear. Nothing is hard-locked - the order is a
 * recommendation, and the diagnostic exists precisely so chapters can be
 * skipped.
 */

import type { Chapter, Level } from "../content/schema";
import { toRoman } from "../engine/format";
import { isLevelComplete, levelOf, type Progress } from "../engine/progress";

interface ChapterViewProps {
  chapter: Chapter;
  progress: Progress;
  onOpenLevel: (level: Level) => void;
  onExit: () => void;
}

export function ChapterView({
  chapter,
  progress,
  onOpenLevel,
  onExit,
}: ChapterViewProps) {
  const completed = chapter.levels.filter((level) =>
    isLevelComplete(progress, level.id, level.problems.length),
  ).length;

  return (
    <section className="chapter">
      <header className="chapter-head">
        <button type="button" className="btn btn-back" onClick={onExit}>
          ← Campaign
        </button>
        <p className="eyebrow">
          Act {toRoman(chapter.act)} · Chapter {chapter.number}
        </p>
        <h1>
          {chapter.name}
          <span className="chapter-tag">{chapter.tag}</span>
        </h1>
        {chapter.subtitle && <p className="level-blurb">{chapter.subtitle}</p>}
        <div className="chapter-progress">
          <div className="bar">
            <span
              style={{ width: `${(completed / chapter.levels.length) * 100}%` }}
            />
          </div>
          <p className="muted">
            {completed} of {chapter.levels.length} levels
          </p>
        </div>
        <div className="gate-card">
          <p className="gate-label">Mastery gate</p>
          <p>{chapter.gate}</p>
        </div>
      </header>

      <ol className="path">
        {chapter.levels.map((level, index) => {
          const done = isLevelComplete(progress, level.id, level.problems.length);
          const solved = levelOf(progress, level.id).solved.length;
          const previousDone =
            index === 0 ||
            isLevelComplete(
              progress,
              chapter.levels[index - 1].id,
              chapter.levels[index - 1].problems.length,
            );

          return (
            <li key={level.id}>
              <button
                type="button"
                className={`node${done ? " node-done" : ""}${
                  !done && previousDone ? " node-next" : ""
                }`}
                aria-label={
                  `Level ${index + 1}: ${level.title}. ${levelKindLabel(level.type)}. ` +
                  (level.type === "concept"
                    ? done
                      ? "Read."
                      : "Not read yet."
                    : `${solved} of ${level.problems.length} solved.`)
                }
                onClick={() => onOpenLevel(level)}
              >
                <span className="node-index" aria-hidden="true">
                  {done ? "✓" : index + 1}
                </span>
                <span className="node-body">
                  <span className="node-title">{level.title}</span>
                  <span className="node-meta">
                    {level.type === "concept"
                      ? "Read"
                      : `${solved} / ${level.problems.length} solved`}
                  </span>
                </span>
                <span className={`node-kind kind-${level.type}`}>
                  {levelKindLabel(level.type)}
                </span>
              </button>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function levelKindLabel(type: Level["type"]): string {
  switch (type) {
    case "concept":
      return "Concept";
    case "choice":
      return "Pick one";
    case "decompose":
      return "Decompose";
    case "solve":
      return "Work it out";
  }
}
