# MiniCalc v1.0 Release Notes

## PR-04 Calculation History / Session Tape

### Summary

PR-04 adds an in-memory, session-only Calculation History panel so users can inspect recent Standard, Date, and Programmer operations without adding persistence or export complexity.

### Features

- Added `HistoryStore` and immutable `HistoryEntry` snapshots.
- Added Standard Mode history for explicit `=` / keyboard Enter completions.
- Added controlled Standard error history, e.g. divide-by-zero as `5 ÷ 0 = Error` with error status.
- Added Date Mode history for successful date difference and date +/- duration calculations.
- Added Programmer Mode history for successful base-switch conversions, with normalized input values.
- Added a scrollable Tkinter History panel and `Clear History` button.

### Quality

- Kept history storage headless and session-only; no filesystem persistence.
- Preserved existing display-string controller APIs by adding narrow `pop_history_entry()` seams.
- Added HistoryStore unit tests, controller history tests, and fake-widget UI coordination tests.
- Deferred Standard immediate-execution chaining history to PR-05+ to avoid broadening engine APIs prematurely.

### Verification

- `python3 -m pytest -q` → 115 passed.
- `python3 -m py_compile calculator.py source/*.py tests/*.py` → clean.
- `git diff --check` → clean.

### Known Limits

- History is not persisted across app restarts.
- History cannot yet be exported, searched, copied, or clicked to restore inputs.
- Standard Mode chaining such as `1 + 2 +` updates the display but does not create a PR-04 history entry.
- Manual visible Tkinter smoke remains recommended before merge.

## PR-03 Date Calculator, Memory Keys, and Mode Controllers

### Summary

PR-03 adds a Date Calculator mode, Standard Mode memory keys, and a minimum mode-controller architecture refactor so the app can support three modes without concentrating all behavior inside `CalculatorUI`.

### Features

- Added Date Mode with two workflows:
  - day difference: `end_date - start_date`
  - date add/subtract duration: years, months, weeks, days
- Added deterministic month-end and leap-year clamping for date arithmetic.
- Added Standard Mode memory keys: `MC`, `MR`, `MS`, `M+`, `M-`.
- Added an `M` memory indicator when memory contains a non-zero value.
- Added headless controllers for Standard, Programmer, and Date modes.
- Moved `CalculatorEngine` to `source/calculator_engine.py` while keeping `calculator.py` as the Tkinter UI entrypoint.

### Quality

- Added `MemoryStore`, `DateCalculator`, and mode-controller unit tests.
- Extended lightweight UI coordination tests without launching Tkinter.
- Preserved PR-02.1 Programmer Mode behavior, including HEX digit `C` vs `AC` clear and 64-bit unsigned input cap.
- Added `docs/pr3/PR3_DEVELOPMENT_HISTORY.md` and `docs/pr3/PR3_SMOKE_CHECKLIST.md` for traceability.

### Verification

- `python3 -m pytest -q` → 94 passed.
- `python3 -m py_compile calculator.py source/*.py tests/*.py` → clean.
- `git diff --check` → clean.

### Known Limits

- Date Mode accepts ISO `YYYY-MM-DD` dates only.
- No timezone, time-of-day, or business-day support.
- Memory is session-only and Standard Mode only.
- Programmer Mode remains non-negative 64-bit unsigned integer conversion only.

## PR-02.1 Programmer Mode Hardening

### Summary

PR-02.1 applies the 3AI review follow-up items for PR-02 before PR-03 work begins. It does not add a new product mode; it hardens the Programmer Mode and local verification workflow.

### Changes

- Added `pytest.ini` so root-level `python -m pytest -q` discovers only `tests/` and ignores stale `pytest-cache-files-*` directories.
- Added `pytest-cache-files-*/` to `.gitignore`.
- Standardized `BaseConverter` imports in tests through `source.base_converter` and centralized test path setup in `tests/conftest.py`.
- Added a 64-bit unsigned integer limit to Programmer Mode conversion and append behavior.
- Renamed the visible clear button from `C` to `AC` to avoid confusion with HEX digit `C`.
- Added lightweight Programmer Mode UI coordination tests that use fake widgets instead of launching Tkinter.
- Tightened the Standard Mode negative-backspace regression assertion.
- Added `docs/programmer_mode_smoke_checklist.md` for manual GUI verification.

### Verification

- `python3 -m pytest -q` → 46 passed.

### Known Limits

- Programmer Mode remains non-negative-integer conversion only.
- Full per-mode controller refactor is deferred until PR-03 planning.

## PR-02 Programmer Mode

### Summary

PR-02 adds a Programmer Mode for integer base conversion while preserving the existing Standard Mode calculator behavior.

### Features

- Added `[Standard|Programmer]` mode controls to the Tkinter UI.
- Added `[DEC|HEX|BIN|OCT]` base controls in Programmer Mode.
- Added `BaseConverter` for headless DEC, HEX, BIN, and OCT validation/conversion.
- Enforced per-base input restrictions: BIN `0-1`, OCT `0-7`, DEC `0-9`, HEX `0-9` and uppercase `A-F`.
- HEX output is normalized to uppercase.
- Invalid programmer input is ignored instead of crashing the UI.

### Quality

- Added converter unit tests for conversion, normalization, invalid digit rejection, unsupported bases, append behavior, and backspace behavior.
- Kept Tkinter lazy-imported inside `CalculatorUI.__init__`.
- Preserved existing Standard Mode engine tests and behavior.

### Known Limits

- Programmer Mode is conversion-only and integer-only for PR-02.
- Negative programmer values are not supported.
- Standard Mode arithmetic state is independent from Programmer Mode state.

## Summary

MiniCalc v1.0 delivers a small Windows-friendly desktop calculator using Python and Tkinter. The calculator logic is separated into a headless `CalculatorEngine` for automated testing and a `CalculatorUI` wrapper for the desktop interface.

## Features

- Four-function arithmetic: add, subtract, multiply, divide
- Decimal input and positive/negative toggle
- Clear and equals controls
- Continuous operation support
- Keyboard support for common calculator keys
- Divide-by-zero error handling
- Scientific notation for results beyond the 12-digit display target

## Quality

- Calculation logic avoids `eval()`, `exec()`, and dynamic execution APIs.
- Unit tests target the engine only and do not import Tkinter.

## Known Limits

- Expression precedence is not implemented; MiniCalc follows immediate-execution desktop calculator behavior.
- Repeated equals keeps the displayed result instead of replaying the previous operation.
