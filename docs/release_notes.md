# MiniCalc v1.0 Release Notes

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
