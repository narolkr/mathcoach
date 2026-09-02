/**
 * A compact keypad for the characters a phone keyboard hides.
 *
 * On a desktop keyboard `6*x*cos(3*x^2+1)` is faster to type than to click,
 * which is why the answer field is plain text. On a phone it is the opposite:
 * `^`, `*`, `(`, `)` and `/` all sit behind the symbol layer, so a single
 * answer means three or four trips between layouts. That friction is enough to
 * stop someone doing their thirty minutes.
 *
 * So this appears only where it helps: narrow viewports and coarse pointers,
 * decided in CSS rather than by sniffing the user agent.
 *
 * Digits and letters are deliberately absent - every keyboard has those. Only
 * the awkward characters earn a key, plus the variables this particular problem
 * actually uses.
 */

interface KeypadKey {
  /** What gets inserted. */
  insert: string;
  /** What the key shows. Defaults to `insert`. */
  label?: string;
  /** How many characters to step the caret back after inserting, so that
   *  `sqrt()` leaves the cursor between the brackets. */
  caretBack?: number;
  wide?: boolean;
}

const OPERATORS: KeypadKey[] = [
  { insert: "^" },
  { insert: "(" },
  { insert: ")" },
  { insert: "*", label: "×" },
  { insert: "/", label: "÷" },
  { insert: "-", label: "−" },
];

const FUNCTIONS: KeypadKey[] = [
  { insert: "sqrt()", label: "√", caretBack: 1 },
  { insert: "sin()", label: "sin", caretBack: 1 },
  { insert: "cos()", label: "cos", caretBack: 1 },
  { insert: "ln()", label: "ln", caretBack: 1 },
  { insert: "e^()", label: "eˣ", caretBack: 1 },
  { insert: "pi", label: "π" },
];

interface MathKeypadProps {
  /** The variables this problem declares, which become their own keys. */
  variables: string[];
  onInsert: (key: KeypadKey) => void;
  onBackspace: () => void;
  disabled?: boolean;
}

export function MathKeypad({
  variables,
  onInsert,
  onBackspace,
  disabled,
}: MathKeypadProps) {
  const variableKeys: KeypadKey[] = variables.map((name) => ({ insert: name }));

  return (
    <div className="keypad" role="group" aria-label="Maths keypad">
      {/* Grouped by kind, six to a row. Mixing the variables in with the
          operators made the first row wrap at eight items, which left two
          keys alone on a second line. */}
      <div className="keypad-row">
        {OPERATORS.map((key) => (
          <Key key={key.insert} k={key} onInsert={onInsert} disabled={disabled} />
        ))}
      </div>
      <div className="keypad-row">
        {FUNCTIONS.map((key) => (
          <Key key={key.insert} k={key} onInsert={onInsert} disabled={disabled} />
        ))}
      </div>
      <div className="keypad-row">
        {variableKeys.map((key) => (
          <Key
            key={key.insert}
            k={key}
            onInsert={onInsert}
            disabled={disabled}
            variant="var"
          />
        ))}
        <button
          type="button"
          className="keypad-key keypad-del"
          aria-label="Delete the character before the cursor"
          disabled={disabled}
          // Insertion must not steal focus from the field, or the caret
          // position is lost and every key would append at the end.
          onMouseDown={(event) => event.preventDefault()}
          onClick={onBackspace}
        >
          ⌫
        </button>
      </div>
    </div>
  );
}

function Key({
  k,
  onInsert,
  disabled,
  variant,
}: {
  k: KeypadKey;
  onInsert: (key: KeypadKey) => void;
  disabled?: boolean;
  variant?: "var";
}) {
  return (
    <button
      type="button"
      className={`keypad-key${variant === "var" ? " keypad-var" : ""}`}
      aria-label={`Insert ${k.insert}`}
      disabled={disabled}
      onMouseDown={(event) => event.preventDefault()}
      onClick={() => onInsert(k)}
    >
      {k.label ?? k.insert}
    </button>
  );
}

export type { KeypadKey };
