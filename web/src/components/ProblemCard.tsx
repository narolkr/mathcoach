/**
 * One problem: prompt, answer entry or choices, verdict, hints, steps, journal.
 *
 * The pedagogy encoded here: you may always see a hint, you may always give up
 * and read the steps, and a wrong answer that matches a known misconception
 * tells you *which mistake you made* rather than just "incorrect".
 */

import { useCallback, useEffect, useRef, useState } from "react";
import type { Choice, Level, Problem } from "../content/schema";
import { allCorrect, gradeAll, type Verdict } from "../engine/grader";
import { formatDuration } from "../engine/format";
import {
  addJournalEntry,
  recordAttempt,
  recordSolved,
  type Progress,
} from "../engine/progress";
import { AnswerInput } from "./AnswerInput";
import { HintLadder } from "./HintLadder";
import { Prose, Tex } from "./MathText";
import { WorkingReview } from "./WorkingReview";
import { PhotoAnswer } from "./PhotoAnswer";

interface ProblemCardProps {
  levelId: string;
  /** Accepted for call-site clarity; the card renders from the problem shape. */
  levelType?: Level["type"];
  problem: Problem;
  alreadySolved: boolean;
  progress: Progress;
  onProgress: (next: Progress) => void;
  onNext: () => void;
  hasNext: boolean;
  onExit: () => void;
  /** Diagnostic mode: no hints, no steps, no journal, one shot per item. */
  quizMode?: boolean;
  onQuizAnswer?: (correct: boolean) => void;
  /** Photo review needs a key; this sends the learner to Settings. */
  onNeedsKey?: () => void;
}

