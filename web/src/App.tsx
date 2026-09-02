import { useCallback, useEffect, useState } from "react";
import type { Bundle, Chapter, Level } from "./content/schema";
import { loadBundle } from "./engine/loadBundle";
import { load, save, storageWorks, type Progress } from "./engine/progress";
import { Campaign } from "./components/Campaign";
import { ChapterView } from "./components/ChapterView";
import { DiagnosticRunner } from "./components/DiagnosticRunner";
import { Journal } from "./components/Journal";
import { ProgressBackup } from "./components/ProgressBackup";
import { Settings } from "./components/Settings";
import { LevelRunner } from "./components/LevelRunner";

type View =
  | { name: "campaign" }
  | { name: "chapter"; chapter: Chapter }
  | { name: "level"; chapter: Chapter; level: Level }
  | { name: "diagnostic" }
  | { name: "journal" };

export function App() {
  const [bundle, setBundle] = useState<Bundle | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState<Progress>(() => load());
  const [view, setView] = useState<View>({ name: "campaign" });
  // Probed once at startup rather than on every save, so the warning is
  // steady rather than flickering.
  const [canPersist] = useState(() => storageWorks());

  useEffect(() => {
    loadBundle()
      .then(setBundle)
      .catch((cause: unknown) => {
        setError(
          cause instanceof Error ? cause.message : "could not load content",
        );
      });
  }, []);

  const updateProgress = useCallback((next: Progress) => {
    setProgress(next);
    save(next);
  }, []);

  const storageWarning = !canPersist && (
    <div className="storage-warning">
      <strong>This browser isn't saving your progress.</strong> You can still
      work through levels, but nothing will survive a reload. Export from the
      Journal tab to keep a copy, or open the app over http(s) rather than as a
      local file.
    </div>
  );

  if (error) {
    return (
      <main className="shell">
        <div className="fatal">
          <h1>Content didn't load</h1>
          <p>{error}</p>
          <p className="muted">
            Run <code>python tools/build.py</code> from the repository root, then
            reload.
          </p>
        </div>
      </main>
    );
  }

  if (!bundle) {
    return (
      <main className="shell">
        <p className="muted">Loading…</p>
      </main>
    );
  }

  return (
    <main className="shell">
      <nav className="topbar">
        <button
          type="button"
          className="brand"
          onClick={() => setView({ name: "campaign" })}
        >
          MathCoach
        </button>
        <div className="topbar-actions">
          <button
            type="button"
            className="btn btn-quiet"
            onClick={() =>
              setView((current) =>
                current.name === "journal"
                  ? { name: "campaign" }
                  : { name: "journal" },
              )
            }
          >
            {view.name === "journal" ? "Campaign" : "Journal"}
          </button>
        </div>
      </nav>

      {storageWarning}

      {view.name === "campaign" && (
        <Campaign
          bundle={bundle}
          progress={progress}
          onProgress={updateProgress}
          onOpenChapter={(chapter) => setView({ name: "chapter", chapter })}
          onStartDiagnostic={() => setView({ name: "diagnostic" })}
        />
      )}

      {view.name === "chapter" && (
        <ChapterView
          chapter={view.chapter}
          progress={progress}
          onOpenLevel={(level) =>
            setView({ name: "level", chapter: view.chapter, level })
          }
          onExit={() => setView({ name: "campaign" })}
        />
      )}

      {view.name === "level" && (
        <LevelRunner
          key={view.level.id}
          level={view.level}
          progress={progress}
          onProgress={updateProgress}
          onExit={() => setView({ name: "chapter", chapter: view.chapter })}
          onNeedsKey={() => setView({ name: "journal" })}
        />
      )}

      {view.name === "diagnostic" && bundle.diagnostic && (
        <DiagnosticRunner
          diagnostic={bundle.diagnostic}
          bundle={bundle}
          progress={progress}
          onProgress={updateProgress}
          onExit={() => setView({ name: "campaign" })}
        />
      )}

      {view.name === "journal" && (
        <>
          <Journal
            progress={progress}
            onExit={() => setView({ name: "campaign" })}
          />
          <ProgressBackup progress={progress} onRestore={updateProgress} />
          <Settings />
        </>
      )}
    </main>
  );
}
