# Architecture Plan: MiniCalc

## Project Overview
MiniCalc is a small Windows desktop calculator built to validate a complete autonomous development workflow: requirements analysis, implementation, debugging, testing, and release preparation. The application will provide a dark-themed Tkinter GUI backed by a headless, importable arithmetic engine that supports basic calculator behavior without using `eval()`, `exec()`, or dynamic code execution.

## Technology Choice
- Language: Python 3.10+
- GUI: Tkinter, included with standard Python desktop installs
- Test framework: `pytest`
- Calculation approach: explicit state machine with direct arithmetic dispatch
- Packaging approach: run from source in Phase 1; optional PyInstaller later

## File List
- `calculator.py`: Main application module containing `CalculatorEngine`, `CalculatorUI`, formatting helpers, and the `__main__` launch block.
- `tests/test_calculator.py`: Headless unit tests for `CalculatorEngine`; must not import or instantiate Tkinter UI.
- `requirements.txt`: Development/test dependencies, initially `pytest`.
- `README.md`: Project description, setup instructions, run command, test command, and supported calculator behavior.
- `.gitignore`: Python cache, virtual environment, test cache, and build artifact exclusions.
- `release_notes.md`: Final release summary for v1.0, including features, known limits, and verification results.

## Module Boundaries
`CalculatorEngine` owns all arithmetic, input sequencing, numeric formatting, and calculator state transitions. It must remain importable in a headless environment and must not import `tkinter`.

`CalculatorUI` owns all Tkinter widgets, layout, theme, keyboard bindings, and calls into `CalculatorEngine` through public methods only. Tkinter imports should happen inside `CalculatorUI.__init__`, a UI factory method, or the `if __name__ == "__main__":` block.

## Class Design

### `CalculatorEngine`
Purpose: Pure-Python calculator state machine and arithmetic engine.

Public methods:
- `press_digit(digit: str) -> str`: Add a digit to the current operand and return display text.
- `press_decimal() -> str`: Add a decimal point if valid and return display text.
- `press_operator(operator: str) -> str`: Accept `+`, `-`, `*`, `/`; store or apply pending operation and return display text.
- `press_equals() -> str`: Resolve the pending operation and return display text.
- `press_clear() -> str`: Reset all state and return the initial display text.
- `press_toggle_sign() -> str`: Toggle sign for the active displayed number.
- `press_percent() -> str`: Convert active displayed number to percentage value.
- `get_display() -> str`: Return current display text.
- `get_state() -> str`: Return current state name for tests/debugging.

Internal responsibilities:
- Track `first_operand`, `second_operand/current_input`, `pending_operator`, `display`, and `state`.
- Perform arithmetic through an operator dispatch table, e.g. `{"+": add, "-": sub, "*": mul, "/": div}`.
- Reject or replace invalid operator sequences according to calculator rules.
- Format results to a maximum of 8 decimal places and 12 displayed numeric characters where practical.
- Never call `eval()`, `exec()`, `compile()`, or any dynamic execution API.

### `CalculatorUI`
Purpose: Dark-themed Tkinter desktop interface for the calculator.

Public methods:
- `__init__(engine: CalculatorEngine | None = None)`: Create or receive an engine instance and initialize UI.
- `run() -> None`: Start the Tkinter main loop.
- `handle_button(label: str) -> None`: Route button clicks to engine methods and update display.
- `handle_key(event) -> None`: Route keyboard input to engine methods and update display.
- `update_display(text: str) -> None`: Render the latest engine display text.

UI responsibilities:
- Build a compact fixed-size or minimally resizable window.
- Use dark background, readable display, and distinct operator/equal/clear button colors.
- Provide buttons for digits, decimal, `+`, `-`, `*`, `/`, `=`, `C`, optional `%`, and optional `+/-`.
- Bind keyboard input for digits, operators, Enter/Return, Escape, Backspace where supported.
- Avoid calculation logic beyond mapping UI labels to engine calls.

## Calculator States

### `waiting_for_first_operand`
Initial state after startup or clear. Digit/decimal input builds the first operand. An operator is only accepted after a valid first operand exists; otherwise it is ignored except sign toggle.

### `waiting_for_second_operand`
State after a valid first operand and operator are selected. Digit/decimal input builds the second operand. Pressing another operator before entering the second operand replaces the pending operator to handle illegal input sequences cleanly.

