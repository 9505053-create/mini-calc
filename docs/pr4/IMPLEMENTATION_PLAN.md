# PR-04 Implementation Plan — Calculation History / Session Tape

> **For Hermes:** Use TDD and 3AI review gates. Do not merge PR-04 into `main` without Scott approval.

**Goal:** Add session-only calculation history for Standard, Date, and Programmer workflows.

**Architecture:** Add a headless `HistoryStore` and small history-event seam in mode/controller outputs. Keep Tkinter responsible for display only.

**Tech Stack:** Python 3, Tkinter, pytest, existing MiniCalc source layout.

---

## Gate 0 — Planning and backup

1. Confirm branch is `pr4-planning`.
2. Confirm base is PR-03 tip `a6c68e3`.
3. Run baseline:
   ```bash
   python3 -m pytest -q
   ```
4. Commit PR-04 planning docs.
5. Push `pr4-planning` to GitHub before implementation.
6. Send planning docs to 3AI review.
7. Resolve planning blockers before production code.

## Task 1 — HistoryStore TDD

**Objective:** Create a headless session history store.

**Files:**

- Create: `source/history_store.py`
- Create: `tests/test_history_store.py`

**Step 1: RED tests**

Required tests:

```python
def test_history_starts_empty(): ...
def test_add_entry_returns_immutable_snapshot(): ...
def test_clear_removes_entries(): ...
def test_max_entries_keeps_newest_entries(): ...
def test_formatted_lines_include_mode_expression_result(): ...
def test_invalid_max_entries_rejected(): ...
```

Run:

```bash
python3 -m pytest tests/test_history_store.py -q
```

Expected: fail because `source.history_store` does not exist.

**Step 2: GREEN implementation**

Implement:

- `HistoryEntry` frozen dataclass.
- `HistoryStore(max_entries=100)`.
- `add()`, `clear()`, `entries()`, `formatted_lines()`.
- Reject `max_entries < 1`.

**Step 3: Verification**

```bash
python3 -m pytest tests/test_history_store.py -q
python3 -m pytest -q
python3 -m py_compile source/history_store.py tests/test_history_store.py
git diff --check
```

Commit:

```bash
git add source/history_store.py tests/test_history_store.py docs/pr4/PR4_DEVELOPMENT_HISTORY.md
git commit -m "feat: add history store core"
```

## Task 2 — Standard Mode history events

**Objective:** Emit history events when Standard Mode completes calculations.

**Files:**

- Modify: `source/mode_controllers.py`
- Modify: `tests/test_mode_controllers.py` or create `tests/test_history_integration.py`

**Design preference:**

Do not make the UI inspect private `CalculatorEngine` fields after the operation. Add a minimal public seam in `StandardModeController` such as:

```python
@dataclass(frozen=True)
class ModeResult:
    display: str
    history_entry: HistoryEntry | None = None
```

If returning `ModeResult` from every controller is too broad, use a smaller `last_history_entry` property with tests.

**Required behavior:**

- `2 + 3 =` emits `Standard: 2 + 3 = 5`.
- Digit-only input emits no entry.
- `5 ÷ 0 =` emits either `Standard: 5 ÷ 0 = Error` or no entry; choose one and document it. Preferred: record controlled error result.
- `MR`, `MC`, `MS`, `M+`, `M-` do not create arithmetic history entries unless a calculation completes.

**Verification:**

```bash
python3 -m pytest tests/test_mode_controllers.py -q
python3 -m pytest -q
git diff --check
```

Commit:

```bash
git add source/mode_controllers.py tests/test_mode_controllers.py docs/pr4/PR4_DEVELOPMENT_HISTORY.md
git commit -m "feat: record standard calculation history"
```

## Task 3 — Date Mode history events

**Objective:** Emit history entries for successful Date Mode calculations.

**Files:**

- Modify: `source/mode_controllers.py`
- Modify: `tests/test_mode_controllers.py` or `tests/test_history_integration.py`

Required behavior:

