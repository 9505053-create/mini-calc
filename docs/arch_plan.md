# Architecture Plan: MiniCalc PR-02 Programmer Mode / Base Converter

## 1. Architecture Overview
PR-02 adds programmer-mode base conversion beside the existing standard calculator.

The current `CalculatorEngine` remains the headless arithmetic state machine for decimal calculator behavior. A new pure-Python `BaseConverter` module owns base validation and conversion for DEC, HEX, BIN, and OCT. The two engines should remain independent: standard mode routes button/key input to `CalculatorEngine`; programmer mode routes base-specific input and base-switch operations through `BaseConverter`.

`CalculatorUI` becomes the coordinator for mode selection, current base selection, visible controls, and display updates. It must not move arithmetic logic into UI callbacks. Tkinter must remain lazily imported inside `CalculatorUI.__init__` or the `if __name__ == "__main__"` block.

Implementation should preserve the existing `calculator.py` API so all 28 current tests keep importing and testing `CalculatorEngine`. If test imports are changed to prefer `source`, ensure `calculator.py` remains importable from the test process before changing `tests/test_calculator.py`.

## 2. File List
- calculator.py: Existing application module; extend `CalculatorUI` with Standard/Programmer mode controls while preserving `CalculatorEngine` behavior.
- source/base_converter.py: New headless conversion module containing `BaseConverter` and no Tkinter imports.
- tests/test_calculator.py: Existing arithmetic regression tests; update path setup to include `PROJECT_ROOT / "source"` without breaking `from calculator import CalculatorEngine`.
- tests/test_base_converter.py: New headless unit tests for base conversion, validation, normalization, and invalid input behavior.
- README.md: Update feature list, run/test commands, and programmer-mode usage notes.
- docs/release_notes.md: Add PR-02 release notes covering programmer mode, supported bases, tests, and known limits.
- docs/arch_plan.md: This architecture plan for PR-02.

## 3. Class Design
### `BaseConverter`
Purpose: Pure conversion and validation service for integer values in DEC, HEX, BIN, and OCT.

Constants:
- `BASES = {"DEC": 10, "HEX": 16, "BIN": 2, "OCT": 8}`
- `VALID_DIGITS = {"DEC": "0123456789", "HEX": "0123456789ABCDEF", "BIN": "01", "OCT": "01234567"}`

Public API:
- `normalize(value: str, base: str) -> str`: Trim whitespace, uppercase HEX letters, remove leading zeroes while returning `"0"` for empty/zero values.
- `is_valid(value: str, base: str) -> bool`: Return whether every character is allowed for the base. Empty strings are invalid except where UI treats them as display `"0"`.
- `convert(value: str, from_base: str, to_base: str) -> str`: Validate and convert an integer string between supported bases. Return uppercase HEX output.
- `convert_all(value: str, from_base: str) -> dict[str, str]`: Return display strings for all four bases, useful for future UI readouts.
- `append_digit(current: str, digit: str, base: str) -> str`: Append only valid base characters; invalid input returns the original value.
- `backspace(current: str) -> str`: Remove the last character and return `"0"` when empty.

Error behavior:
- Unsupported base names raise `ValueError`.
- Invalid input should not crash the UI. The UI should catch `ValueError` and keep the previous display or show a controlled `"Error"` state.
- Conversion uses `int(value, radix)` and explicit format functions, not `eval()`, `exec()`, or `compile()`.

Formatting rules:
- DEC output uses `str(number)`.
- HEX output uses uppercase `format(number, "X")`.
- BIN output uses `format(number, "b")`.
- OCT output uses `format(number, "o")`.
- Negative numbers are out of scope for PR-02 programmer input unless explicitly added later.

## 4. UI Integration
Add a mode toggle row above the existing calculator keypad:
- `[Standard] [Programmer]`

In Standard mode:
- Existing display, buttons, keyboard behavior, and `CalculatorEngine` routing remain unchanged.
- Base selector controls can be hidden or disabled.
- Existing decimal, percent, sign toggle, and arithmetic buttons continue to behave as today.

