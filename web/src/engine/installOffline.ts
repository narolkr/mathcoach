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

  // Whether a worker was already in charge when this page loaded. A first
  // install goes from no controller to one, which is not an update and must
  // not trigger the reload below.
  const hadController = Boolean(navigator.serviceWorker.controller);
  let reloading = false;

  /*
   * Reload once when a new worker takes over.
   *
   * The worker is cache-first, which is what makes the app open instantly and
   * offline - but it also means a fresh deploy serves the *old* build on the
   * next launch, and the new one only appears the launch after. The effect is
   * "I updated the app and nothing changed", which is exactly the kind of
   * thing that wastes an evening. The worker calls skipWaiting and
   * clients.claim, so it takes control as soon as it activates; this listens
   * for that and reloads into the new build straight away.
   *
   * The `reloading` flag matters: without it, a worker that keeps claiming
   * clients can put the page in a reload loop.
   */
  navigator.serviceWorker.addEventListener("controllerchange", () => {
    if (!hadController || reloading) return;
    reloading = true;
    window.location.reload();
  });

  window.addEventListener("load", () => {
    // Relative, so the app works from a repository subpath such as
    // username.github.io/mathcoach/ as well as from a domain root.
    navigator.serviceWorker
      .register("./sw.js", { scope: "./" })
      .then((registration) => {
        // Ask whether the deployed worker has changed. Browsers do this on
        // navigation anyway, but an installed app can stay open for days.
        void registration.update();
      })
      .catch(() => {
        // Offline support is a bonus; failing to get it is not worth an error.
      });
  });
}
