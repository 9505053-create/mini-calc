# MiniCalc PR-03 Spec — Date Calculator, Memory Keys, Mode Controllers

Date: 2026-05-15
Base branch: `pr3-planning` created from `pr2.1-local-hardening`
Base commit: `a6bcbe0 fix: harden programmer mode before PR3`
Status: Planning draft for 3AI review

## 1. Goal

PR-03 expands MiniCalc from two modes into a small multi-mode calculator while keeping the project stable and testable:

1. Add **Date Calculator** mode.
2. Add **Memory Keys** for Standard Mode.
3. Introduce the **minimum necessary mode-controller architecture** so `CalculatorUI` does not become a God Object when Date Mode is added.

PR-03 must preserve PR-02.1 behavior:

- Standard Mode arithmetic continues to pass all existing tests.
- Programmer Mode keeps DEC/HEX/BIN/OCT conversion and 64-bit unsigned cap.
- Root-level `python -m pytest -q` remains clean.
- No `eval()`, `exec()`, or dynamic code execution is allowed.

## 2. Product Scope

### 2.1 Date Calculator Mode

Date Calculator mode supports two workflows.

#### Workflow A — Difference Between Dates

User can enter/select:

- Start date
- End date

MiniCalc displays:

- Difference in days using Python `date` arithmetic: `end_date - start_date`
- Same date returns `0 days`
- End before start is allowed and returns a negative day count

Required examples:

- `2026-05-15` to `2026-05-16` → `1 day`
- `2026-05-15` to `2026-05-15` → `0 days`
- `2026-05-16` to `2026-05-15` → `-1 day`
- `2024-02-28` to `2024-03-01` → `2 days` because 2024 is leap year

#### Workflow B — Add/Subtract Duration

User can enter/select:

- Base date
- Operation: add or subtract
- Duration components:
  - years
  - months
  - weeks
  - days

MiniCalc displays the resulting date.

Duration order must be deterministic:

1. Apply years.
2. Apply months.
3. Apply weeks and days as a combined day delta.

Month/year overflow rule:

- If the target month has fewer days than the source date, clamp to the last valid day of the target month.

Required examples:

- `2026-05-15 + 10 days` → `2026-05-25`
- `2026-05-15 - 2 weeks` → `2026-05-01`
- `2024-01-31 + 1 month` → `2024-02-29`
- `2025-01-31 + 1 month` → `2025-02-28`
- `2024-02-29 + 1 year` → `2025-02-28`

### 2.2 Memory Keys

Memory Keys are added for Standard Mode only in PR-03.

Required keys:

- `MC` — memory clear; set memory to `0`
- `MR` — memory recall; load memory value into the current Standard Mode input/display
- `MS` — memory store; replace memory with current Standard Mode display value
- `M+` — add current Standard Mode display value to memory
- `M-` — subtract current Standard Mode display value from memory

Required behavior:

- Memory uses `Decimal`, matching `CalculatorEngine` precision style.
- Invalid current display values such as `Error` do not change memory.
- Memory starts at `0`.
- `MR` after `MC` recalls `0`.
- A minimal `M` indicator should be shown when memory is non-zero; if deferred, documentation must not imply a visible indicator exists.
- Memory persists while switching between Standard, Programmer, and Date modes during one app session.
- PR-03 does not need persistent memory across app restarts.

### 2.3 Mode Controller Adjustment

PR-03 introduces mode controllers to keep responsibilities clear.

Current state after PR-02.1:

- `CalculatorEngine` owns Standard arithmetic state.
- `BaseConverter` owns Programmer conversion logic.
- `CalculatorUI` currently owns mode switching, Programmer state, button enable/disable rules, and display coordination.

PR-03 target:

- `CalculatorUI` remains the only Tkinter owner.
- Headless logic remains outside Tkinter and testable.
- Mode-specific routing moves out of large UI methods where practical.
- The controller extraction should be incremental and minimal; do not rewrite the entire application.

Recommended controller boundaries:

- `StandardModeController`
  - wraps `CalculatorEngine`
  - coordinates `MemoryStore`
  - handles Standard button/key commands
- `ProgrammerModeController`
  - wraps `BaseConverter`
  - owns `current_base` and `programmer_value`
  - handles Programmer button/key commands and base switching
- `DateModeController`
  - wraps `DateCalculator`
  - owns Date Mode state/workflow selection
  - formats Date Mode display strings
- `CalculatorUI`
  - creates widgets
  - dispatches UI events to the active controller
  - applies controller-provided button state / visibility
  - updates display

## 3. Non-Goals

PR-03 must not include:

- Time-of-day, timezone, daylight-saving, locale calendar, holiday, or business-day logic.
- Natural-language date parsing.
- Expression parser or operator precedence rewrite for Standard Mode.
- Signed/two's-complement Programmer Mode arithmetic.
- Persistent memory across app restarts.
- Full MVC rewrite or multi-file Tkinter UI framework.
- GitHub `main` merge of PR-02.1 unless Scott separately approves it.

## 4. Data and Formatting Rules

### 4.1 Dates

- Internal date type: `datetime.date`
- Canonical string format: ISO `YYYY-MM-DD`
- Invalid dates must be rejected with controlled errors, not crashes.
- Recommended user-facing invalid display: `Invalid date`
- Date output format: ISO `YYYY-MM-DD`

### 4.2 Duration

- Duration components are integers.
- Empty duration fields are treated as `0`.
- Whitespace-only duration fields are treated as `0`.
- Non-integer duration fields such as `abc` or `1.5` are controlled validation errors.
- Negative component strings are validation errors; subtraction uses the operation selector instead.
- Weeks are converted to `7 * weeks` days after year/month application.

