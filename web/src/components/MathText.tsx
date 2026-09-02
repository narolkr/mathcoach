/** KaTeX rendering: bare LaTeX strings, and prose with `$...$` mixed in. */

import katex from "katex";
import { useMemo } from "react";

interface MathProps {
  latex: string;
  display?: boolean;
  className?: string;
}

/**
 * A LaTeX string with no surrounding prose.
 *
 * Named `Tex`, not `Math`: a component called `Math` shadows the global `Math`
 * object in every module that imports it, so `Math.round(...)` would silently
 * become a call to this component.
 */
export function Tex({ latex, display = false, className }: MathProps) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(latex, {
        displayMode: display,
        throwOnError: false,
        strict: false,
        output: "html",
      });
    } catch (error) {
      // Should be impossible: scripts/check-latex.mjs renders every string in
      // the bundle at build time. Show the source rather than a blank space.
      console.error("KaTeX failed on", latex, error);
      return `<code>${escapeHtml(latex)}</code>`;
    }
  }, [latex, display]);

  return (
    <span
      className={className}
      // KaTeX output, from build-time-validated content. Not user input.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

/**
 * Prose containing inline maths delimited by `$...$`, which is how hints and
 * step notes are authored. Splitting on `$` and rendering alternate segments
 * keeps the text as real text - selectable, wrappable, screen-readable.
 */
export function Prose({
  text,
  className,
}: {
  text: string;
  className?: string;
}) {
  const segments = useMemo(() => splitMath(text), [text]);
  return (
    <span className={className}>
      {segments.map((segment, index) =>
        segment.math ? (
          <Tex key={index} latex={segment.text} />
        ) : (
          <span key={index}>{segment.text}</span>
        ),
      )}
    </span>
  );
}

interface Segment {
  text: string;
  math: boolean;
}

export function splitMath(text: string): Segment[] {
  const segments: Segment[] = [];
  let index = 0;

  while (index < text.length) {
    const open = text.indexOf("$", index);
    if (open === -1) {
      segments.push({ text: text.slice(index), math: false });
      break;
    }
    const close = text.indexOf("$", open + 1);
    if (close === -1) {
      // Unpaired `$` - treat the rest as plain text rather than swallowing it.
      segments.push({ text: text.slice(index), math: false });
      break;
    }
    if (open > index) {
      segments.push({ text: text.slice(index, open), math: false });
    }
    segments.push({ text: text.slice(open + 1, close), math: true });
    index = close + 1;
  }

  return segments.filter((segment) => segment.text.length > 0);
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
