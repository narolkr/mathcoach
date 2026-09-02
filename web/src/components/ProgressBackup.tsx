/**
 * Export and restore progress as a file.
 *
 * This is the safety net for the offline build. Progress lives in
 * `localStorage`, which on a `file://` page is keyed to an origin the browser
 * may treat as opaque - and a phone's browser storage gets cleared by
 * "clear browsing data", by storage pressure, or by opening the file from a
 * slightly different path. Six months of work is too much to leave to that.
 *
 * The download uses a data: URL rather than a blob: URL, because blob URLs are
 * unreliable on file:// origins in some mobile browsers.
 */

import { useRef, useState } from "react";
import {
  exportProgress,
  importProgress,
  save,
  type Progress,
} from "../engine/progress";

interface ProgressBackupProps {
  progress: Progress;
  onRestore: (progress: Progress) => void;
}

export function ProgressBackup({ progress, onRestore }: ProgressBackupProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  const solvedCount = Object.values(progress.levels).reduce(
    (total, level) => total + level.solved.length,
    0,
  );

  const download = () => {
    const json = exportProgress(progress);
    const stamp = new Date().toISOString().slice(0, 10);
    const link = document.createElement("a");
    link.href = `data:application/json;charset=utf-8,${encodeURIComponent(json)}`;
    link.download = `mathcoach-progress-${stamp}.json`;
    document.body.append(link);
    link.click();
    link.remove();
    setFailed(false);
    setMessage(
      `Saved ${solvedCount} solved problem${solvedCount === 1 ? "" : "s"} and ` +
        `${progress.journal.length} journal entr${progress.journal.length === 1 ? "y" : "ies"}.`,
    );
  };

  const restore = async (file: File) => {
    try {
      const restored = importProgress(await file.text());
      onRestore(restored);
      save(restored);
      const count = Object.values(restored.levels).reduce(
        (total, level) => total + level.solved.length,
        0,
      );
      setFailed(false);
      setMessage(`Restored ${count} solved problems.`);
    } catch (cause) {
      setFailed(true);
      setMessage(
        cause instanceof Error ? cause.message : "Couldn't read that file.",
      );
    }
  };

  return (
    <section className="panel backup">
      <div>
        <p className="eyebrow">Backup</p>
        <p className="muted">
          Progress is stored by the browser, and browsers lose it — cleared
          data, storage pressure, or opening the file from a different folder.
          Export occasionally and you can always get back.
        </p>
      </div>

      <div className="backup-actions">
        <button type="button" className="btn" onClick={download}>
          Export progress
        </button>
        <button
          type="button"
          className="btn"
          onClick={() => fileRef.current?.click()}
        >
          Restore from file
        </button>
        <input
          ref={fileRef}
          type="file"
          accept="application/json,.json"
          hidden
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void restore(file);
            // Clear it so re-picking the same file fires change again.
            event.target.value = "";
          }}
        />
      </div>

      {message && (
        <p className={failed ? "feedback feedback-bad" : "muted"}>{message}</p>
      )}
    </section>
  );
}
