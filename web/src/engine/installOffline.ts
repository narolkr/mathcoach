/**
 * Register the service worker, so the installed app works with no network.
 *
 * Guarded on three things, each for a reason:
 *
 * - **A secure origin.** Service workers require https or localhost. On a
 *   `file://` page registration throws, and the offline single-file build needs
 *   no worker anyway - everything is already inlined in the one file.
 * - **Production only.** In dev, a cache-first worker serves stale modules and
 *   makes edits appear not to apply, which is a miserable afternoon.
 * - **Support.** Older iOS versions lack it; the app still works, just online.
 */
export function installOffline(): void {
  if (!("serviceWorker" in navigator)) return;
  if (import.meta.env.DEV) return;
  if (window.location.protocol === "file:") return;
  // `isSecureContext` covers https and localhost without hard-coding either.
  if (!window.isSecureContext) return;

  window.addEventListener("load", () => {
    // Relative, so the app works from a repository subpath such as
    // username.github.io/mathcoach/ as well as from a domain root.
    navigator.serviceWorker.register("./sw.js", { scope: "./" }).catch(() => {
      // Offline support is a bonus; failing to get it is not worth an error.
    });
  });
}
