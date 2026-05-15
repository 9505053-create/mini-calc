# MiniCalc PR-04 Development History

Start time: 2026-05-15 14:11:55 +0800
Controller: Hermes
Branch: `pr4-planning`
Base: `pr3-planning` commit `a6c68e3 docs: resolve PR3 review package hygiene notes`

## Operating Policy

- Do not merge PR-02.1, PR-03, or PR-04 into `main` without Scott approval.
- PR-04 starts from the backed-up PR-03 branch tip so work remains traceable.
- Keep GitHub backups before implementation and after meaningful milestones.
- Keep this history updated with decisions, verification commands, review results, and commits.
- Use TDD for implementation after planning clears review.

## PR-03 carry-over

PR-03 local implementation status before PR-04:

- Branch `pr3-planning` pushed to GitHub at `a6c68e3`.
- Local automated gate passed: `python3 -m pytest -q` -> `94 passed`.
- Codex implementation hygiene re-review: `PASS_WITH_WARNINGS`, previous package blocker resolved.
- Gemini implementation/hygiene review: `PASS`.
- Claude implementation review retry remains scheduled due to Claude quota reset; this does not block PR-04 planning but must be recorded before any merge decision.
- Manual visible Tkinter GUI smoke remains a caveat until Scott/Hermes completes it in a GUI-capable environment.

## PR-04 scope decision

PRD remaining extra feature after PR-03:

- `計算歷史紀錄` / calculation history.

PR-04 will therefore focus on **Calculation History / Session Tape**:

- Standard Mode records completed arithmetic expressions and results.
- Date Mode records completed date calculations.
- Programmer Mode records base-switch conversions.
- History is session-only for PR-04; persistence/export is out of scope unless Scott later requests it.
- History must be headless-testable and must not move business logic into Tkinter callbacks.

## 2026-05-15 14:11 — PR-04 kickoff

Actions:

- Created branch `pr4-planning` from PR-03 tip `a6c68e3`.
- Baseline verification on the new branch:
  - `python3 -m pytest -q` -> `94 passed in 0.54s`.
- Started PR-04 planning docs under `docs/pr4/`.

Next:

1. Produce `PR4_SPEC.md`, `IMPLEMENTATION_PLAN.md`, and `ACCEPTANCE_CRITERIA.md`.
2. Commit and push `pr4-planning` to GitHub as pre-implementation backup.
3. Send PR-04 planning package to 3AI reviewers.
4. Only start PR-04 implementation after planning blockers are cleared.


## 2026-05-15 14:18 — PR-04 planning review patches

3AI planning review status:

- Codex: `PASS_WITH_WARNINGS`, no blocker.
- Gemini: `PASS`, recommended richer chaining history if low risk.
- Claude: initial process hung with no output and was killed; will retry later if needed.

Decision after review synthesis:

- Follow Codex's lower-risk recommendation for PR-04: record explicit `=` / keyboard Enter completions only; defer Standard immediate-execution chaining history to PR-05+.
- Record controlled Standard errors such as divide-by-zero with `status="error"`.
- Skip invalid Date inputs and Programmer no-op/failed/ignored inputs.
- Use a narrow `pop_history_entry()` history-event drain seam instead of broad `ModeResult` migration to preserve existing display-string controller APIs.
- Require Programmer same-base clicks to emit no history entry.
- Require scrollable/toggleable history UI and fake-widget clear-history test.
- Added `docs/pr4/PR4_SMOKE_CHECKLIST.md`.


## 2026-05-15 — PR-04 Task 1 HistoryStore TDD

RED:

- Added `tests/test_history_store.py` for empty store, immutable entry snapshots, clear, max-entry trimming, formatting, and invalid max-entry rejection.
- Verified RED: `python3 -m pytest tests/test_history_store.py -q` failed with `ModuleNotFoundError: No module named 'source.history_store'`.

GREEN:

- Added `source/history_store.py` with frozen `HistoryEntry` and bounded in-memory `HistoryStore`.
- Verification:
  - `python3 -m pytest tests/test_history_store.py -q` -> `7 passed`.
  - `python3 -m pytest -q` -> `101 passed`.
  - `python3 -m py_compile source/history_store.py tests/test_history_store.py` -> clean.
  - `git diff --check` -> clean.


## 2026-05-15 — PR-04 Task 2 Standard Mode history events

RED:

- Added controller tests for Standard `=` history, keyboard `Return` history, controlled divide-by-zero error history, and non-recorded digit/memory/chaining actions.
- Verified RED: `test_standard_controller_records_equals_history_entry` failed with `AttributeError: 'StandardModeController' object has no attribute 'pop_history_entry'`.

GREEN:

- Added a narrow `pop_history_entry()` drain seam to `StandardModeController` while preserving display-string return values.
- Captured Standard expression context before `press_equals()` so controlled errors like divide-by-zero can still record `5 ÷ 0 = Error`.
- Fixed an existing keyboard routing edge case discovered by the new test: empty `char` was matching `char in "+-*/"`; now operator-key routing requires a non-empty char.
- Verification:
  - `python3 -m pytest tests/test_mode_controllers.py -q` -> `19 passed`.
  - `python3 -m pytest -q` -> `105 passed`.
  - `python3 -m py_compile source/mode_controllers.py tests/test_mode_controllers.py` -> clean.
  - `git diff --check` -> clean.


## 2026-05-15 — PR-04 Task 3 Date Mode history events

RED:

- Added Date controller tests for difference history, duration add/subtract history, and invalid input no-history behavior.
- Verified RED: `test_date_controller_records_difference_history_entry` failed with `AttributeError: 'DateModeController' object has no attribute 'pop_history_entry'`.

GREEN:

- Added `pop_history_entry()` to `DateModeController`.
- Successful date difference now emits `HistoryEntry(mode="Date", expression="start → end", result="N days")`.
- Successful duration add/subtract now emits human-readable duration history.
- Invalid date/duration inputs reset/leave no pending history entry.
- Verification:
  - `python3 -m pytest tests/test_mode_controllers.py -q` -> `23 passed`.
  - `python3 -m pytest -q` -> `109 passed`.
  - `python3 -m py_compile source/mode_controllers.py tests/test_mode_controllers.py` -> clean.
  - `git diff --check` -> clean.
