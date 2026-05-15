# PR-02.1 Programmer Mode Hardening — Development History

Date: 2026-05-15
Controller: Hermes
Status: completed on branch `pr2.1-local-hardening`; branch pushed to GitHub for version control, main remains unchanged

## Background

PR-02 (`1a42b2d`) was reviewed by Claude Opus, Codex, and Gemini in:

`C:\Users\chien\_3AI_WorkSpace\code_reviews\minicalc_pr2_3ai_review_20260515_111847\`

3AI consensus was `PASS_WITH_WARNINGS`: no blocking PR-02 defect, but several small hardening items should be addressed before starting PR-03.

## Scope agreed for PR-02.1

This local patch intentionally stays small and does not start PR-03 work.

Implemented scope:

1. Make root-level `pytest -q` ignore stale permission-locked pytest cache folders.
2. Add `.gitignore` coverage for `pytest-cache-files-*/`.
3. Standardize `BaseConverter` imports in tests through `source.base_converter`.
4. Add lightweight Programmer Mode UI coordination tests without opening Tkinter.
5. Add unsigned 64-bit input limit for Programmer Mode conversion.
6. Rename visible Clear button from `C` to `AC` so it no longer conflicts with HEX digit `C`.
7. Tighten the weak negative-backspace regression assertion.
8. Document manual smoke checks for Programmer Mode.

Deferred intentionally:

- Full per-mode controller refactor. This is better done at the PR-03 boundary when the next mode is known.
- Full Tkinter GUI automation. Current tests exercise coordination logic without launching a window; manual smoke checklist covers visual behavior.
- Programmer signed/two's-complement support. PR-02/2.1 remains non-negative integer conversion only.

## TDD evidence

Failing tests were added before implementation and verified red:

- `test_append_digit_enforces_unsigned_64_bit_limit`
- `test_convert_rejects_values_beyond_unsigned_64_bit_limit`
- `test_programmer_mode_ac_button_clears_without_conflicting_with_hex_c`
- `test_programmer_mode_ignores_digits_beyond_64_bit_limit`

Initial targeted run showed 4 failures and 1 pass, confirming the tests captured missing behavior.

After implementation, targeted tests passed:

```text
5 passed in 0.21s
```

Full root verification after PR-02.1 implementation:

```text
python3 -m pytest -q
46 passed in 0.33s
```

## Files changed

- `.gitignore` — added `pytest-cache-files-*/`.
- `pytest.ini` — restricts pytest discovery to `tests/` and excludes stale cache/build folders.
- `source/base_converter.py` — added unsigned 64-bit range enforcement.
- `calculator.py` — renamed clear button label to `AC`; supports both `AC` and legacy internal `CLEAR` action.
- `tests/conftest.py` — centralizes project-root import setup.
- `tests/test_base_converter.py` — standardized import style and added 64-bit limit tests.
- `tests/test_calculator.py` — removed duplicated path bootstrapping and tightened negative backspace assertion.
- `tests/test_programmer_ui.py` — added lightweight UI coordination tests using fake widgets.
- `docs/programmer_mode_smoke_checklist.md` — manual PR-02.1 smoke checklist.
- `README.md` and `docs/release_notes.md` — updated PR-02.1 behavior and test notes.

## 3AI PR-02.1 review

3AI review package:

`C:\Users\chien\_3AI_WorkSpace\code_reviews\minicalc_pr2_1_3ai_review_20260515_114044\`

Results:

- Claude Opus: `PASS_WITH_WARNINGS`
- Codex: `PASS_WITH_WARNINGS`
- Gemini: `PASS`

Blocking issues: none.

Non-blocking notes:

- Include all new/untracked files in the final local commit before any later GitHub push.
- Manual GUI smoke checklist exists but should be executed visually before release/push.
- Per-mode controller refactor remains deferred until PR-03 planning.

## Local-only version-control policy

Per Scott's instruction, PR-02.1 was developed and verified on local disk first. After Hermes and 3AI Agent review agreed it was ready, the branch was pushed to GitHub for version control before any PR-03 work. `main` is still unchanged until Scott chooses merge/rebase strategy.
