/**
 * The concept card renderer: Markdown with `$...$` and `$$...$$` maths.
 *
 * Maths is extracted to placeholders *before* Markdown parsing, because
 * Markdown would otherwise mangle LaTeX - underscores become emphasis, and
 * backslashes get eaten. The rendered KaTeX is substituted back afterwards.
 */

import katex from "katex";
import { marked } from "marked";
import { useMemo } from "react";

marked.setOptions({ gfm: true, breaks: false });

interface Extracted {
  source: string;
  maths: Array<{ latex: string; display: boolean }>;
}

const PLACEHOLDER = (index: number) => `@@MATHCOACH_MATH_${index}@@`;

function extractMath(markdown: string): Extracted {
  const maths: Extracted["maths"] = [];

  // $$...$$ first, so the $...$ pass can't split a display block in half.
  let source = markdown.replace(/\$\$([\s\S]+?)\$\$/g, (_match, latex) => {
    maths.push({ latex: String(latex).trim(), display: true });
    return PLACEHOLDER(maths.length - 1);
  });

  // `[^$]` rather than `[^$\n]`: the concept cards are hard-wrapped at ~79
  // columns, so inline maths regularly straddles a line break. Forbidding the
  // newline made those spans render as literal `$\sin(0.01) = 0.00999983$`.
  source = source.replace(/\$([^$]+?)\$/g, (_match, latex) => {
    maths.push({
      // Collapse the wrap's whitespace so KaTeX sees one clean line.
      latex: String(latex).replace(/\s+/g, " ").trim(),
      display: false,
    });
    return PLACEHOLDER(maths.length - 1);
  });

  return { source, maths };
}

function renderMath(latex: string, display: boolean): string {
  try {
    return katex.renderToString(latex, {
      displayMode: display,
      throwOnError: false,
      strict: false,
      output: "html",
    });
  } catch (error) {
    console.error("KaTeX failed on", latex, error);
    return `<code>${latex}</code>`;
  }
}

export function Markdown({ source }: { source: string }) {
  const html = useMemo(() => {
    const { source: withPlaceholders, maths } = extractMath(source);
    let out = marked.parse(withPlaceholders) as string;

    maths.forEach((entry, index) => {
      const rendered = renderMath(entry.latex, entry.display);
      // A display block sits alone in its own paragraph; unwrap it so the
      // paragraph doesn't add stray vertical space around it.
      out = out
        .replace(
          new RegExp(`<p>\\s*${PLACEHOLDER(index)}\\s*</p>`, "g"),
          entry.display ? `<div class="math-block">${rendered}</div>` : rendered,
        )
        .replace(new RegExp(PLACEHOLDER(index), "g"), rendered);
    });

    return out;
  }, [source]);

  return (
    <div
      className="prose"
      // Content is authored in this repo and validated at build time.
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
