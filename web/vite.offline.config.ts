import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Build variant for the single-file offline bundle.
 *
 * Two differences from the normal build, both forced by `file://`:
 *
 * - **IIFE, not ES modules.** A `file://` page cannot load a module script:
 *   module resolution goes through CORS, and every local file counts as a
 *   different origin. A classic script has no such problem.
 * - **One chunk.** Nothing may be requested separately, so code splitting and
 *   CSS splitting are both off.
 *
 * Fonts stay as separate files here; scripts/pack-offline.mjs inlines the ones
 * that are actually needed, which keeps the woff and truetype fallbacks out of
 * the final file.
 */
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: {
    outDir: "dist-offline-raw",
    emptyOutDir: true,
    cssCodeSplit: false,
    // Deliberately low: the packer decides what gets inlined, so that only
    // woff2 makes it in rather than all three font formats.
    assetsInlineLimit: 0,
    rollupOptions: {
      output: {
        format: "iife",
        inlineDynamicImports: true,
        entryFileNames: "app.js",
        assetFileNames: "[name][extname]",
      },
    },
  },
});
