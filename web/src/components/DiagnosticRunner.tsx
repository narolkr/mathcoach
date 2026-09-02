/**
 * The placement quiz.
 *
 * No hints, no worked steps, one attempt per item - the content pipeline strips
 * those from diagnostic instances. The point is to measure what's retained, not
 * how well someone follows guidance.
 *
 * A chapter is only marked known if *every* item for it is right. The cost of a
 * false "you know this" is a gap that resurfaces chapters later disguised as
 * being bad at calculus; the cost of a false "study this" is one easy
 * afternoon.
 */

import { useMemo, useState } from "react";
import type { Bundle, Diagnostic } from "../content/schema";
import {
  recordDiagnostic,
  type DiagnosticResult,
  type Progress,
} from "../engine/progress";
import { ProblemCard } from "./ProblemCard";
import { Tex } from "./MathText";

interface DiagnosticRunnerProps {
  diagnostic: Diagnostic;
  bundle: Bundle;
  progress: Progress;
  onProgress: (next: Progress) => void;
  onExit: () => void;
}

export function DiagnosticRunner({
  diagnostic,
  bundle,
  progress,
  onProgress,
  onExit,
}: DiagnosticRunnerProps) {
  const [index, setIndex] = useState(0);
  const [correctById, setCorrectById] = useState<Record<string, boolean>>({});
  const [finished, setFinished] = useState(false);

  const chapterName = useMemo(() => {
    const names: Record<string, string> = {};
    for (const chapter of bundle.chapters) {
      names[chapter.id] = `${chapter.number}. ${chapter.name}`;
    }
    return names;
  }, [bundle]);

  const finish = (answers: Record<string, boolean>) => {
    const byChapter: Record<string, boolean[]> = {};
    for (const item of diagnostic.items) {
      (byChapter[item.chapterId] ??= []).push(
        answers[item.problem.id] ?? false,
      );
    }
    const passedByChapter: Record<string, boolean> = {};
    for (const [chapterId, results] of Object.entries(byChapter)) {
      const share = results.filter(Boolean).length / results.length;
      passedByChapter[chapterId] = share >= diagnostic.passThreshold;
    }

    const result: DiagnosticResult = {
      at: new Date().toISOString(),
      passedByChapter,
      itemsCorrect: answers,
    };
    const skippable = new Set(
      bundle.chapters.filter((c) => c.skippable).map((c) => c.id),
    );
    onProgress(recordDiagnostic(progress, result, skippable));
    setFinished(true);
  };

  if (finished) {
    return (
      <Results
        diagnostic={diagnostic}
        bundle={bundle}
        correctById={correctById}
        chapterName={chapterName}
        onExit={onExit}
      />
    );
  }

  const item = diagnostic.items[index];
  const hasNext = index < diagnostic.items.length - 1;

  return (
    <article className="level">
      <header className="level-head">
        <button type="button" className="btn btn-back" onClick={onExit}>
          ← Leave the quiz
        </button>
        <div>
          <p className="eyebrow">
            Placement · {index + 1} of {diagnostic.items.length}
          </p>
          <h2>{diagnostic.title}</h2>
        </div>
      </header>

      <p className="level-blurb">
        Testing: <strong>{item.skill}</strong>. If you don't know it, say so by
        getting it wrong — that's the quiz working, not you failing.
      </p>

      <div className="bar">
        <span
          style={{ width: `${(index / diagnostic.items.length) * 100}%` }}
        />
      </div>

      <ProblemCard
        key={item.problem.id}
        levelId={diagnostic.id}
        levelType="solve"
        problem={item.problem}
        alreadySolved={false}
        progress={progress}
        onProgress={onProgress}
        quizMode
        onQuizAnswer={(correct) =>
          setCorrectById((previous) => ({
            ...previous,
            [item.problem.id]: correct,
          }))
        }
        onNext={() => {
          if (hasNext) {
            setIndex(index + 1);
          } else {
            finish(correctById);
          }
        }}
        hasNext={hasNext}
        onExit={onExit}
      />
    </article>
  );
}

function Results({
  diagnostic,
  bundle,
  correctById,
  chapterName,
  onExit,
}: {
  diagnostic: Diagnostic;
  bundle: Bundle;
  correctById: Record<string, boolean>;
  chapterName: Record<string, string>;
  onExit: () => void;
}) {
  const byChapter: Record<string, typeof diagnostic.items> = {};
  for (const item of diagnostic.items) {
    (byChapter[item.chapterId] ??= []).push(item);
  }

  const skippable = new Set(
    bundle.chapters.filter((c) => c.skippable).map((c) => c.id),
  );

  return (
    <section className="level">
      <header className="level-head">
        <div>
          <p className="eyebrow">Placement results</p>
          <h2>Where you are</h2>
        </div>
      </header>

      <ol className="entries">
        {Object.entries(byChapter).map(([chapterId, items]) => {
          const right = items.filter((i) => correctById[i.problem.id]).length;
          const passed = right === items.length;
          const canSkip = skippable.has(chapterId);
          return (
            <li key={chapterId}>
              <div className="entry-head">
                <strong>{chapterName[chapterId] ?? chapterId}</strong>
                <span
                  className={
                    passed ? "tier tier-easy" : "tier tier-hard"
                  }
                >
                  {right} / {items.length}
                </span>
              </div>
              <p className="muted">
                {passed && canSkip
                  ? "Folded away. Reopen it from the campaign map any time."
                  : passed && !canSkip
                    ? "All correct — but this chapter stays, because its second half isn't school material and the quiz can't test it."
                    : "Worth doing. " +
                      items
                        .filter((i) => !correctById[i.problem.id])
                        .map((i) => i.skill)
                        .join("; ") +
                      "."}
              </p>
              <ul className="misconceptions">
                {items.map((i) => (
                  <li key={i.problem.id}>
                    <span className={correctById[i.problem.id] ? "" : "muted"}>
                      {correctById[i.problem.id] ? "✓" : "✗"} {i.skill}
                    </span>{" "}
                    <Tex latex={i.problem.promptLatex} />
                  </li>
                ))}
              </ul>
            </li>
          );
        })}
      </ol>

      <div className="level-footer">
        <button type="button" className="btn btn-primary" onClick={onExit}>
          Go to the campaign
        </button>
      </div>
    </section>
  );
}