In Programmer mode:
- Show base buttons `[DEC] [HEX] [BIN] [OCT]`.
- Disable or hide decimal point and percent because PR-02 conversion is integer-only.
- Digit buttons must respect the selected base:
  - BIN: enable `0`, `1`; reject `2`-`9` and `A`-`F`.
  - OCT: enable `0`-`7`; reject `8`, `9`, `A`-`F`.
  - DEC: enable `0`-`9`; reject `A`-`F`.
  - HEX: enable `0`-`9`, `A`-`F`.
- Add HEX input buttons `A` through `F` only in Programmer mode, or support them through keyboard input while visible controls show them.
- When a base button is pressed, convert the current programmer display from the old base to the new base and update the display.
- Invalid keyboard or button input must be ignored, not allowed to crash.

UI callback routing:
- `handle_button()` checks `self.mode`.
- Standard mode delegates to existing `CalculatorEngine` methods.
- Programmer mode delegates input validation/conversion to `BaseConverter`.
- `update_display()` remains the single display update path.

## 5. State Management
Add UI-owned state:
- `self.mode: str = "Standard"`
- `self.current_base: str = "DEC"`
- `self.programmer_value: str = "0"`
- `self.base_converter = BaseConverter()`

Standard state remains entirely inside `CalculatorEngine`.

Mode switching:
- Standard to Programmer: initialize `programmer_value` from the current standard display only if it is a non-negative integer decimal string; otherwise use `"0"`.
- Programmer to Standard: clear or preserve the standard engine independently. Recommended behavior for PR-02 is to leave `CalculatorEngine` state untouched and restore its display when returning to Standard.
- Programmer base switch: convert `programmer_value` from `old_base` to `new_base`; only update `current_base` after successful conversion.

Programmer display invariant:
- `programmer_value` is always normalized for `current_base`.
- HEX letters are always uppercase.
- Empty input displays `"0"`.
- Invalid input leaves `programmer_value` and display unchanged.

## 6. Test Strategy
Existing tests:
- Keep all 28 `tests/test_calculator.py` tests passing.
- Add or adjust the pre-check path setup:
  `sys.path.insert(0, str(PROJECT_ROOT / "source"))`
- If `calculator.py` stays at repo root, retain a repo-root path entry or add a compatibility import path so `CalculatorEngine` remains importable.

New `tests/test_base_converter.py` coverage:
- DEC to HEX: `255 -> FF`
- DEC to BIN: `10 -> 1010`
- DEC to OCT: `8 -> 10`
- HEX to DEC: `FF -> 255`
- BIN to DEC: `1010 -> 10`
- OCT to DEC: `10 -> 8`
- HEX lowercase input normalizes to uppercase before conversion.
- Leading zeroes normalize: `000F -> F`, `0000 -> 0`.
- Invalid BIN digit rejects `2`.
- Invalid OCT digit rejects `8`.
- Invalid DEC digit rejects `A`.
- Invalid HEX digit rejects `G`.
- Unsupported base raises `ValueError`.
- `append_digit()` ignores invalid characters and preserves current display.
- Empty input validation is false, while UI-level empty display should remain `"0"`.

Optional UI smoke tests can instantiate `CalculatorUI` only in an environment with a display. Unit tests should remain headless and avoid importing Tkinter directly.

## 7. Known Constraints
- Do NOT use `eval()`, `exec()`, or `compile()`.
- Tkinter must be lazy-imported only inside `CalculatorUI.__init__` or `if __name__ == "__main__"`.
- All 28 existing calculator tests must still pass.
- HEX display must be uppercase only.
- Invalid input must not crash the app.
- Programmer mode is integer-only for PR-02.
- Keep `CalculatorEngine` independent from `BaseConverter`; UI coordinates between them.
- Preserve learned calculator fixes: scientific formatting checks integer digits first, mainstream percent behavior, and no `-0` display from sign toggle.