### `result_displayed`
State after `=` or an automatic continuous calculation. Digit input starts a new calculation. Operator input reuses the displayed result as the first operand for a continued calculation.

## Input Flow
- Digits append to the active input buffer unless the current display is `Error` or `Overflow`, in which case input starts fresh only after `C`.
- Decimal point is allowed once per active input buffer.
- Pressing an operator after first operand stores it and waits for the second operand.
- Pressing an operator after second operand computes immediately, displays the result, then stores the new operator for continuous calculations such as `1 + 2 + 3 = 6`.
- Pressing equals computes only when both operands and a pending operator are available.
- Pressing equals repeatedly may either keep the result unchanged or repeat the last operation; Phase 1 should choose unchanged for simpler, predictable behavior.

## Arithmetic Strategy
Use a small state machine plus direct operation functions, not a full expression parser. MiniCalc only needs immediate-execution calculator semantics, so `1 + 2 * 3 =` should behave like a basic calculator if entered sequentially, not like precedence-based algebra.

Implementation sketch:
- Store operands as `Decimal` or `float`.
- Prefer `Decimal` for predictable display formatting of cases like `0.1 + 0.2`.
- Convert input strings to `Decimal` only when computing.
- Arithmetic dispatch:
  - `+`: `left + right`
  - `-`: `left - right`
  - `*`: `left * right`
  - `/`: validate right operand is not zero, then `left / right`

## Formatting Rules
- Normal results display up to 8 decimal places.
- Trailing zeroes and a trailing decimal point are removed for typical integer-looking results.
- Test expectation for floating precision can assert normalized display, for example `0.3` or a documented fixed form.
- If the integer part is too large for the 12-digit display target, use scientific notation where possible.
- If a result is non-finite or cannot be reasonably represented, display `Overflow`.

## Error Handling Strategy
- Divide by zero: display `Error`, lock calculation input except `C`, and avoid crashing.
- Overflow: display `Overflow`, lock calculation input except `C`, and avoid crashing.
- Invalid numbers: display `Error` for impossible conversion cases, though UI should prevent most of them.
- Consecutive operators:
  - If no second operand has been entered, replace the pending operator.
  - If a second operand exists, compute immediately and then store the new operator.
- Multiple decimal points: ignore additional decimal presses.
- Equals without complete expression: leave display unchanged.
- Clear: always resets from any normal or error state.

## Test Strategy
Tests target `CalculatorEngine` only and must run without Tkinter, windows, or display server access.

Required tests in `tests/test_calculator.py`:
- Basic addition: `2 + 3 = 5`
- Basic subtraction: `10 - 4 = 6`
- Multiplication: `6 * 7 = 42`
- Division: `8 / 2 = 4`
- Divide by zero: `5 / 0 = Error`, then `C` restores `0`
- Floating point display: `0.1 + 0.2` produces the documented rounded display
- Continuous operation: `1 + 2 + 3 = 6`
- Negative result: `3 - 5 = -2`
- Consecutive operators: `5 + - 2 = 3` if replacement behavior is used
- Decimal guard: pressing decimal twice does not produce invalid input
- Result continuation: `2 + 3 =`, then `* 4 =` gives `20`

Test constraints:
- Do not import `tkinter` in test files.
- Instantiate `CalculatorEngine` directly.
- Assert returned display strings and selected state transitions.
- Include tests for recovery after `Error` and `Overflow` where feasible.

## README Content
README should include:
- Project purpose: MiniCalc desktop calculator for workflow validation.
- Requirements: Python 3.10+.
- Setup: create virtual environment and install `requirements.txt`.
- Run: `python calculator.py`.
- Test: `pytest`.
- Safety note: calculations do not use `eval()` or `exec()`.
- Feature list and known limitations.

## Development Phases
1. Scaffold files and initial README.
2. Implement `CalculatorEngine` with state machine and tests.
3. Implement Tkinter `CalculatorUI` with dark theme and button routing.
4. Run and fix unit tests.
5. Manually smoke-test GUI on Windows.
6. Create release notes and commit cleanly.

## Acceptance Mapping
- Four arithmetic operations: `CalculatorEngine` arithmetic dispatch.
- UI operable: `CalculatorUI` buttons and display.
- No crash on errors: explicit error state and `C` recovery.
- Continuous operations: operator press computes pending expression when second operand exists.
- Headless QA: `tests/test_calculator.py` imports only engine code.
- Security constraint: no dynamic execution APIs in calculation path.
