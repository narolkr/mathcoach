/**
 * Answer entry: a text field with a live KaTeX preview of what you typed.
 *
 * Plain text rather than a structured maths editor, deliberately: on a desktop
 * keyboard `6x*cos(3x^2+1)` is faster to type than it is to click, and this
 * user writes code all day. The preview exists so a typo shows up as
 * obviously-wrong rendered maths before you submit it.
 *
 * On phones that reasoning inverts, because the symbol characters are all one
 * layout-switch away - so a keypad appears there, driven by CSS media queries
 * rather than by guessing at the device.
 */

import { useCallback, useEffect, useMemo, useRef } from "react";
import { Tex } from "./MathText";
import { toLatex } from "../engine/toLatex";
import { MathKeypad, type KeypadKey } from "./MathKeypad";

interface AnswerInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
  autoFocus?: boolean;
  /** What shape of answer this slot wants: "a number", "in terms of x". */
  hintText?: string;
  /** Variables this problem allows, which become keypad keys. */
  variables?: string[];
}

export function AnswerInput({
  label,
  value,
  onChange,
  onSubmit,
  disabled,
  autoFocus,
  hintText,
  variables = [],
}: AnswerInputProps) {
  const preview = useMemo(() => toLatex(value), [value]);
  const inputRef = useRef<HTMLInputElement>(null);
  /** Where the caret should go once React has committed the new value. */
  const pendingCaret = useRef<number | null>(null);

  /**
   * Restore the caret after the value lands in the DOM.
   *
   * This has to be an effect rather than a `requestAnimationFrame` inside the
   * key handler. The frame callback fires *before* React commits the new
   * value, so setting the selection there gets overwritten by the re-render
   * and the caret snaps to the end - which broke `sqrt()` exactly where it
   * matters, turning the next keystroke into `sqrt()x` instead of `sqrt(x)`.
   */
  useEffect(() => {
    const caret = pendingCaret.current;
    if (caret === null) return;
    pendingCaret.current = null;
    const input = inputRef.current;
    if (!input) return;
    input.focus();
    input.setSelectionRange(caret, caret);
  }, [value]);

  /** Splice text in at the caret, and remember where the caret should end up. */
  const insert = useCallback(
    (key: KeypadKey) => {
      const input = inputRef.current;
      if (!input) return;

      // Fall back to the end of the value when the field has never been
      // focused and so has no selection of its own.
      const start = input.selectionStart ?? value.length;
      const end = input.selectionEnd ?? value.length;
      pendingCaret.current = start + key.insert.length - (key.caretBack ?? 0);
      onChange(value.slice(0, start) + key.insert + value.slice(end));
    },
    [value, onChange],
  );

  const backspace = useCallback(() => {
    const input = inputRef.current;
    if (!input) return;

    const start = input.selectionStart ?? value.length;
    const end = input.selectionEnd ?? value.length;
    // A selection deletes itself; an empty caret deletes the character before.
    const from = start === end ? Math.max(0, start - 1) : start;
    pendingCaret.current = from;
    onChange(value.slice(0, from) + value.slice(end));
  }, [value, onChange]);

  return (
    <div className="answer">
      <label className="answer-label" htmlFor={`answer-${label}`}>
        {label} =
      </label>
      <input
        ref={inputRef}
        id={`answer-${label}`}
        className="answer-input"
        type="text"
        value={value}
        spellCheck={false}
        autoComplete="off"
        autoCapitalize="off"
        autoCorrect="off"
        // `text` rather than a numeric inputmode: answers are expressions, and
        // a numeric pad would hide the letters that functions need.
        inputMode="text"
        enterKeyHint="done"
        // A syntax demo, deliberately not the derivative of anything in the
        // chapter - an example that doubles as an answer gives the level away.
        placeholder="syntax: 3*x^2 + sin(2*x) - sqrt(x)/2"
        disabled={disabled}
        autoFocus={autoFocus}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            onSubmit();
          }
        }}
      />
      <div className="answer-preview" aria-hidden="true">
        {preview ? (
          <Tex latex={preview} />
        ) : (
          <span className="muted">{hintText || "preview"}</span>
        )}
      </div>
      <MathKeypad
        variables={variables}
        onInsert={insert}
        onBackspace={backspace}
        disabled={disabled}
      />
    </div>
  );
}
