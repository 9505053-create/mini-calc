# MiniCalc PR-05 Implementation Plan

## Operating Rules

- Use TDD: write failing tests before production code.
- Keep Standard controller return type as display string.
- Use existing `pop_history_entry()` event-drain seam.
- Keep documenting every phase in `docs/pr5/PR5_DEVELOPMENT_HISTORY.md`.
- Do not merge to `main` without Scott approval.

## Phase 0 — Branch and baseline

1. Create `pr5-final-release` from PR-04 tip.
2. Push to GitHub before implementation.
3. Run baseline gate.

## Phase 1 — Standard chaining history TDD

1. Add tests for:
   - `1 + 2 +` records `1 + 2 = 3` and leaves next pending operator intact.
   - `1 + -` operator replacement records no history.
   - `5 ÷ 0 +` records controlled error history.
   - keyboard operator chaining follows the same event behavior.
2. Verify RED.
3. Implement minimal controller-side capture around `press_operator()`.
4. Verify targeted and full tests.

## Phase 2 — UI integration regression

1. Add or update fake-widget tests to ensure chaining history is consumed by the UI.
2. Verify RED/GREEN if UI changes are needed.
3. Keep history panel behavior unchanged otherwise.

## Phase 3 — Final release closure

1. Update README and release notes.
2. Update PR-04 caveat status and PR-05 acceptance docs.
3. Run full automated gate:
   - `python3 -m pytest -q`
   - `python3 -m py_compile ...`
   - `git diff --check`
4. Run Tkinter smoke using the best available environment and record exact command/output.
5. Build final review package.
6. Run 3AI implementation review and record verdicts.
7. Push GitHub backup.
