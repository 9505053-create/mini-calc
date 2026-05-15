# MiniCalc PR-03 Acceptance Criteria

Date: 2026-05-15
Scope: Date Calculator, Standard Mode Memory Keys, minimum mode-controller architecture
Status: Planning draft for 3AI review

## 1. Release Gate Summary

PR-03 is acceptable only when all of the following are true:

1. Date Calculator mode works for date difference and add/subtract duration workflows.
2. Memory Keys work in Standard Mode.
3. Mode-controller extraction prevents Date/Programmer/Standard routing from being concentrated in one large `CalculatorUI` method set.
4. All existing PR-02.1 behavior remains intact.
5. Automated tests, compile checks, and diff checks pass.
6. 3AI reviewer pass has no blocking issue.
7. Scott approves merge or PR strategy; no automatic merge to `main`.

## 2. Date Calculator Acceptance Criteria

### 2.1 Difference Workflow

Given Date Mode is active, when the user enters a start date and end date in ISO `YYYY-MM-DD`, MiniCalc displays the day difference as `end_date - start_date`.

Required examples:

- Start `2026-05-15`, end `2026-05-16` → display contains `1 day`.
- Start `2026-05-15`, end `2026-05-15` → display contains `0 days`.
- Start `2026-05-16`, end `2026-05-15` → display contains `-1 day`.
- Start `2024-02-28`, end `2024-03-01` → display contains `2 days`.

Pass conditions:

- Headless `DateCalculator.days_between()` tests pass.
- Date Mode controller formats singular/plural day text correctly.
- Invalid date input is handled as a controlled error.

Fail conditions:

- Leap year day difference is wrong.
- End-before-start crashes or is disallowed without a spec change.
- Invalid date raises an uncaught Tkinter traceback.

### 2.2 Add/Subtract Duration Workflow

Given Date Mode is active, when the user enters a base date, operation, and duration components, MiniCalc applies duration in this order:

1. Years
2. Months
3. Weeks/days

Required examples:

- `2026-05-15 + 10 days` → `2026-05-25`
- `2026-05-15 - 2 weeks` → `2026-05-01`
- `2024-01-31 + 1 month` → `2024-02-29`
- `2025-01-31 + 1 month` → `2025-02-28`
- `2024-02-29 + 1 year` → `2025-02-28`

Pass conditions:

- Month-end clamping is deterministic and covered by tests.
- Empty and whitespace-only duration fields are treated as zero.
- Non-integer, decimal, and negative duration component strings produce controlled validation errors.
- Subtracting months/years across month-end and leap-day boundaries is covered by tests.
- Multi-component ordering and month rollover beyond 12 months are covered by tests.
- ISO output format is `YYYY-MM-DD`.

Fail conditions:

- Month-end cases crash.
- Leap-day year addition is wrong.
- UI silently returns an old result after invalid input without an error indication.

## 3. Memory Keys Acceptance Criteria

Memory Keys are PR-03 Standard Mode features.

### 3.1 Key Behavior

- `MC`: clears memory to `0`; memory indicator becomes inactive if implemented.
- `MR`: recalls memory into Standard Mode input/display using `CalculatorEngine.replace_current_input(text)`; controllers must not mutate engine private fields directly.
- `MS`: stores the current Standard Mode display value.
- `M+`: adds current Standard Mode display value to memory.
- `M-`: subtracts current Standard Mode display value from memory.

Required examples:

- Start app → `MR` displays/loads `0`.
- Press `1`, `2`, `MS`, `AC`, `MR` → display `12`.
- Store `10`, then display `2`, press `M+`, `MR` → display `12`.
- Store `10`, then display `3`, press `M-`, `MR` → display `7`.
- Display `Error`, press `MS` → memory remains unchanged.

Pass conditions:

- Memory uses `Decimal` internally.
- Memory survives mode switching during one app session.
- A minimal `M` memory indicator is present when memory is non-zero, or documentation explicitly states that no visual indicator exists in PR-03.
- Memory commands do not break existing Standard Mode operations.
- During a pending operation such as `5 +`, `MR` replaces/fills the second operand and preserves the pending operator.
- After a result display, `MR` starts a new first operand and clears pending operation.
- In `Error` state, `MR` is a no-op until `AC`.
- Memory buttons are disabled or ignored in Programmer/Date Mode for PR-03.

Fail conditions:

- Memory accepts `Error` as a stored value.
- Memory precision introduces float artifacts.
- `MR` corrupts pending Standard Mode operations without documented/test-covered behavior.

## 4. Mode-Controller Architecture Acceptance Criteria

PR-03 must reduce `CalculatorUI` responsibility enough to support three modes safely.

Pass conditions:

- `CalculatorEngine` has been moved to `source/calculator_engine.py`, with compatibility re-export from `calculator.py`, before controller extraction.
- There is a headless controller or equivalent class for each mode:
  - Standard
  - Programmer
  - Date
- Tkinter widget creation remains in `CalculatorUI`.
- Controller logic is testable without launching Tk.
- Programmer Mode state (`current_base`, `programmer_value`) is not scattered across multiple unrelated UI methods after refactor.
- Date Mode calculation logic is not embedded directly in Tkinter callbacks.
- Standard Mode arithmetic remains delegated to `CalculatorEngine`.

