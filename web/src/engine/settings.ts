/**
 * Settings that are this-device-only: the Gemini API key and model choice.
 *
 * Kept in localStorage under its own key, deliberately separate from progress:
 * exporting progress must never carry a credential into a file you might share.
 *
 * The key is entered in the app and never compiled into the build. Baking it
 * into `mathcoach.html` would mean anyone you sent that file to had your key.
 */

const KEY = "mathcoach.settings.v1";

/**
 * Flash-Lite rather than Flash, for three reasons that all point the same way
 * on this workload:
 *
 * - **Thinking is off by default on Lite and on for Flash.** Reading
 *   handwriting is recognition, not reasoning, so thinking is latency with no
 *   benefit - and on a 2.5 model it can consume the output budget and return
 *   nothing at all.
 * - **Four times the daily free quota** at the time of writing: 15 requests a
 *   minute and 1000 a day, against 10 and 250 for Flash.
 * - **Accuracy matters less here than it looks.** A misread is shown for
 *   confirmation before anything is graded, and correctness is settled by the
 *   fingerprint grader, never by the model. So the cheap model's mistakes are
 *   visible and fixable rather than silently wrong.
 *
 * Newer models exist; `listVisionModels()` asks the key what it can actually
 * use rather than trusting this to stay current.
 */
export const DEFAULT_MODEL = "gemini-2.5-flash-lite";

export interface Settings {
  /** Empty until the learner pastes one in. */
  apiKey: string;
  model: string;
}

const EMPTY: Settings = { apiKey: "", model: DEFAULT_MODEL };

export function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { ...EMPTY };
    const parsed = JSON.parse(raw) as Partial<Settings>;
    return {
      apiKey: parsed.apiKey ?? "",
      model: parsed.model || DEFAULT_MODEL,
    };
  } catch {
    return { ...EMPTY };
  }
}

export function saveSettings(settings: Settings): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify(settings));
    return true;
  } catch {
    return false;
  }
}

export function clearSettings(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // Nothing useful to do.
  }
}

/** Enough of the key to recognise it, without printing the whole thing. */
export function maskKey(apiKey: string): string {
  if (apiKey.length <= 8) return "•".repeat(apiKey.length);
  return `${apiKey.slice(0, 4)}…${apiKey.slice(-4)}`;
}
