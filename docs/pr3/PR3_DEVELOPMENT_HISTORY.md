# MiniCalc PR-03 Development History

Start time: 2026-05-15 12:27:25 +0800
Controller: Hermes
Branch: `pr3-planning`
Base: `pr2.1-local-hardening` commit `a6bcbe0`
Planning commit: `5cbe378 docs: add PR3 planning package`
Repository: `https://github.com/9505053-create/mini-calc`

## Ground Rules

- Do not merge PR-02.1 or PR-03 into `main` without Scott approval.
- Back up PR3 planning state to GitHub before implementation work begins.
- Use TDD: write failing tests before production code for new behavior.
- Keep a development history so Scott can track the sequence of decisions, verification commands, and commits.
- Preserve PR-02.1 stability: existing Standard Mode and Programmer Mode tests must stay green.
- After implementation, run 3AI implementation review before any merge discussion.

## Scope

PR-03 implementation targets:

1. Date Calculator mode.
2. Standard Mode Memory Keys.
3. Minimum necessary mode-controller architecture adjustment.

Out of scope:

- Merge to `main`.
- Persistent memory across app restarts.
- Timezone/time-of-day/business-day date logic.
- Programmer Mode signed/two's-complement arithmetic.
- Full MVC rewrite beyond the planned controller extraction.

## Planning Artifacts

- `docs/pr3/PR3_SPEC.md`
- `docs/pr3/IMPLEMENTATION_PLAN.md`
- `docs/pr3/ACCEPTANCE_CRITERIA.md`

3AI planning review summary:

- `C:\Users\chien\_3AI_WorkSpace\code_reviews\minicalc_pr3_planning_rereview_20260515_121727\FINAL_3AI_REVIEW_SUMMARY.md`

Planning review final verdict:

- Claude: `PASS_WITH_WARNINGS`
- Codex: `PASS_WITH_WARNINGS`
- Gemini: `PASS`
- Overall: `PASS_WITH_WARNINGS`, no blocking issue.

## Timeline

### 2026-05-15 12:27 — PR3 implementation kickoff

Scott approved moving PR3 forward, with explicit instruction to back up to GitHub before proceeding and to maintain a development history.

Initial state:

```text
branch: pr3-planning
latest commit: 5cbe378 docs: add PR3 planning package
main/origin-main: 1a42b2d PR-02
pr2.1-local-hardening: a6bcbe0 PR-02.1 hardening
working tree: clean
```

Next steps:

1. Commit this development history file.
2. Push `pr3-planning` to GitHub as pre-implementation backup.
3. Start Phase 1 with MemoryStore tests first.

## Verification Log

### Pre-backup status check

Command:

```bash
date '+%Y-%m-%d %H:%M:%S %z'
git status --short --branch
git log --oneline --max-count=5
git remote -v
```

Result:

```text
2026-05-15 12:27:25 +0800
## pr3-planning
5cbe378 docs: add PR3 planning package
a6bcbe0 fix: harden programmer mode before PR3
1a42b2d v1.2 — PR-02 Programmer Mode / Base Converter
90a63ce v1.0 — PR-01 顧問團通過，28 tests passed
origin https://github.com/9505053-create/mini-calc.git
```


### 2026-05-15 12:28 — Phase 1 MemoryStore headless core

TDD RED:

```bash
python3 -m pytest tests/test_memory_store.py -q
```

Expected failure observed:

```text
ModuleNotFoundError: No module named 'source.memory_store'
```

GREEN implementation:

- Created `source/memory_store.py`.
- Created `tests/test_memory_store.py`.
- Implemented `MemoryStore` with `recall`, `store`, `add`, `subtract`, `clear`, and non-zero `has_value` indicator semantics.

Verification:

```bash
python3 -m pytest tests/test_memory_store.py -q
python3 -m pytest -q
python3 -m py_compile source/memory_store.py tests/test_memory_store.py
git diff --check
```

