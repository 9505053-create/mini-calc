# MiniCalc PR-05 Spec — Final Release Hardening

## Goal

PR-05 is the final release-hardening phase for MiniCalc v1.0. It closes the PR-04 merge caveats and finishes the one deferred low-risk history behavior from PR-04.

## Scope

1. Standard Mode chaining history
   - Record immediate-execution chaining calculations when a second operator completes a pending operation.
   - Example: `1 + 2 +` displays `3` and records `1 + 2 = 3`.
   - Continue to record explicit `=` / keyboard Enter completions.
   - Controlled errors from chaining, such as `5 ÷ 0 +`, record `5 ÷ 0 = Error` with `status="error"`.
   - Operator replacement without a second operand, such as `1 + -`, must not record history.

2. Final verification closure
   - Run complete automated gates.
   - Run Tkinter smoke in an available GUI-capable or headless-display environment and record evidence.
   - Run final 3AI implementation review covering PR-04 + PR-05 cumulative release state.
   - Update release notes, acceptance criteria, and development history.

## Non-goals

- Do not merge `main` without Scott approval.
- Do not add persistence, export/import, search, or click-to-restore history.
- Do not redesign the controller API; keep the narrow `pop_history_entry()` event seam.
- Do not broaden Programmer Mode beyond conversion-only semantics.

## Acceptance Summary

PR-05 is complete when:

- Chaining history has test-first coverage and implementation.
- No PR-04 caveat remains unrecorded: final review and Tkinter smoke evidence are documented.
- `pytest`, `py_compile`, and `git diff --check` pass.
- GitHub branch `pr5-final-release` is pushed.
