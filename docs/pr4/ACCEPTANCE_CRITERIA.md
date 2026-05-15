# PR-04 Acceptance Criteria — Calculation History / Session Tape

Date: 2026-05-15
Branch: `pr4-planning`
Status: Planning draft for 3AI review

## Release gate

PR-04 is not ready until all of the following are true:

- PR-04 planning docs are reviewed by 3AI and all blockers are resolved.
- Implementation follows TDD with RED/GREEN evidence recorded in `PR4_DEVELOPMENT_HISTORY.md`.
- Branch is pushed to GitHub before 3AI implementation review.
- Automated gate passes:

```bash
python3 -m pytest -q && \
python3 -m py_compile calculator.py source/calculator_engine.py source/base_converter.py source/memory_store.py source/date_calculator.py source/mode_controllers.py source/history_store.py tests/conftest.py tests/test_calculator.py tests/test_base_converter.py tests/test_programmer_ui.py tests/test_memory_store.py tests/test_date_calculator.py tests/test_mode_controllers.py tests/test_history_store.py && \
git diff --check
```

- No PR-04 merge into `main` without Scott approval.

## Functional criteria

### History store

- Starts empty.
- Adds immutable entries.
- Returns immutable snapshots.
- Clears all entries.
- Enforces configurable max-entry cap and keeps newest entries.
- Formats entries consistently for UI display.
- Rejects invalid `max_entries` values.
- Has no Tkinter imports and no filesystem persistence.

### Standard Mode history

- Completed arithmetic calculation records one history entry.
- Entry includes mode, expression, result, and status.
- Digit-only input does not create entries.
- Clear / backspace / sign toggle alone does not create entries.
- Memory keys do not create arithmetic history entries unless they participate in a completed calculation via displayed input.
- Divide-by-zero creates a controlled history entry or is explicitly skipped; the chosen behavior must be documented and tested.

Preferred behavior:

- Record controlled errors: `5 ÷ 0 = Error` with `status="error"`.

### Date Mode history

- Successful date difference records one entry.
- Successful date duration add/subtract records one entry.
- Entries include inputs and result in human-readable text.
- Invalid date/duration input returns controlled UI error and does not add a successful history entry.

### Programmer Mode history

- Base-switch conversion records one entry.
- Entry includes from-base, input value, to-base, converted value.
- Digit append/backspace does not create entries.
- Invalid ignored input does not create entries.
- Failed conversion does not mutate history.

### UI criteria

- History panel/list is visible or clearly toggleable.
- History lines update after completed Standard, Date, and Programmer events.
- `Clear History` clears both store and visible UI.
- Layout remains usable in Standard, Programmer, and Date modes.
- Existing display and mode controls still work.
- UI automated tests remain headless; real Tkinter launch is manual smoke only.

## Regression criteria

PR-04 must preserve PR-03 behavior:

- Standard arithmetic and memory keys still work.
- Date Calculator still handles leap-year/month-end/duration edge cases.
- Programmer Mode still preserves 64-bit unsigned cap and HEX `C` vs `AC` behavior.
- Existing 94 PR-03 tests continue to pass plus new PR-04 tests.

## Documentation criteria

- `README.md` documents history behavior and session-only limitation.
- `docs/release_notes.md` includes PR-04 section.
- `docs/pr4/PR4_DEVELOPMENT_HISTORY.md` records decisions, tests, commits, and review results.
- `docs/pr4/PR4_SMOKE_CHECKLIST.md` covers manual GUI history checks.

## 3AI review criteria

Planning review should answer:

- Whether recording only `=` for Standard Mode is acceptable or if chaining must be recorded in PR-04.
- Whether controlled error results should be recorded.
- Whether `ModeResult` / history-event seam is appropriately minimal.
- Whether history UI scope is too broad for PR-04.

Implementation review should return:

- Claude: architecture / UX / maintainability verdict.
- Codex: tests / edge cases / correctness verdict.
- Gemini: roadmap / release-readiness verdict.

No merge decision until review verdicts are reported to Scott.
