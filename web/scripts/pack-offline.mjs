/**
 * Pack the app into one self-contained HTML file that runs from file://.
 *
 *   node scripts/pack-offline.mjs
 *
 * Why this exists: a `file://` page can make no subresource requests that
 * matter. Module scripts are blocked by CORS, `fetch()` of a sibling file is
 * blocked, and font files 404 - which for a maths app means KaTeX silently
 * falls back to system glyphs and every formula renders wrong. So everything
 * has to be in the one file: script, styles, fonts, and the content bundle.
 *
 * Reads the IIFE build in dist-offline-raw/ and writes dist-offline/.
 */

import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync } from "node:fs";
import { join, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";

const WEB = dirname(dirname(fileURLToPath(import.meta.url)));
const RAW = join(WEB, "dist-offline-raw");
const OUT_DIR = join(WEB, "dist-offline");
const OUT = join(OUT_DIR, "mathcoach.html");
const BUNDLE = join(WEB, "public", "content", "bundle.json");

function fail(message) {
  console.error(`pack-offline: ${message}`);
  process.exit(1);
}

if (!existsSync(RAW)) {
  fail("no dist-offline-raw/. Run: npx vite build --config vite.offline.config.ts");
}
if (!existsSync(BUNDLE)) {
  fail("no content bundle. Run: python tools/build.py");
}

/**
 * Discover the emitted script and stylesheet from index.html rather than
 * assuming their names. Vite names the bundled CSS `style.css` for an IIFE
 * build and `app.css` for others, and that is exactly the kind of detail that
 * changes under you on a version bump.
 */
const indexHtml = readFileSync(join(RAW, "index.html"), "utf8");

function assetFromIndex(pattern, what) {
  const match = pattern.exec(indexHtml);
  if (!match) {
    fail(`could not find the ${what} referenced in dist-offline-raw/index.html`);
  }
  const path = join(RAW, basename(match[1]));
  if (!existsSync(path)) {
    fail(`index.html references ${match[1]}, which was not emitted`);
  }
  return readFileSync(path, "utf8");
}

const js = assetFromIndex(/<script[^>]+src="([^"]+\.js)"/i, "script");
let css = assetFromIndex(/<link[^>]+href="([^"]+\.css)"/i, "stylesheet");

/**
 * Collapse each @font-face's src list down to a single inlined woff2.
 *
 * KaTeX ships woff2, woff and truetype for all 20 faces. Inlining all three
 * would roughly triple the font payload for no benefit: every browser that can
 * run this app supports woff2. Base64 also costs ~33% over the raw bytes, so
 * being selective matters.
 */
let inlined = 0;
let droppedFallbacks = 0;
css = css.replace(/src:([^;}]+)/g, (whole, srcList) => {
  const woff2 = /url\(\s*["']?([^"')]+\.woff2)["']?\s*\)/.exec(srcList);
  if (!woff2) return whole;

  const assetPath = join(RAW, basename(woff2[1]));
  if (!existsSync(assetPath)) {
    fail(`font referenced by CSS but not emitted: ${woff2[1]}`);
  }
  const b64 = readFileSync(assetPath).toString("base64");
  inlined += 1;
  if (/\.woff\b|\.ttf\b/.test(srcList)) droppedFallbacks += 1;
  return `src:url(data:font/woff2;base64,${b64}) format("woff2")`;
});

// Any remaining url(...) would be a request the offline file cannot make.
const leftover = [...css.matchAll(/url\(\s*["']?(?!data:)([^"')]+)["']?\s*\)/g)];
if (leftover.length) {
  fail(
    `${leftover.length} asset reference(s) survived inlining and would 404 ` +
      `from file://: ${leftover.slice(0, 4).map((m) => m[1]).join(", ")}`,
  );
}

const bundleJson = readFileSync(BUNDLE, "utf8");
JSON.parse(bundleJson); // fail loudly here rather than at runtime on the phone

// `</script>` inside JSON would end the tag early. It cannot appear in this
// data today, but escaping it costs nothing and removes the whole class of bug.
const safeBundle = bundleJson
  .replace(/<\/script/gi, "<\/script")
  .replace(/<!--/g, "<\!--");

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<!-- viewport-fit=cover so the safe-area insets in styles.css have an effect
     on notched phones. -->
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#0e141b" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#eef1f5" media="(prefers-color-scheme: light)">
<!-- Lets Android's "Add to Home screen" open it without browser chrome. -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>MathCoach</title>
<!-- The only remote reference in the file, and it is optional: offline, the
     fallback stacks in styles.css take over and everything still reads. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap" media="all" onerror="this.remove()">
<style>${css}</style>
</head>
<body>
<div id="root"></div>
<script>window.__MATHCOACH_BUNDLE__=${safeBundle};</script>
<script>${js}</script>
</body>
</html>
`;

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, html, "utf8");

const mb = (n) => `${(n / 1024 / 1024).toFixed(2)} MB`;
const kb = (n) => `${Math.round(n / 1024)} KB`;
console.log("pack-offline: wrote dist-offline/mathcoach.html");
console.log(`  script   ${kb(Buffer.byteLength(js))}`);
console.log(`  styles   ${kb(Buffer.byteLength(css))}  (${inlined} fonts inlined, ${droppedFallbacks} fallback src lists dropped)`);
console.log(`  content  ${kb(Buffer.byteLength(bundleJson))}`);
console.log(`  total    ${mb(statSync(OUT).size)}  - one file, no requests`);
