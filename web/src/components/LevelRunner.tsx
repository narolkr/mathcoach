/** One level, problem by problem. Concept levels read; the rest practise. */

import { useEffect, useMemo, useRef, useState } from "react";
import type { Level, Problem } from "../content/schema";
import { levelOf, recordAttempt, type Progress } from "../engine/progress";
import { Markdown } from "./Markdown";
import { ProblemCard } from "./ProblemCard";

interface LevelRunnerProps {
  level: Level;
  progress: Progress;
  onProgress: (next: Progress) => void;
  onExit: () => void;
  /** Photo review needs an API key; this opens Settings. */
  onNeedsKey?: () => void;
}

export function LevelRunner(props: LevelRunnerProps) {
  if (props.level.type === "concept") {
    return <ConceptLevel {...props} />;
  }
  return <PracticeLevel {...props} />;
}

function ConceptLevel({ level, progress, onProgress, onExit }: LevelRunnerProps) {
  const marked = useRef(false);
  useEffect(() => {
    if (marked.current) return;
    marked.current = true;
    if (levelOf(progress, level.id).attempts === 0) {
      onProgress(recordAttempt(progress, level.id));
    }
  }, [level.id, progress, onProgress]);

  return (
    <article className="level">
      <LevelHeader level={level} onExit={onExit} />
      <Markdown source={level.bodyMd ?? ""} />
      <div className="level-footer">
        <button type="button" className="btn" onClick={onExit}>
          Done reading — back to the chapter
        </button>
      </div>
    </article>
  );
}

function PracticeLevel({
  level,
  progress,
  onProgress,
  onExit,
  onNeedsKey,
}: LevelRunnerProps) {
  const solvedIds = useMemo(
    () => new Set(levelOf(progress, level.id).solved),
    [progress, level.id],
  );

  // Start at the first unsolved problem so returning to a level resumes it.
  const [index, setIndex] = useState(() => {
    const next = level.problems.findIndex((p) => !solvedIds.has(p.id));
    return next === -1 ? 0 : next;
  });

  const problem = level.problems[index];

  return (
    <article className="level">
      <LevelHeader level={level} onExit={onExit} />
      <p className="level-blurb">{level.blurb}</p>
      <ProblemPips
        problems={level.problems}
        index={index}
        solvedIds={solvedIds}
        onJump={setIndex}
      />
      <ProblemCard
        key={problem.id}
        levelId={level.id}
        levelType={level.type}
        problem={problem}
        alreadySolved={solvedIds.has(problem.id)}
        progress={progress}
        onProgress={onProgress}
        onNext={() =>
          setIndex((i) => Math.min(i + 1, level.problems.length - 1))
        }
        hasNext={index < level.problems.length - 1}
        onExit={onExit}
        onNeedsKey={onNeedsKey}
      />
    </article>
  );
}

function LevelHeader({ level, onExit }: { level: Level; onExit: () => void }) {
  return (
    <header className="level-head">
      <button type="button" className="btn btn-back" onClick={onExit}>
        ← Chapter
      </button>
      <div>
        <p className="eyebrow">{levelTypeLabel(level.type)}</p>
        <h2>{level.title}</h2>
      </div>
    </header>
  );
}

export function levelTypeLabel(type: Level["type"]): string {
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

function ProblemPips({
  problems,
  index,
  solvedIds,
  onJump,
}: {
  problems: Problem[];
  index: number;
  solvedIds: Set<string>;
  onJump: (index: number) => void;
}) {
  return (
    <ol className="pips" aria-label="Problems in this level">
      {problems.map((problem, i) => {
        const state = solvedIds.has(problem.id)
          ? "done"
          : i === index
            ? "current"
            : "todo";
        return (
          <li key={problem.id}>
            <button
              type="button"
              className={`pip pip-${state}`}
              aria-label={`Problem ${i + 1}${state === "done" ? ", solved" : ""}`}
              aria-current={i === index}
              onClick={() => onJump(i)}
            >
              {i + 1}
            </button>
          </li>
        );
      })}
    </ol>
  );
}
