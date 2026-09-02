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
 * Confirmed available on the free tier at the time of writing. Newer models
 * exist (the 3.x series); `listVisionModels()` asks the key what it can
 * actually use rather than trusting this list to stay current.
 */
export const DEFAULT_MODEL = "gemini-2.5-flash";

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