Acceptable compromise:

- `CalculatorUI` may still own widget layout and button enable/disable application.
- Controller extraction can be in one file, `source/mode_controllers.py`, for PR-03.
- Full MVC / per-widget component framework is not required.

Fail conditions:

- `source/mode_controllers.py` imports `CalculatorEngine` from root `calculator.py`, creating or risking a circular import.
- Date logic is implemented directly inside button callbacks with no headless tests.
- Programmer Mode regressions appear after moving logic.
- `CalculatorUI` becomes significantly harder to test than PR-02.1.

## 5. Regression Acceptance Criteria

Existing behavior must remain stable.

Required existing tests:

```bash
python3 -m pytest tests/test_calculator.py tests/test_base_converter.py tests/test_programmer_ui.py -q
```

Expected:

- All existing PR-02.1 tests pass.

Required behavioral checks:

- Standard Mode basic arithmetic still works.
- Decimal, percent, sign toggle, backspace, divide-by-zero, scientific notation behavior remain unchanged.
- Programmer Mode still supports DEC/HEX/BIN/OCT.
- HEX `C` is a digit; `AC` clears.
- 64-bit unsigned cap still blocks overflow input.
- Root-level `python3 -m pytest -q` does not discover stale pytest cache directories.

## 6. Automated Verification Gate

Before PR-03 is considered ready for final 3AI implementation review, run:

```bash
python3 -m pytest -q && \
python3 -m py_compile calculator.py source/calculator_engine.py source/base_converter.py source/memory_store.py source/date_calculator.py source/mode_controllers.py tests/conftest.py tests/test_calculator.py tests/test_calculator_engine.py tests/test_base_converter.py tests/test_programmer_ui.py tests/test_memory_store.py tests/test_date_calculator.py tests/test_mode_controllers.py && \
git diff --check
```

Pass criteria:

- `pytest` exits 0.
- `py_compile` exits 0.
- `git diff --check` exits 0.

## 7. Manual GUI Smoke Acceptance Criteria

A human or GUI-capable Hermes session should verify:

### Standard Mode

- `2 + 3 =` shows `5`.
- `100 + 10 %` shows `110`.
- Divide by zero shows controlled `Error`, then `AC` recovers.
- Memory buttons perform `MS`, `MR`, `M+`, `M-`, `MC` as specified.

### Programmer Mode

- Switching to Programmer starts in DEC.
- HEX accepts `A-F`; `C` appends as digit.
- `AC` clears.
- BIN disables/ignores `2-9` and `A-F`.
- `FFFFFFFFFFFFFFFF` cannot be extended beyond 64-bit unsigned max.

### Date Mode

- Difference workflow: `2026-05-15` to `2026-05-16` shows `1 day`.
- Add/subtract workflow: `2024-01-31 + 1 month` shows `2024-02-29`.
- Invalid date such as `2026-02-30` shows controlled invalid-date message.
- Invalid duration component such as `abc` shows a controlled validation message.
- Switching away and back does not crash.

## 8. Documentation Acceptance Criteria

PR-03 docs must include:

- README update listing Date Calculator and Memory Keys.
- Release notes section for PR-03.
- Date Calculator smoke checklist.
- Known limits:
  - Date Mode uses ISO date input.
  - No time zones/time-of-day/business days.
  - Memory is session-only.
  - Memory Keys are Standard Mode only in PR-03.

## 9. 3AI Reviewer Acceptance Criteria

Planning review must happen before implementation.

Implementation review must happen after code and tests are complete.

Required reviewer roles:

- Claude: architecture, maintainability, UI/UX, controller boundaries.
- Codex: code correctness, tests, edge cases, regression risk.
- Gemini: product coherence, roadmap fit, final risk summary.

PR-03 can proceed from planning to implementation only when:

- Planning review has no blocking issue, or blocking issues have been fixed.

PR-03 can proceed from implementation to merge discussion only when:

- Implementation review has no blocking issue, or blocking issues have been fixed.
- Scott explicitly approves the merge/PR strategy.

## 10. Explicit Non-Acceptance Items

PR-03 is not accepted if any of these happen:

- `main` is merged or rewritten without Scott approval.
- PR-02.1 Programmer Mode behavior regresses.
- Automated tests require a visible Tkinter display.
- Dynamic code execution is introduced.
- Date calculations depend on non-stdlib packages without a separate decision.
- Memory uses binary float internally.

## 11. First 3AI Planning Review Fixes Required Before Implementation

The first 3AI planning review produced these resolved gating criteria:

- Codex's circular-import blocker is resolved by making `source/calculator_engine.py` extraction mandatory before controllers.
- Claude's `MR` state-machine ambiguity is resolved by specifying `replace_current_input(text)` behavior.
- Claude's `MemoryStore.has_value` ambiguity is resolved: it means non-zero memory indicator.
- Claude/Codex date-duration concerns are resolved with explicit invalid-duration, subtract clamp, multi-component ordering, and >12-month rollover acceptance tests.
- Claude's active-second-operand `MR` gap is resolved with an explicit `replace_current_input` test requirement.
- Gemini's UI-space warning is resolved by requiring separate mode frames and allowing Date Mode window resizing.
