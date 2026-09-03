/**
 * The Gemini API key and model choice.
 *
 * The key is typed in here and kept in this browser's localStorage. It is
 * never compiled into the build: baking it into `mathcoach.html` would mean
 * anyone you sent that file to had your key, and that file is meant to be
 * copied around freely.
 */

import { useState } from "react";
import {
  clearSettings,
  loadSettings,
  maskKey,
  saveSettings,
  DEFAULT_MODEL,
  type Settings as StoredSettings,
} from "../engine/settings";
import { listVisionModels, testVision } from "../engine/vision";

export function Settings({ onChanged }: { onChanged?: () => void }) {
  const [settings, setSettings] = useState<StoredSettings>(() => loadSettings());
  const [draftKey, setDraftKey] = useState("");
  const [models, setModels] = useState<string[] | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  const [checking, setChecking] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    ok: boolean;
    message: string;
  } | null>(null);

  const persist = (next: StoredSettings) => {
    setSettings(next);
    const ok = saveSettings(next);
    setFailed(!ok);
    setMessage(
      ok ? "Saved on this device." : "This browser refused to store the key.",
    );
    onChanged?.();
  };

  const checkModels = async () => {
    setChecking(true);
    setMessage(null);
    try {
      const available = await listVisionModels(settings.apiKey);
      setModels(available);
      setFailed(false);
      setMessage(
        available.length
          ? `Your key can use ${available.length} models.`
          : "That key returned no usable models.",
      );
    } catch (cause) {
      setFailed(true);
      setMessage(cause instanceof Error ? cause.message : "Couldn't reach Gemini.");
    } finally {
      setChecking(false);
    }
  };

  const runTest = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      setTestResult(await testVision(settings.apiKey, settings.model));
    } catch (cause) {
      setTestResult({
        ok: false,
        message: cause instanceof Error ? cause.message : "Unknown failure.",
      });
    } finally {
      setTesting(false);
    }
  };

  /* The stored model may not appear in the fetched list - a model can be
     retired, or the list can be narrower than what was saved earlier. A
     <select> whose value matches no option displays its FIRST option instead,
     so the dropdown would show one model while every request used another.
     Keeping the stored value as an explicit option makes the mismatch visible
     rather than silent. */
  const options =
    models && !models.includes(settings.model)
      ? [settings.model, ...models]
      : models;

  return (
    <section className="panel settings">
      <div>
        <p className="eyebrow">Photo review</p>
        <p className="muted">
          Optional. Add a free Gemini API key to photograph your handwritten
          working and have the <em>method</em> reviewed. Your answers are always
          graded exactly, offline, without this — the key only adds commentary
          on your working.
        </p>
      </div>

      {settings.apiKey ? (
        <div className="settings-row">
          <p>
            Key stored: <code>{maskKey(settings.apiKey)}</code>
          </p>
          <button
            type="button"
            className="btn btn-quiet"
            onClick={() => {
              clearSettings();
              setSettings({ apiKey: "", model: DEFAULT_MODEL });
              setModels(null);
              setMessage("Key removed from this device.");
              setFailed(false);
              onChanged?.();
            }}
          >
            Remove key
          </button>
        </div>
      ) : (
        <div className="settings-row">
          <label className="answer-label" htmlFor="gemini-key">
            API key
          </label>
          <input
            id="gemini-key"
            className="answer-input"
            type="password"
            value={draftKey}
            spellCheck={false}
            autoComplete="off"
            placeholder="Paste a key from aistudio.google.com/apikey"
            onChange={(event) => setDraftKey(event.target.value)}
          />
          <button
            type="button"
            className="btn btn-primary"
            disabled={!draftKey.trim()}
            onClick={() => {
              persist({ ...settings, apiKey: draftKey.trim() });
              setDraftKey("");
            }}
          >
            Save key
          </button>
          <p className="muted">
            Get one free at{" "}
            <a
              href="https://aistudio.google.com/apikey"
              target="_blank"
              rel="noreferrer"
            >
              aistudio.google.com/apikey
            </a>
            . No card required. Note that Google may use free-tier requests to
            improve its models — fine for calculus working, worth knowing.
          </p>
        </div>
      )}

      {settings.apiKey && (
        <div className="settings-row">
          <label className="answer-label" htmlFor="gemini-model">
            Model
          </label>
          {models ? (
            <select
              id="gemini-model"
              className="answer-input"
              value={settings.model}
              onChange={(event) =>
                persist({ ...settings, model: event.target.value })
              }
            >
              {options?.map((name) => (
                <option key={name} value={name}>
                  {name}
                  {models.includes(name) ? "" : " — not in your key's list"}
                </option>
              ))}
            </select>
          ) : (
            <input
              id="gemini-model"
              className="answer-input"
              type="text"
              value={settings.model}
              spellCheck={false}
              onChange={(event) =>
                setSettings({ ...settings, model: event.target.value })
              }
              onBlur={() => persist(settings)}
            />
          )}
          <div className="settings-buttons">
            <button
              type="button"
              className="btn"
              disabled={checking}
              onClick={() => void checkModels()}
            >
              {checking ? "Checking…" : "Check which models my key can use"}
            </button>
            <button
              type="button"
              className="btn"
              disabled={testing}
              onClick={() => void runTest()}
            >
              {testing ? "Sending…" : "Send a test image"}
            </button>
          </div>
          <p className="muted">
            Google adds and retires models faster than this app gets rebuilt, so
            it asks your key rather than trusting a hard-coded list.
          </p>
          <p className="muted">
            <strong>If photos are slow or come back empty, pick{" "}
            <code>gemini-2.5-flash-lite</code>.</strong> It is the right choice
            for reading handwriting: thinking is off by default (
            <code>gemini-2.5-flash</code> has it on, and reasoning about
            handwriting is wasted time), and the free tier allows roughly four
            times as many requests per day. Its transcription mistakes cost you
            little, because you confirm what it read before anything is graded
            and the grader is never the model. <em>Send a test image</em> reports
            how long a round trip actually takes, so you can compare.
          </p>
          <p className="muted">
            <strong>If a photo fails but the model is listed</strong>, use{" "}
            <em>Send a test image</em>. Listing models proves less than it
            looks: that call takes no image and is not restricted by region, so
            it can offer a model that refuses to actually run. The test sends
            one small generated image down the same path a photo takes and
            reports exactly what Google says.
          </p>
          {testResult && (
            <p
              className={
                testResult.ok ? "feedback feedback-good" : "feedback feedback-bad"
              }
            >
              {testResult.message}
            </p>
          )}
        </div>
      )}

      {message && (
        <p className={failed ? "feedback feedback-bad" : "muted"}>{message}</p>
      )}
    </section>
  );
}
