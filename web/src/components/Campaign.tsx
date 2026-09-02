/**
 * The campaign map: chapters grouped by act.
 *
 * Sudoku Coach draws its campaign as a branching skill tree. This is the
 * honest version of that for a linear-with-gaps curriculum: acts as bands,
 * chapters as nodes, and a visible gap where Act I jumps to chapter 9 because
 * chapters 6-8 aren't written yet. Pretending otherwise would misrepresent how
 * much exists.
 *
 * Nothing is hard-locked. `requires` is advisory, and the diagnostic collapses
 * chapters rather than the app forbidding them.
 */

import type { Bundle, Chapter } from "../content/schema";
import { toRoman } from "../engine/format";
import {
  isChapterKnown,
  isLevelComplete,
  setChapterKnown,
  type Progress,
} from "../engine/progress";

interface CampaignProps {
  bundle: Bundle;
  progress: Progress;
  onOpenChapter: (chapter: Chapter) => void;
  onStartDiagnostic: () => void;
  onProgress: (next: Progress) => void;
}

function chapterProgress(progress: Progress, chapter: Chapter) {
  const done = chapter.levels.filter((level) =>
    isLevelComplete(progress, level.id, level.problems.length),
  ).length;
  return { done, total: chapter.levels.length };
}

export function Campaign({
  bundle,
  progress,
  onOpenChapter,
  onStartDiagnostic,
  onProgress,
}: CampaignProps) {
  const acts = [...new Set(bundle.chapters.map((c) => c.act))].sort();
  const takenDiagnostic = progress.diagnostic !== null;

  // Missing-chapter gaps are computed against the previous chapter in the
  // *whole* ordered list, not within an act. Act I ends at chapter 5 and Act II
  // starts at 9, so an act-local comparison would silently hide that 6, 7 and 8
  // don't exist yet - exactly the thing this notice is for.
  // Consolidation tiers share the number of the chapter they follow, so they
  // are excluded from both sides of the comparison or they would invent a gap.
  const numbered = bundle.chapters.filter((c) => !c.isConsolidation);
  const gapBefore = new Map<string, number>();
  numbered.forEach((chapter, index) => {
    const previous = numbered[index - 1];
    if (previous && chapter.number - previous.number > 1) {
      gapBefore.set(chapter.id, chapter.number - previous.number - 1);
    }
  });

  const totalLevels = bundle.chapters.reduce(
    (sum, c) => sum + c.levels.length,
    0,
  );
  const doneLevels = bundle.chapters.reduce(
    (sum, c) => sum + chapterProgress(progress, c).done,
    0,
  );

  return (
    <section className="campaign">
      <header className="campaign-head">
        <p className="eyebrow">Campaign</p>
        <h1>Calculus to Backpropagation</h1>
        <div className="chapter-progress">
          <div className="bar">
            <span
              style={{
                width: totalLevels ? `${(doneLevels / totalLevels) * 100}%` : "0%",
              }}
            />
          </div>
          <p className="muted">
            {doneLevels} of {totalLevels} levels across{" "}
            {bundle.chapters.length} chapters
          </p>
        </div>
      </header>

      {bundle.diagnostic && (
        <div className={takenDiagnostic ? "gate-card" : "gate-card gate-cta"}>
          <p className="gate-label">
            {takenDiagnostic ? "Placement taken" : "Start here"}
          </p>
          {takenDiagnostic ? (
            <>
              <p>
                {progress.knownChapters.length === 0
                  ? "The diagnostic didn't mark any chapter as already known, so Act I is all worth doing."
                  : `${progress.knownChapters.length} chapter${
                      progress.knownChapters.length === 1 ? "" : "s"
                    } marked as already known and folded away below. Reopen any of them if you'd rather not skip.`}
              </p>
              <button
                type="button"
                className="btn btn-quiet"
                onClick={onStartDiagnostic}
              >
                Retake the placement quiz
              </button>
            </>
          ) : (
            <>
              <p>{bundle.diagnostic.blurb}</p>
              <button
                type="button"
                className="btn btn-primary"
                onClick={onStartDiagnostic}
              >
                Take the placement quiz
              </button>
            </>
          )}
        </div>
      )}

      {acts.map((act) => {
        const chapters = bundle.chapters.filter((c) => c.act === act);
        return (
          <section key={act} className="act-band">
            <header className="act-band-head">
              <span className="act-numeral">{toRoman(act)}</span>
              <h2>{bundle.acts[String(act)] ?? `Act ${act}`}</h2>
            </header>

            <ol className="chapter-list">
              {chapters.map((chapter) => {
                const { done, total } = chapterProgress(progress, chapter);
                const known = isChapterKnown(progress, chapter.id);
                const complete = done === total;
                const gap = gapBefore.get(chapter.id) ?? 0;

                return (
                  <li key={chapter.id}>
                    {gap > 0 && (
                      <p className="chapter-gap">
                        {gap} chapter{gap === 1 ? "" : "s"} not written yet
                        {" — "}
                        <a
                          href="https://claude.ai/code/artifact/0b532e7c-2859-4ece-b1fd-633830b2f7f1"
                          target="_blank"
                          rel="noreferrer"
                        >
                          the roadmap covers them
                        </a>
                      </p>
                    )}
                    <div
                      className={
                        "chapter-node" +
                        (known ? " chapter-known" : "") +
                        (complete ? " chapter-complete" : "")
                      }
                    >
                      <button
                        type="button"
                        className="chapter-open"
                        aria-label={
                          (chapter.isConsolidation
                            ? `Consolidation tier: ${chapter.name}. `
                            : `Chapter ${chapter.number}: ${chapter.name}. `) +
                          (known
                            ? "Marked as already known. "
                            : `${done} of ${total} levels complete. `) +
                          chapter.subtitle
                        }
                        onClick={() => onOpenChapter(chapter)}
                      >
                        <span className="chapter-num" aria-hidden="true">
                          {complete
                            ? "✓"
                            : chapter.isConsolidation
                              ? "★"
                              : chapter.number}
                        </span>
                        <span className="chapter-body">
                          <span className="chapter-name">
                            {chapter.name}
                            <span className="chapter-tag-inline">
                              {chapter.tag}
                            </span>
                          </span>
                          {!known && (
                            <span className="chapter-sub">
                              {chapter.subtitle}
                            </span>
                          )}
                          <span className="chapter-meta">
                            {known
                              ? "folded away — you passed this in the diagnostic"
                              : `${done} / ${total} levels`}
                          </span>
                        </span>
                      </button>

                      {chapter.skippable && takenDiagnostic && (
                        <button
                          type="button"
                          className="btn btn-quiet chapter-toggle"
                          onClick={() =>
                            onProgress(
                              setChapterKnown(progress, chapter.id, !known),
                            )
                          }
                        >
                          {known ? "Reopen" : "Mark known"}
                        </button>
                      )}
                    </div>
                  </li>
                );
              })}
            </ol>
          </section>
        );
      })}
    </section>
  );
}
