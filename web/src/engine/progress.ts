/**
 * Progress, kept in localStorage.
 *
 * Deliberately records *insight*, not score: the journal is the primary
 * artefact and the counters exist to unlock levels. There are no streaks - this
 * runs alongside a full-time job and streak pressure would make it a chore.
 */

const KEY = "mathcoach.progress.v1";

export interface JournalEntry {
  /** ISO timestamp. */
  at: string;
  problemId: string;
  promptLatex: string;
  solved: boolean;
  /** Seconds spent on the problem. */
  seconds: number;
  hintsUsed: number;
  /** The learner's own words. The whole point of the journal. */
  insight: string;
}

export interface LevelProgress {
  /** Problem ids answered correctly, ever. */
  solved: string[];
  attempts: number;
  /** Misconception ids the learner has hit, with counts. Feeds future drills. */
  misconceptions: Record<string, number>;
}

export interface DiagnosticResult {
  /** ISO timestamp of when it was taken. */
  at: string;
  /** Chapter id -> whether every item for it was answered correctly. */
  passedByChapter: Record<string, boolean>;
  /** Item problem id -> correct. Kept so the readout can say what was missed. */
  itemsCorrect: Record<string, boolean>;
}

export interface Progress {
  levels: Record<string, LevelProgress>;
  journal: JournalEntry[];
  /** Null until the diagnostic has been taken. */
  diagnostic: DiagnosticResult | null;
  /**
   * Chapters the learner has chosen to collapse as already-known. Seeded by the
   * diagnostic, but editable: passing the quiz is a suggestion, not a verdict,
   * and a chapter can always be reopened.
   */
  knownChapters: string[];
}

const EMPTY: Progress = {
  levels: {},
  journal: [],
  diagnostic: null,
  knownChapters: [],
};

export function load(): Progress {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return structuredClone(EMPTY);
    const parsed = JSON.parse(raw) as Partial<Progress>;
    return {
      levels: parsed.levels ?? {},
      journal: parsed.journal ?? [],
      diagnostic: parsed.diagnostic ?? null,
      knownChapters: parsed.knownChapters ?? [],
    };
  } catch {
    // Private browsing, blocked storage, corrupt JSON - all mean "start fresh"
    // rather than "crash".
    return structuredClone(EMPTY);
  }
}

/**
 * Whether this browser will actually keep what we write.
 *
 * Worth probing rather than assuming, because the offline single-file build
 * runs from `file://`, where storage behaviour varies: most browsers allow it,
 * some treat every local file as its own opaque origin, and a few refuse
 * outright. Silently losing months of progress is the worst failure this app
 * has available to it, so the UI says so when this returns false.
 *
 * Probes by round-tripping a value: merely reading `localStorage` succeeds in
 * cases where writing later throws.
 */
export function storageWorks(): boolean {
  try {
    const probe = `${KEY}.probe`;
    localStorage.setItem(probe, "1");
    const echoed = localStorage.getItem(probe);
    localStorage.removeItem(probe);
    return echoed === "1";
  } catch {
    return false;
  }
}

/** Returns false when the write failed, so callers can warn rather than guess. */
export function save(progress: Progress): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify(progress));
    return true;
  } catch {
    // Quota exceeded, or storage disabled for this origin. The session keeps
    // working in memory; it just will not survive a reload.
    return false;
  }
}

/** The whole of progress as JSON, for the export button. */
export function exportProgress(progress: Progress): string {
  return JSON.stringify(
    { format: "mathcoach-progress", version: 1, savedAt: new Date().toISOString(), progress },
    null,
    2,
  );
}

/**
 * Parse an exported file back into progress.
 *
 * Throws with a readable message rather than returning a half-populated
 * object: restoring a backup is exactly when silent partial failure would be
 * most damaging.
 */
export function importProgress(text: string): Progress {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error("That file isn't valid JSON.");
  }

  const outer = parsed as { format?: string; progress?: Partial<Progress> };
  if (outer?.format !== "mathcoach-progress" || !outer.progress) {
    throw new Error(
      "That doesn't look like a MathCoach progress export - the file should " +
        'start with {"format": "mathcoach-progress"}.',
    );
  }

  const incoming = outer.progress;
  return {
    levels: incoming.levels ?? {},
    journal: incoming.journal ?? [],
    diagnostic: incoming.diagnostic ?? null,
    knownChapters: incoming.knownChapters ?? [],
  };
}