- Difference: `2026-05-15 → 2026-05-20 = 5 days`.
- Duration add: `2026-01-31 + 1 month = 2026-02-28`.
- Duration subtract: `2026-03-31 - 1 month = 2026-02-28`.
- Invalid date/duration emits no successful history entry and returns controlled error display.

Verification:

```bash
python3 -m pytest tests/test_mode_controllers.py tests/test_date_calculator.py -q
python3 -m pytest -q
git diff --check
```

Commit:

```bash
git add source/mode_controllers.py tests/test_mode_controllers.py docs/pr4/PR4_DEVELOPMENT_HISTORY.md
git commit -m "feat: record date calculation history"
```

## Task 4 — Programmer Mode conversion history

**Objective:** Emit history entries for base-switch conversions only.

**Files:**

- Modify: `source/mode_controllers.py`
- Modify: `tests/test_mode_controllers.py`

Required behavior:

- DEC `255` switch to HEX emits `DEC 255 → HEX FF`.
- HEX `FF` switch to BIN emits `HEX FF → BIN 11111111`.
- Digit append/backspace emits no history entry.
- Invalid ignored input emits no history entry.
- Failed conversion leaves prior state unchanged and emits no history entry.

Verification:

```bash
python3 -m pytest tests/test_mode_controllers.py tests/test_base_converter.py -q
python3 -m pytest -q
git diff --check
```

Commit:

```bash
git add source/mode_controllers.py tests/test_mode_controllers.py docs/pr4/PR4_DEVELOPMENT_HISTORY.md
git commit -m "feat: record programmer conversion history"
```

## Task 5 — Tkinter History UI integration

**Objective:** Display and clear session history in the GUI.

**Files:**

- Modify: `calculator.py`
- Modify: `tests/test_programmer_ui.py` or create `tests/test_history_ui.py`
- Update: `docs/pr4/PR4_SMOKE_CHECKLIST.md`

Required UI:

- A compact History panel/list or text widget.
- Clear History button.
- Standard/Date/Programmer completed events append visible lines.
- Clear History clears store and UI.
- Layout remains usable in all modes.

Testing strategy:

- Use fake-widget tests similar to existing `tests/test_programmer_ui.py`.
- Do not require a real Tk display for automated tests.
- Manual smoke checklist covers the real GUI.

Verification:

```bash
python3 -m pytest tests/test_programmer_ui.py -q
python3 -m pytest -q
python3 -m py_compile calculator.py source/history_store.py source/mode_controllers.py tests/test_programmer_ui.py
git diff --check
```

Commit:

```bash
git add calculator.py tests/test_programmer_ui.py docs/pr4/PR4_SMOKE_CHECKLIST.md docs/pr4/PR4_DEVELOPMENT_HISTORY.md
git commit -m "feat: integrate history panel UI"
```

## Task 6 — Documentation and release gate

**Objective:** Finish user/developer docs and prepare 3AI implementation review.

Files:

- Modify: `README.md`
- Modify: `docs/release_notes.md`
- Update: `docs/pr4/ACCEPTANCE_CRITERIA.md`
- Update: `docs/pr4/PR4_DEVELOPMENT_HISTORY.md`

Final gate:

```bash
python3 -m pytest -q && \
python3 -m py_compile calculator.py source/calculator_engine.py source/base_converter.py source/memory_store.py source/date_calculator.py source/mode_controllers.py source/history_store.py tests/conftest.py tests/test_calculator.py tests/test_base_converter.py tests/test_programmer_ui.py tests/test_memory_store.py tests/test_date_calculator.py tests/test_mode_controllers.py tests/test_history_store.py && \
git diff --check
```

Expected:

- All tests pass.
- Compile clean.
- Diff check clean.

Commit and push:

```bash
git add README.md docs/release_notes.md docs/pr4/
git commit -m "docs: update PR4 release documentation"
git push origin pr4-planning
```

## Task 7 — 3AI implementation review

Build review packages from `git ls-files` only.

Review focus:

- Claude: architecture, UX, maintainability.
- Codex: code correctness, tests, edge cases.
- Gemini: product coherence, roadmap, release readiness.

Do not merge after review. Report verdicts to Scott first.
