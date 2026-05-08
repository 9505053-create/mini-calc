# MiniCalc v1.0 Release Notes

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
