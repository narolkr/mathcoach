/**
 * Getting the content bundle, whether it sits beside the app or inside it.
 *
 * Two deployment shapes:
 *
 * - **Served** (dev, or any static host): `content/bundle.json` is fetched.
 * - **Offline single file**: the whole bundle is inlined into the HTML as
 *   `window.__MATHCOACH_BUNDLE__`, because a `file://` page cannot fetch
 *   anything at all - the browser treats every local read as a cross-origin
 *   request and blocks it. That is the difference between "works from your
 *   phone's Downloads folder" and "blank screen".
 *
 * The inlined bundle wins when present, so the single-file build never touches
 * the network.
 */

import type { Bundle } from "../content/schema";
import { SCHEMA_VERSION } from "../content/schema";

declare global {
  interface Window {
    __MATHCOACH_BUNDLE__?: Bundle;
  }
}

function assertVersion(bundle: Bundle): Bundle {
  if (bundle.schemaVersion !== SCHEMA_VERSION) {
    throw new Error(
      `content is schema v${bundle.schemaVersion}, app expects ` +
        `v${SCHEMA_VERSION} - re-run python tools/build.py`,
    );
  }
  return bundle;
}

export async function loadBundle(): Promise<Bundle> {
  const inlined = window.__MATHCOACH_BUNDLE__;
  if (inlined) {
    return assertVersion(inlined);
  }

  // `document.baseURI` rather than a root-relative path, so a build served
  // from a subdirectory still finds its content.
  const response = await fetch(new URL("content/bundle.json", document.baseURI));
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return assertVersion((await response.json()) as Bundle);
}