Result:

```text
6 passed in 0.15s
52 passed in 0.37s
py_compile clean
git diff --check clean
```


### 2026-05-15 12:31 — Phase 2 DateCalculator headless core

TDD RED:

```bash
python3 -m pytest tests/test_date_calculator.py -q
```

Expected failure observed:

```text
ModuleNotFoundError: No module named 'source.date_calculator'
```

GREEN implementation:

- Created `source/date_calculator.py`.
- Created `tests/test_date_calculator.py`.
- Implemented ISO date parsing, day difference, add/subtract duration, year/month clamp, invalid duration validation, multi-component ordering, and >12-month rollover handling.

Verification:

```bash
python3 -m pytest tests/test_date_calculator.py -q
python3 -m pytest -q
python3 -m py_compile source/date_calculator.py tests/test_date_calculator.py
git diff --check
```

Result:

```text
20 passed in 0.19s
72 passed in 0.44s
py_compile clean
git diff --check clean
```


### 2026-05-15 12:35 — Phase 3.0 CalculatorEngine module boundary and Memory Recall API

Refactor boundary:

- Moved `CalculatorEngine` from root `calculator.py` to `source/calculator_engine.py`.
- Kept `calculator.py` compatibility import: `from source.calculator_engine import CalculatorEngine`.
- Verified existing PR-02.1 regression tests still pass after the move.

TDD RED for `replace_current_input`:

```bash
python3 -m pytest tests/test_calculator.py::TestReplaceCurrentInput -q
```

Expected failure observed:

```text
AttributeError: 'CalculatorEngine' object has no attribute 'replace_current_input'
```

GREEN implementation:

- Added `CalculatorEngine.replace_current_input(text: str) -> str`.
- Covered pending second operand, active second operand, result state, and error no-op behavior.

Verification:

```bash
python3 -m pytest tests/test_calculator.py::TestReplaceCurrentInput -q
python3 -m pytest tests/test_calculator.py tests/test_base_converter.py tests/test_programmer_ui.py -q
python3 -m pytest -q
python3 -m py_compile calculator.py source/calculator_engine.py tests/test_calculator.py
git diff --check
```

Result:

```text
4 passed in 0.16s
50 passed in 0.34s
76 passed in 0.45s
py_compile clean
git diff --check clean
```


### 2026-05-15 12:42 — Phase 3 controllers headless layer

TDD RED / GREEN sequence:

1. Standard controller memory tests first.
   - RED: `ModuleNotFoundError: No module named 'source.mode_controllers'`.
   - GREEN: implemented `StandardModeController`.
2. Programmer controller tests next.
   - RED: `ImportError: cannot import name 'ProgrammerModeController'`.
   - GREEN: implemented `ProgrammerModeController`.
3. Date controller tests next.
   - RED: `ImportError: cannot import name 'DateModeController'`.
   - GREEN: implemented `DateModeController`.

Implemented:

- `source/mode_controllers.py`
  - `StandardModeController`
  - `ProgrammerModeController`
  - `DateModeController`
- `tests/test_mode_controllers.py`

Coverage highlights:

- `MS`, `MR`, `M+`, `M-`, `MC`.
- `MR` preserves pending Standard operation.
- Memory store ignores `Error` display.
- Programmer HEX `C` digit vs `AC` clear.
- Programmer 64-bit overflow guard.
- Programmer base switching and button-state rules.
- Date difference singular/plural and negative formatting.
- Date invalid date / invalid duration controlled messages.
- Date duration add/subtract integration through controller.

Verification:

```bash
python3 -m pytest tests/test_mode_controllers.py -q
python3 -m pytest -q
python3 -m py_compile source/mode_controllers.py tests/test_mode_controllers.py
git diff --check
```

Result:

```text
15 passed in 0.18s
91 passed in 0.51s
py_compile clean
git diff --check clean
```

## Commit Log

_To be updated as PR-03 progresses._
