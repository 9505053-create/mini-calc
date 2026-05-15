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
