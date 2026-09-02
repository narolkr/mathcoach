/**
 * Render every LaTeX string in the content bundle with KaTeX.
 *
 * Python can validate the maths but it cannot know whether KaTeX will render
 * the output, so this is the other half of that guarantee. Runs in `npm test`
 * and exits non-zero on the first unrenderable string, which means a level with
 * broken typesetting cannot reach the app.
 */

import { readFileSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";
import katex from "katex";

const HERE = dirname(fileURLToPath(import.meta.url));
const ROOT = join(HERE, "..", "..");
const BUNDLE = join(HERE, "..", "public", "content", "bundle.json");

/** Prose fields carry inline maths between `$...$`. Pull those out too. */
function extractInlineMath(text) {
  const found = [];
  const parts = text.split("$");
  // Odd indices are between a matched pair of delimiters.
  for (let i = 1; i < parts.length; i += 2) {
    if (parts[i].trim()) found.push(parts[i]);
  }
  if (parts.length % 2 === 0) {
    throw new Error(`unpaired $ in prose: ${text.slice(0, 90)}`);
  }
  return found;
}

/** Everything that will be handed to KaTeX, with a path for error messages. */
function* latexStrings(bundle) {
  // Diagnostic items carry full problems, so walk them through the same checks
  // as a chapter with a single synthetic level.
  const levelSources = [
    ...bundle.chapters,
    ...(bundle.diagnostic
      ? [
          {
            levels: [
              {
                id: bundle.diagnostic.id,
                problems: bundle.diagnostic.items.map((item) => item.problem),
              },
            ],
          },
        ]
      : []),
  ];

  for (const chapter of levelSources) {
    for (const level of chapter.levels) {
      for (const problem of level.problems) {
        const where = `${level.id}/${problem.id}`;
        yield [`${where} promptLatex`, problem.promptLatex, false];

        for (const answer of problem.answers) {
          yield [`${where} answer[${answer.label}]`, answer.latex, false];
        }
        for (const [index, step] of problem.steps.entries()) {
          yield [`${where} step[${index}].latex`, step.latex, true];
          for (const inline of extractInlineMath(step.note)) {
            yield [`${where} step[${index}].note`, inline, false];
          }
        }
        for (const [index, hint] of problem.hints.entries()) {
          for (const inline of extractInlineMath(hint)) {
            yield [`${where} hint[${index}]`, inline, false];
          }
        }
        for (const answer of problem.answers) {
          for (const distractor of answer.distractors) {
            for (const inline of extractInlineMath(distractor.feedback)) {
              yield [`${where} distractor[${distractor.id}]`, inline, false];
            }
          }
        }

        // Choice options: the label is LaTeX when isLatex is set, and the
        // feedback is prose that may carry inline $...$ math.
        for (const choice of problem.choices ?? []) {
          if (choice.isLatex) {
            yield [`${where} choice[${choice.id}].label`, choice.label, false];
          }
          for (const inline of extractInlineMath(choice.feedback)) {
            yield [`${where} choice[${choice.id}].feedback`, inline, false];
          }
        }
      }

      // Concept cards: $$...$$ display blocks and $...$ inline.
      //
      // These regexes MUST match Markdown.tsx's extractMath exactly. When they
      // drifted, this script shared the renderer's blind spot: inline maths
      // wrapped across a newline was invisible to both, so the check reported
      // everything clean while two spans rendered as literal dollar signs.
      if (level.bodyMd) {
        let body = level.bodyMd;
        const display = [...body.matchAll(/\$\$([\s\S]+?)\$\$/g)];
        for (const [index, match] of display.entries()) {
          yield [`${level.id} bodyMd display[${index}]`, match[1].trim(), true];
        }
        body = body.replace(/\$\$[\s\S]+?\$\$/g, "");
        const inline = [...body.matchAll(/\$([^$]+?)\$/g)];
        for (const [index, match] of inline.entries()) {
          yield [
            `${level.id} bodyMd inline[${index}]`,
            match[1].replace(/\s+/g, " ").trim(),
            false,
          ];
        }

        // Anything left is an unpaired delimiter, which would reach the reader
        // as a raw `$`. Report it rather than rendering it.
        const leftover = body.replace(/\$[^$]+?\$/g, "");
        const strays = (leftover.match(/\$/g) ?? []).length;
        if (strays > 0) {
          const context = (leftover.match(/[^\n]*\$[^\n]*/g) ?? [])
            .slice(0, 3)
            .join(" | ");
          throw new Error(
            `${level.id}: ${strays} unpaired $ in bodyMd - they would render ` +
              `as literal dollar signs. Near: ${context}`,
          );
        }
      }
    }
  }
}

let bundle;
try {
  bundle = JSON.parse(readFileSync(BUNDLE, "utf8"));
} catch (error) {
  console.error(
    `Cannot read ${relative(ROOT, BUNDLE)}.\n` +
      "Run `python tools/build.py` from the repository root first.",
  );
  console.error(String(error.message ?? error));
  process.exit(1);
}

const failures = [];
let checked = 0;

for (const [where, latex, display] of latexStrings(bundle)) {
  checked += 1;
  try {
    // strict:false matches the app's render options exactly; throwOnError:true
    // is the whole point of this script.
    katex.renderToString(latex, {
      displayMode: display,
      throwOnError: true,
      strict: false,
      output: "html",
    });
  } catch (error) {
    failures.push({ where, latex, message: String(error.message ?? error) });
  }
}

// A leaked \log means natural log will render as "log" rather than "ln".
const raw = readFileSync(BUNDLE, "utf8");
if (raw.includes("\\\\log")) {
  failures.push({
    where: "bundle",
    latex: "\\log",
    message: "raw \\log in the bundle; natural log should be emitted as \\ln",
  });
}

if (failures.length > 0) {
  console.error(`KaTeX check FAILED: ${failures.length} of ${checked} strings\n`);
  for (const failure of failures.slice(0, 20)) {
    console.error(`  ${failure.where}`);
    console.error(`    ${failure.latex}`);
    console.error(`    ${failure.message}\n`);
  }
  if (failures.length > 20) {
    console.error(`  ...and ${failures.length - 20} more`);
  }
  process.exit(1);
}

console.log(`KaTeX check passed: ${checked} strings render cleanly.`);
