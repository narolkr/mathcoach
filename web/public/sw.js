/*
 * Service worker: makes the installed app work with no network.
 *
 * Strategy is cache-first for everything, with a network fallback that fills
 * the cache as it goes. Chosen over a precache manifest of hashed filenames
 * because it needs no build-time coordination: whatever the app requests on
 * first load gets kept, and a hashed asset name changing just means the next
 * visit caches the new one.
 *
 * The content bundle is the important part. It is over a megabyte, and without
 * it cached the app opens to "Content didn't load" on a train.
 */

const CACHE = "mathcoach-v1";

// The shell, fetched eagerly at install so the very first offline launch works
// even if the learner never navigated anywhere.
const SHELL = ["./", "./index.html", "./manifest.webmanifest", "./content/bundle.json"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      const urls = [...SHELL, ...(await hashedAssets())];
      // Individually, not addAll: addAll rejects the whole install if any one
      // request fails, and a single 404 should not leave the app uninstalled.
      await Promise.allSettled(urls.map((url) => cache.add(url)));
      await self.skipWaiting();
    })(),
  );
});

/**
 * The built script and stylesheet, read out of index.html.
 *
 * These have content-hashed filenames, so they cannot be listed in SHELL. They
 * also cannot be left to the fetch handler: a worker does not intercept the
 * requests made by the very page load that registered it, so on a first visit
 * the app's own code would go uncached and the first offline launch would fail.
 * Parsing index.html keeps this self-maintaining across rebuilds - no asset
 * manifest to generate and keep in step.
 *
 * The stylesheet is then parsed in turn for KaTeX's font files. Those matter
 * more than they look: they are referenced from the CSS rather than the HTML,
 * so they were missed at first - and without them offline maths renders in a
 * fallback serif, which is subtly and silently wrong rather than obviously
 * broken. Only woff2 is taken; the woff and truetype fallbacks would triple
 * the payload for browsers that no longer exist.
 */
async function hashedAssets() {
  try {
    const response = await fetch("./index.html", { cache: "reload" });
    if (!response.ok) return [];
    const html = await response.text();

    const urls = new Set();
    const stylesheets = [];
    for (const match of html.matchAll(/(?:src|href)="([^"]+\.(?:js|css))"/g)) {
      const url = new URL(match[1], self.location.href).href;
      urls.add(url);
      if (url.endsWith(".css")) stylesheets.push(url);
    }

    for (const sheet of stylesheets) {
      for (const font of await fontsIn(sheet)) urls.add(font);
    }

    return [...urls];
  } catch {
    // Offline at install time. The fetch handler will pick them up later.
    return [];
  }
}

async function fontsIn(stylesheetUrl) {
  try {
    const response = await fetch(stylesheetUrl, { cache: "reload" });
    if (!response.ok) return [];
    const css = await response.text();
    const fonts = new Set();
    for (const match of css.matchAll(/url\(\s*["']?([^"')]+\.woff2)["']?\s*\)/g)) {
      fonts.add(new URL(match[1], stylesheetUrl).href);
    }
    return [...fonts];
  } catch {
    return [];
  }
}

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const names = await caches.keys();
      await Promise.all(
        names.filter((name) => name !== CACHE).map((name) => caches.delete(name)),
      );
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;

  // Only same-origin GETs. The Gemini call must always hit the network, and
  // caching a POST is meaningless anyway.
  if (request.method !== "GET") return;
  if (new URL(request.url).origin !== self.location.origin) return;

  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE);
      const hit = await cache.match(request, { ignoreSearch: true });
      if (hit) {
        // Refresh in the background so a redeploy is picked up next launch,
        // without making this load wait for the network.
        void refresh(cache, request);
        return hit;
      }

      try {
        const response = await fetch(request);
        if (response.ok) void cache.put(request, response.clone());
        return response;
      } catch {
        // Offline and not cached. For a navigation, the shell is a better
        // answer than a browser error page.
        if (request.mode === "navigate") {
          const shell = await cache.match("./index.html");
          if (shell) return shell;
        }
        throw new Error("offline and not cached");
      }
    })(),
  );
});

async function refresh(cache, request) {
  try {
    const response = await fetch(request);
    if (response.ok) await cache.put(request, response.clone());
  } catch {
    // Offline; the cached copy stands.
  }
}