### 4.3 Memory Values

- Memory values use `Decimal` internally.
- Display formatting should reuse existing `CalculatorEngine` formatting where practical.
- `has_value` means "memory is non-zero" for a calculator-style `M` indicator. Storing `0` is allowed and recalls `0`, but the indicator may be inactive.
- Memory recall should behave like current input replacement, not an immediate computation.
- `MR` behavior by Standard engine state:
  - `WAITING_FIRST`: replace the current input/display with memory.
  - `WAITING_SECOND` with no current second operand: set the second operand to memory and preserve the pending operator.
  - `WAITING_SECOND` with an active second operand: replace that active second operand with memory.
  - `RESULT`: start a new first operand from memory and clear pending operation.
  - `ERROR`: no-op until `AC`, matching existing digit-input behavior after errors.

## 5. Proposed Files

Create:

- `source/memory_store.py`
- `source/date_calculator.py`
- `source/calculator_engine.py`
- `source/mode_controllers.py`
- `tests/test_memory_store.py`
- `tests/test_date_calculator.py`
- `tests/test_calculator_engine.py`
- `tests/test_mode_controllers.py`
- `docs/pr3/PR3_SPEC.md`
- `docs/pr3/IMPLEMENTATION_PLAN.md`
- `docs/pr3/ACCEPTANCE_CRITERIA.md`
- `docs/date_calculator_smoke_checklist.md`

Modify:

- `calculator.py`
- `README.md`
- `docs/release_notes.md`

Mandatory architecture prerequisite before controller extraction:

- Move `CalculatorEngine` from `calculator.py` to `source/calculator_engine.py`, while keeping a compatibility re-export in `calculator.py` so existing imports such as `from calculator import CalculatorEngine` continue to work.
- Reason: `CalculatorUI` will need to import mode controllers, and `StandardModeController` needs `CalculatorEngine`. Leaving `CalculatorEngine` only in root `calculator.py` creates a likely circular import path.
- Add a public `CalculatorEngine.replace_current_input(text: str) -> str` method before wiring `MR`. Controllers must not mutate private engine fields directly.

## 6. Testing Requirements

Minimum automated gate:

```bash
python3 -m pytest -q
python3 -m py_compile calculator.py source/calculator_engine.py source/base_converter.py source/memory_store.py source/date_calculator.py source/mode_controllers.py tests/conftest.py tests/test_calculator.py tests/test_calculator_engine.py tests/test_base_converter.py tests/test_programmer_ui.py tests/test_memory_store.py tests/test_date_calculator.py tests/test_mode_controllers.py
git diff --check
```

Expected after PR-03 implementation:

- All existing 46 tests still pass.
- New Memory, Date, and controller tests pass.
- No Tkinter window is opened during automated tests.

Manual GUI smoke checklist must cover:

- Standard Mode arithmetic regression.
- Standard Mode memory keys.
- Programmer Mode PR-02.1 regression.
- Date Mode difference workflow.
- Date Mode add/subtract workflow.
- Switching modes without losing memory state or corrupting displays.

## 7. Risks and Mitigations

### Risk: `calculator.py` grows too large

Mitigation: Move routing/state logic into mode controllers while leaving Tk widget ownership in `CalculatorUI`.

### Risk: Date month/year arithmetic ambiguity

Mitigation: Specify deterministic clamp-to-last-day behavior and test leap-year/end-of-month cases.

### Risk: Memory recall semantics break Standard Mode state machine

Mitigation: Add targeted `CalculatorEngine` or `StandardModeController` tests for `MR` before/after operations and after result display.

### Risk: UI tests become brittle

Mitigation: Keep most tests headless against pure classes; use fake-widget smoke tests only for coordination rules.

### Risk: PR3 becomes too large

Mitigation: Implement in TDD slices: memory first, date core second, controller extraction third, UI integration last. Stop at MVP criteria.

## 8. Open Questions for 3AI Reviewers

1. Resolved: implement Memory/Date headless engines first, then perform the controller extraction during integration.
2. Resolved: Date Calculator MVP is ISO-date only, stdlib-only, with explicit month/year clamp rules.
3. Resolved: Memory Keys are Standard-only for PR-03.
4. Resolved: use one `source/mode_controllers.py` file for PR-03, with the option to split per mode in a later PR if file size grows.
5. For reviewers: does the revised plan preserve PR-02.1 stability enough to proceed into implementation?

## 9. Reviewer-Driven Clarifications Added After First 3AI Pass

The first planning review identified one blocking issue from Codex and several warnings from Claude/Gemini. The plan now resolves them as follows:

- `CalculatorEngine` extraction to `source/calculator_engine.py` is mandatory before controller extraction, not optional.
- `calculator.py` keeps a compatibility re-export for existing tests/imports.
- `CalculatorEngine.replace_current_input(text: str)` is required before `MR` wiring so controllers do not mutate private engine state.
- `MR` state-machine behavior is specified explicitly for waiting-first, waiting-second, result, and error states.
- `MemoryStore.has_value` is defined as a non-zero memory indicator, not proof that a store operation occurred.
- Duration subtraction uses `operation="add" | "subtract"`; the earlier `sign=-1` API sketch is retired.
- Date duration parsing must handle empty, whitespace, non-integer, decimal, and negative fields as specified.
- Date duration tests must include multi-component year/month/day ordering and month rollover beyond 12 months.
- `replace_current_input` tests must cover active second-operand replacement.
- Date Mode UI should use mode-specific frames and may resize the window when Date Mode is active.