export function levelOf(progress: Progress, levelId: string): LevelProgress {
  return (
    progress.levels[levelId] ?? { solved: [], attempts: 0, misconceptions: {} }
  );
}

export function recordSolved(
  progress: Progress,
  levelId: string,
  problemId: string,
): Progress {
  const level = levelOf(progress, levelId);
  if (level.solved.includes(problemId)) return progress;
  return {
    ...progress,
    levels: {
      ...progress.levels,
      [levelId]: {
        ...level,
        solved: [...level.solved, problemId],
        attempts: level.attempts + 1,
      },
    },
  };
}

export function recordAttempt(
  progress: Progress,
  levelId: string,
  misconceptionId?: string,
): Progress {
  const level = levelOf(progress, levelId);
  const misconceptions = { ...level.misconceptions };
  if (misconceptionId) {
    misconceptions[misconceptionId] = (misconceptions[misconceptionId] ?? 0) + 1;
  }
  return {
    ...progress,
    levels: {
      ...progress.levels,
      [levelId]: { ...level, attempts: level.attempts + 1, misconceptions },
    },
  };
}

export function addJournalEntry(
  progress: Progress,
  entry: JournalEntry,
): Progress {
  return { ...progress, journal: [entry, ...progress.journal] };
}

/**
 * A level counts as complete at 80% solved. Not 100%: demanding every last
 * problem turns a practice set into a completionist grind, and the roadmap's
 * gate is the real measure of mastery anyway.
 */
export const COMPLETION_THRESHOLD = 0.8;

export function isLevelComplete(
  progress: Progress,
  levelId: string,
  problemCount: number,
): boolean {
  if (problemCount === 0) {
    // Concept levels: opening one is completing it.
    return levelOf(progress, levelId).attempts > 0;
  }
  return (
    levelOf(progress, levelId).solved.length >=
    Math.ceil(problemCount * COMPLETION_THRESHOLD)
  );
}

export function markConceptRead(progress: Progress, levelId: string): Progress {
  const level = levelOf(progress, levelId);
  if (level.attempts > 0) return progress;
  return {
    ...progress,
    levels: { ...progress.levels, [levelId]: { ...level, attempts: 1 } },
  };
}

/**
 * Record a completed diagnostic and seed the known-chapter list from it.
 *
 * Only chapters marked `skippable` in the bundle can be collapsed, which is how
 * chapter 4 stays put: its log-likelihood half appears in no school syllabus,
 * so school fluency is no evidence of knowing it.
 */
export function recordDiagnostic(
  progress: Progress,
  result: DiagnosticResult,
  skippableChapterIds: Set<string>,
): Progress {
  const known = Object.entries(result.passedByChapter)
    .filter(([chapterId, passed]) => passed && skippableChapterIds.has(chapterId))
    .map(([chapterId]) => chapterId);

  return { ...progress, diagnostic: result, knownChapters: known };
}

export function isChapterKnown(progress: Progress, chapterId: string): boolean {
  return progress.knownChapters.includes(chapterId);
}

/** Reopening a chapter the diagnostic collapsed, or collapsing one by hand. */
export function setChapterKnown(
  progress: Progress,
  chapterId: string,
  known: boolean,
): Progress {
  const current = new Set(progress.knownChapters);
  if (known) current.add(chapterId);
  else current.delete(chapterId);
  return { ...progress, knownChapters: [...current] };
}

/** Misconceptions ranked by how often they've bitten, most frequent first. */
export function topMisconceptions(
  progress: Progress,
): Array<{ id: string; count: number }> {
  const totals: Record<string, number> = {};
  for (const level of Object.values(progress.levels)) {
    for (const [id, count] of Object.entries(level.misconceptions)) {
      totals[id] = (totals[id] ?? 0) + count;
    }
  }
  return Object.entries(totals)
    .map(([id, count]) => ({ id, count }))
    .sort((a, b) => b.count - a.count);
}

export function reset(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // Same as save(): nothing useful to do.
  }
}