export function ProblemCard({
  levelId,
  problem,
  alreadySolved,
  progress,
  onProgress,
  onNext,
  hasNext,
  onExit,
  quizMode = false,
  onQuizAnswer,
  onNeedsKey,
}: ProblemCardProps) {
  const [inputs, setInputs] = useState<string[]>(() =>
    problem.answers.map(() => ""),
  );
  const [verdicts, setVerdicts] = useState<Verdict[] | null>(null);
  const [picked, setPicked] = useState<string | null>(null);
  const [hintsRevealed, setHintsRevealed] = useState(0);
  const [showSteps, setShowSteps] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [solvedNow, setSolvedNow] = useState(false);
  const [answered, setAnswered] = useState(false);
  const startedAt = useRef(Date.now());

  useEffect(() => {
    const timer = window.setInterval(
      () => setElapsed((Date.now() - startedAt.current) / 1000),
      1000,
    );
    return () => window.clearInterval(timer);
  }, []);

  const solved = solvedNow || alreadySolved;
  const isChoice = problem.choices !== undefined && problem.choices.length > 0;

  const submit = useCallback(() => {
    if (problem.answers.length === 0 || answered) return;
    const results = gradeAll(inputs, problem.answers);
    setVerdicts(results);

    // An unreadable answer is not an attempt - it's a typo.
    if (results.some((v) => v.kind === "invalid")) return;

    setAnswered(true);
    const right = allCorrect(results);
    if (quizMode) {
      onQuizAnswer?.(right);
      if (right) setSolvedNow(true);
      return;
    }

    if (right) {
      setSolvedNow(true);
      onProgress(recordSolved(progress, levelId, problem.id));
      return;
    }
    setAnswered(false); // let them try again
    const misconception = results.find((v) => v.kind === "misconception");
    onProgress(
      recordAttempt(
        progress,
        levelId,
        misconception?.kind === "misconception"
          ? misconception.distractorId
          : undefined,
      ),
    );
  }, [
    inputs,
    problem,
    progress,
    levelId,
    onProgress,
    quizMode,
    onQuizAnswer,
    answered,
  ]);

  const pick = useCallback(
    (choiceId: string) => {
      if (picked) return;
      setPicked(choiceId);
      const right = choiceId === problem.correctChoice;
      if (quizMode) {
        onQuizAnswer?.(right);
        if (right) setSolvedNow(true);
        return;
      }
      if (right) {
        setSolvedNow(true);
        onProgress(recordSolved(progress, levelId, problem.id));
      } else {
        onProgress(recordAttempt(progress, levelId, `picked-${choiceId}`));
      }
    },
    [picked, problem.correctChoice, progress, levelId, onProgress, quizMode, onQuizAnswer],
  );

  return (
    <section className="problem">
      <div className="problem-head">
        <p className="instruction">{problem.instruction}</p>
        <span className={`tier tier-${problem.tier}`}>{problem.tier}</span>
      </div>

      <div className="prompt">
        <Tex latex={problem.promptLatex} display />
      </div>

      {problem.assumption && (
        <p className="assumption">{problem.assumption}</p>
      )}

      {isChoice ? (
        <ChoiceGrid
          choices={problem.choices ?? []}
          correct={problem.correctChoice ?? null}
          picked={picked}
          onPick={pick}
        />
      ) : (
        <>
          {!solved && onNeedsKey && (
            <PhotoAnswer
              problem={problem}
              onNeedsKey={onNeedsKey}
              onTranscribed={(answer) =>
                // Fills the first slot only. Multi-slot problems ask for
                // separate named values, and guessing which line of the page
                // maps to which box would be worse than letting you type them.
                setInputs((previous) =>
                  previous.map((value, index) => (index === 0 ? answer : value)),
                )
              }
            />
          )}

          <div className="answers">
            {problem.answers.map((answer, i) => (
              <AnswerInput
                key={answer.label}
                label={answer.label}
                hintText={answer.hintText}
                variables={problem.variables}
                value={inputs[i]}
                autoFocus={i === 0}
                disabled={solved}
                onChange={(value) =>
                  setInputs((previous) =>
                    previous.map((v, j) => (j === i ? value : v)),
                  )
                }
                onSubmit={submit}
              />
            ))}
          </div>

          {!solved && (
            <button type="button" className="btn btn-primary" onClick={submit}>
              Check
            </button>
          )}

          {verdicts && !solved && (
            <VerdictList verdicts={verdicts} answers={problem.answers} />
          )}
        </>
      )}

      {solved && (
        <SolvedPanel
          problem={problem}
          seconds={elapsed}
          hintsUsed={hintsRevealed}
          justSolved={solvedNow}
          progress={progress}
          onProgress={onProgress}
          onNext={onNext}
          hasNext={hasNext}
          onExit={onExit}
          quizMode={quizMode}
          onNeedsKey={onNeedsKey}
        />
      )}

      {!solved && !quizMode && (
        <>
          <HintLadder
            hints={problem.hints}
            revealed={hintsRevealed}
            elapsedSeconds={elapsed}
            onReveal={() => setHintsRevealed((n) => n + 1)}
          />

          {problem.steps.length > 0 && (
            <div className="steps-toggle">
              {showSteps ? (
                <Steps problem={problem} />
              ) : (
                <button
                  type="button"
                  className="btn btn-quiet"
                  onClick={() => setShowSteps(true)}
                >
                  Give up and show the worked steps
                </button>
              )}
            </div>
          )}

          <p className="timer">On this problem {formatDuration(elapsed)}</p>
        </>
      )}

      {quizMode && (picked !== null || answered) && (
        <div className="level-footer">
          <button type="button" className="btn btn-primary" onClick={onNext}>
            {hasNext ? "Next question →" : "See results"}
          </button>
        </div>
      )}
    </section>
  );
}

function ChoiceGrid({
  choices,
  correct,
  picked,
  onPick,
}: {
  choices: Choice[];
  correct: string | null;
  picked: string | null;
  onPick: (id: string) => void;
}) {
  const pickedChoice = choices.find((c) => c.id === picked);
  const correctChoice = choices.find((c) => c.id === correct);
  const wasRight = picked !== null && picked === correct;

  return (
    <>
      <div className="choices">
        {choices.map((choice) => {
          const isPicked = picked === choice.id;
          const isCorrect = correct === choice.id;
          const state = !picked
            ? ""
            : isCorrect
              ? " choice-correct"
              : isPicked
                ? " choice-wrong"
                : "";
          return (
            <button
              key={choice.id}
              type="button"
              className={`choice${state}`}
              disabled={picked !== null}
              onClick={() => onPick(choice.id)}
            >
              {choice.isLatex ? <Tex latex={choice.label} /> : choice.label}
            </button>
          );
        })}
      </div>

      {picked && (
        <div
          className={
            wasRight ? "feedback feedback-good" : "feedback feedback-bad"
          }
        >
          {wasRight ? (
            <p>
              <strong>Yes.</strong>{" "}
              <Prose text={pickedChoice?.feedback ?? ""} />
            </p>
          ) : (
            <>
              <p>
                <strong>Not this time.</strong>{" "}
                <Prose text={pickedChoice?.feedback ?? ""} />
              </p>
              {correctChoice && (
                <p>
                  <Prose text={correctChoice.feedback} />
                </p>
              )}
            </>
          )}
        </div>
      )}
    </>
  );
}

function VerdictList({
  verdicts,
  answers,
}: {
  verdicts: Verdict[];
  answers: Problem["answers"];
}) {
  return (
    <div className="verdicts">
      {verdicts.map((verdict, i) => {
        const label = answers[i]?.label ?? "";
        switch (verdict.kind) {
          case "correct":
            return (
              <p key={i} className="feedback feedback-good">
                <strong>{label}</strong> is right.
              </p>
            );
          case "misconception":
            return (
              <p key={i} className="feedback feedback-bad">
                <strong>Not quite{label ? ` for ${label}` : ""}.</strong>{" "}
                <Prose text={verdict.feedback} />
              </p>
            );
          case "wrong":
            return (
              <p key={i} className="feedback feedback-bad">
                <strong>Not right{label ? ` for ${label}` : ""}.</strong> Check
                each part separately — one of them is off.
              </p>
            );
          case "invalid":
            return (
              <p key={i} className="feedback feedback-warn">
                {verdict.message}
              </p>
            );
        }
      })}
    </div>
  );
}

function Steps({ problem }: { problem: Problem }) {
  return (
    <ol className="steps">
      {problem.steps.map((step, i) => (
        <li key={i}>
          <Tex latex={step.latex} display />
          <Prose className="step-note" text={step.note} />
        </li>
      ))}
    </ol>
  );
}

function SolvedPanel({
  problem,
  seconds,
  hintsUsed,
  justSolved,
  progress,
  onProgress,
  onNext,
  hasNext,
  onExit,
  quizMode,
  onNeedsKey,
}: {
  problem: Problem;
  seconds: number;
  hintsUsed: number;
  justSolved: boolean;
  progress: Progress;
  onProgress: (next: Progress) => void;
  onNext: () => void;
  hasNext: boolean;
  onExit: () => void;
  quizMode: boolean;
  onNeedsKey?: () => void;
}) {
  const [insight, setInsight] = useState("");
  const [logged, setLogged] = useState(false);

  const logIt = () => {
    onProgress(
      addJournalEntry(progress, {
        at: new Date().toISOString(),
        problemId: problem.id,
        promptLatex: problem.promptLatex,
        solved: true,
        seconds: Math.round(seconds),
        hintsUsed,
        insight: insight.trim(),
      }),
    );
    setLogged(true);
  };

  if (quizMode) {
    return (
      <p className="feedback feedback-good">
        <strong>Correct.</strong>
      </p>
    );
  }

  return (
    <div className="solved">
      <p className="feedback feedback-good">
        <strong>{justSolved ? "Correct." : "Already solved."}</strong>{" "}
        {justSolved &&
          `${formatDuration(seconds)}, ${hintsUsed} hint${hintsUsed === 1 ? "" : "s"}.`}
      </p>

      {problem.answers.length > 0 && (
        <div className="canonical">
          {problem.answers.map((answer) => (
            <p key={answer.label}>
              <span className="muted">{answer.label} = </span>
              <Tex latex={answer.latex} />
            </p>
          ))}
        </div>
      )}

      {problem.steps.length > 0 && <Steps problem={problem} />}

      {justSolved && !logged && (
        <div className="journal-prompt">
          <label htmlFor="insight">
            What did you learn? One line. Skip it if there was nothing new —
            but if something clicked, this is the field that matters.
          </label>
          <textarea
            id="insight"
            rows={2}
            value={insight}
            placeholder="e.g. the root applies to the coefficient too"
            onChange={(event) => setInsight(event.target.value)}
          />
          <button type="button" className="btn btn-quiet" onClick={logIt}>
            {insight.trim() ? "Save to journal" : "Skip"}
          </button>
        </div>
      )}

      {logged && <p className="muted">Logged.</p>}

      {/* After the answer, never before: this reviews the route you took, and
          a camera button next to an unsolved problem is a hint you can reach
          for at thirty seconds. */}
      {problem.answers.length > 0 && onNeedsKey && (
        <WorkingReview
          problem={problem}
          answer={problem.answers[0]}
          onNeedsKey={onNeedsKey}
        />
      )}

      <div className="level-footer">
        {hasNext ? (
          <button type="button" className="btn btn-primary" onClick={onNext}>
            Next problem →
          </button>
        ) : (
          <button type="button" className="btn btn-primary" onClick={onExit}>
            Finish level
          </button>
        )}
      </div>
    </div>
  );
}
