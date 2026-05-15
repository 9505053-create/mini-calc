# MiniCalc PR-03 Implementation Plan

> For Hermes: implement this plan with TDD and 3AI review gates. Do not merge PR-02.1 or PR-03 into `main` without Scott approval.

Goal: Add Date Calculator, Standard Mode Memory Keys, and the minimum mode-controller architecture needed to keep MiniCalc maintainable.

Architecture: Keep Tkinter ownership in `CalculatorUI`; move mode-specific command routing and state into headless controllers. Add pure `MemoryStore` and `DateCalculator` modules with unit tests before UI integration.

Tech Stack: Python 3, Tkinter, `datetime`, `calendar`, `decimal.Decimal`, pytest.

---

## Phase 0 — Planning and Review Gate

### Task 0.1: Keep PR3 work isolated from main

Objective: Ensure PR3 planning and implementation happen on a branch based on PR-02.1 without merging to `main`.

Files:

- No source file changes.

Steps:

1. Confirm current branch is `pr3-planning` or a later PR3 branch.
2. Confirm `origin/main` remains at PR-02 until Scott decides otherwise.
3. Confirm PR-02.1 branch exists remotely for version control.
4. Confirm existing `tests/conftest.py` is present from PR-02.1 and keeps root/source imports stable.

Verification:

```bash
git status --short --branch
git rev-parse origin/main
git rev-parse origin/pr2.1-local-hardening
```

Expected:

- Working tree clean before implementation.
- `origin/main` is still the PR-02 commit unless Scott has separately approved a merge.

### Task 0.2: 3AI planning review

Objective: Have Claude/Codex/Gemini review PR3 planning docs before coding.

Files:

- Review: `docs/pr3/PR3_SPEC.md`
- Review: `docs/pr3/IMPLEMENTATION_PLAN.md`
- Review: `docs/pr3/ACCEPTANCE_CRITERIA.md`

Verification:

- All three reviewers produce Markdown reports.
- Hermes produces a final summary with blockers/non-blockers.
- Implementation starts only if there are no blocking planning issues, or after blockers are fixed.

---

## Phase 1 — Memory Keys Headless Core

### Task 1.1: Create `MemoryStore` tests

Objective: Define memory behavior before implementation.

Files:

- Create: `tests/test_memory_store.py`
- Create later: `source/memory_store.py`

Test cases:

```python
from decimal import Decimal

from source.memory_store import MemoryStore


def test_memory_starts_at_zero():
    memory = MemoryStore()
    assert memory.recall() == Decimal("0")
    assert not memory.has_value


def test_store_replaces_memory():
    memory = MemoryStore()
    memory.store(Decimal("12.5"))
    assert memory.recall() == Decimal("12.5")
    assert memory.has_value


def test_memory_add_and_subtract():
    memory = MemoryStore()
    memory.store(Decimal("10"))
    memory.add(Decimal("2.5"))
    memory.subtract(Decimal("4"))
    assert memory.recall() == Decimal("8.5")


def test_add_from_default_zero_memory():
    memory = MemoryStore()
    memory.add(Decimal("5"))
    assert memory.recall() == Decimal("5")
    assert memory.has_value


def test_store_zero_recalls_zero_but_indicator_is_inactive():
    memory = MemoryStore()
    memory.store(Decimal("0"))
    assert memory.recall() == Decimal("0")
    assert not memory.has_value


def test_clear_resets_memory():
    memory = MemoryStore()
    memory.store(Decimal("99"))
    memory.clear()
    assert memory.recall() == Decimal("0")
    assert not memory.has_value
```

Run:

```bash
python3 -m pytest tests/test_memory_store.py -q
```

Expected before implementation: fail because module does not exist.

### Task 1.2: Implement `MemoryStore`

Objective: Add a small pure memory service.

Files:

- Create: `source/memory_store.py`

Implementation sketch:

```python
from __future__ import annotations

from decimal import Decimal


class MemoryStore:
    def __init__(self) -> None:
        self._value = Decimal("0")
        self._has_value = False

    @property
    def has_value(self) -> bool:
        return self._has_value

    def recall(self) -> Decimal:
        return self._value

    def store(self, value: Decimal) -> None:
        self._value = value
        self._has_value = value != 0  # non-zero memory indicator semantics

    def add(self, value: Decimal) -> None:
        self.store(self._value + value)

    def subtract(self, value: Decimal) -> None:
        self.store(self._value - value)

    def clear(self) -> None:
        self._value = Decimal("0")
        self._has_value = False
```

Run:

```bash
python3 -m pytest tests/test_memory_store.py -q
```

Expected: pass.

---

## Phase 2 — Date Calculator Headless Core

### Task 2.1: Create date difference tests

Objective: Lock down date difference semantics.

Files:

- Create/modify: `tests/test_date_calculator.py`
- Create later: `source/date_calculator.py`

Test cases:

```python
import pytest

from source.date_calculator import DateCalculator


def test_days_between_adjacent_dates():
    calc = DateCalculator()
    assert calc.days_between("2026-05-15", "2026-05-16") == 1


def test_days_between_same_date_is_zero():
    calc = DateCalculator()
    assert calc.days_between("2026-05-15", "2026-05-15") == 0


def test_days_between_allows_negative_result():
    calc = DateCalculator()
    assert calc.days_between("2026-05-16", "2026-05-15") == -1


def test_days_between_leap_year_boundary():
    calc = DateCalculator()
    assert calc.days_between("2024-02-28", "2024-03-01") == 2


def test_invalid_date_raises_value_error():
    calc = DateCalculator()
    with pytest.raises(ValueError):
        calc.days_between("2026-02-30", "2026-03-01")
```

Run:

```bash
python3 -m pytest tests/test_date_calculator.py -q
```

Expected before implementation: fail because module does not exist.

### Task 2.2: Implement date parsing and difference

Objective: Add ISO date parsing and day difference.

Files:

- Create: `source/date_calculator.py`

Implementation sketch:

```python
from __future__ import annotations

from datetime import date


class DateCalculator:
    def parse_date(self, text: str) -> date:
        try:
            return date.fromisoformat(str(text).strip())
        except ValueError as exc:
            raise ValueError("invalid ISO date; expected YYYY-MM-DD") from exc

    def days_between(self, start: str, end: str) -> int:
        start_date = self.parse_date(start)
        end_date = self.parse_date(end)
        return (end_date - start_date).days
```

Run:

```bash
python3 -m pytest tests/test_date_calculator.py -q
```

Expected: date difference tests pass.

### Task 2.3: Create add/subtract duration tests

Objective: Lock down duration semantics, especially leap-year and month-end clamping.

Files:

- Modify: `tests/test_date_calculator.py`

Test cases:

```python
def test_add_days():
    calc = DateCalculator()
    assert calc.add_duration("2026-05-15", days=10) == "2026-05-25"


def test_subtract_weeks():
    calc = DateCalculator()
    assert calc.add_duration("2026-05-15", weeks=2, operation="subtract") == "2026-05-01"


def test_subtract_month_clamps_end_of_month():
    calc = DateCalculator()
    assert calc.add_duration("2024-03-31", months=1, operation="subtract") == "2024-02-29"


def test_subtract_year_from_leap_day_clamps():
    calc = DateCalculator()
    assert calc.add_duration("2024-02-29", years=1, operation="subtract") == "2023-02-28"


def test_add_month_clamps_leap_year_february():
    calc = DateCalculator()
    assert calc.add_duration("2024-01-31", months=1) == "2024-02-29"


def test_add_month_clamps_non_leap_february():
    calc = DateCalculator()
    assert calc.add_duration("2025-01-31", months=1) == "2025-02-28"


def test_add_year_from_leap_day_clamps():
    calc = DateCalculator()
    assert calc.add_duration("2024-02-29", years=1) == "2025-02-28"


def test_multi_component_duration_applies_years_months_then_days():
    calc = DateCalculator()
    assert calc.add_duration("2024-01-31", years=1, months=1, days=5) == "2025-03-05"


def test_month_rollover_beyond_one_year():
    calc = DateCalculator()
    assert calc.add_duration("2024-01-31", months=13) == "2025-02-28"
```

Run targeted tests.

Expected before implementation: fail because `add_duration` does not exist.

### Task 2.4: Implement add/subtract duration

Objective: Add deterministic year/month/week/day date arithmetic.

Files:

- Modify: `source/date_calculator.py`

Implementation notes:

- Use `calendar.monthrange(year, month)[1]` for last day.
- Apply years, then months, then week/day delta.
- Use `datetime.timedelta` for days.
- Use `operation="add" | "subtract"`; reject other operation values with `ValueError`.
- Return ISO string.

Run:

```bash
python3 -m pytest tests/test_date_calculator.py -q
```

Expected: pass.

---

## Phase 3 — CalculatorEngine Boundary and Mode Controller Extraction

### Task 3.0: Move `CalculatorEngine` to `source/calculator_engine.py`

Objective: Remove the circular import risk before mode controllers import the Standard engine.

Files:

- Create: `source/calculator_engine.py`
- Modify: `calculator.py`
- Create: `tests/test_calculator_engine.py` only if extra tests are useful; existing `tests/test_calculator.py` must keep importing `CalculatorEngine` from `calculator.py`.

Steps:

1. Move the existing `CalculatorEngine` class unchanged from `calculator.py` into `source/calculator_engine.py`.
2. In `calculator.py`, add `from source.calculator_engine import CalculatorEngine` as a compatibility re-export.
3. Keep `CalculatorUI` in `calculator.py`.
4. Run the existing regression tests before any behavior change.

Run:

```bash
python3 -m pytest tests/test_calculator.py tests/test_base_converter.py tests/test_programmer_ui.py -q
```

Expected: all existing PR-02.1 tests pass.

### Task 3.0b: Add public current-input replacement API for Memory Recall

Objective: Provide a tested public method for `MR` without direct controller mutation of engine internals.

Files:

- Modify: `source/calculator_engine.py`
- Test: `tests/test_calculator.py` or `tests/test_calculator_engine.py`

Required behavior for `replace_current_input(text: str) -> str`:

- Validate/normalize the provided Decimal-compatible text through existing formatting rules.
- `WAITING_FIRST`: replace current input/display.
- `WAITING_SECOND` with no current second operand: set second operand and preserve pending operator.
- `WAITING_SECOND` with active second operand: replace active second operand.
- `RESULT`: start a new first operand and clear pending operation.
- `ERROR`: no-op until `AC`.

Concrete tests:

```python
def test_replace_current_input_preserves_pending_operator_for_second_operand():
    engine = CalculatorEngine()
    engine.press_digit("5")
    engine.press_operator("+")
    assert engine.replace_current_input("12") == "12"
    assert engine.press_equals() == "17"


def test_replace_current_input_replaces_active_second_operand():
    engine = CalculatorEngine()
    engine.press_digit("5")
    engine.press_operator("+")
    engine.press_digit("3")
    assert engine.replace_current_input("12") == "12"
    assert engine.press_equals() == "17"


def test_replace_current_input_after_result_starts_new_input():
    engine = CalculatorEngine()
    press_sequence(engine, ["2", "+", "3", "="])
    assert engine.replace_current_input("12") == "12"
    assert engine.press_operator("+") == "12"


def test_replace_current_input_after_error_is_noop():
    engine = CalculatorEngine()
    press_sequence(engine, ["5", "/", "0", "="])
    assert engine.replace_current_input("12") == "Error"
```


### Task 3.1: Define controller tests for Standard memory commands

Objective: Verify memory commands without opening Tk.

Files:

- Create: `tests/test_mode_controllers.py`
- Create later: `source/mode_controllers.py`

Required tests:

- `MS` stores current Standard display.
- `MR` recalls stored value into current input/display.
- `M+` and `M-` update memory.
- Memory commands ignore `Error` display.
- Standard arithmetic behavior still delegates to `CalculatorEngine`.

Expected before implementation: fail because controllers do not exist.

Concrete Standard memory controller tests must include:

```python
def test_memory_recall_preserves_pending_operation():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)
    controller.handle_button("5")
    controller.handle_button("+")
    memory.store(Decimal("12"))
    assert controller.handle_button("MR") == "12"
    assert controller.handle_button("=") == "17"


def test_memory_store_ignores_error_display():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)
    memory.store(Decimal("9"))
    controller.handle_button("5")
    controller.handle_button("÷")
    controller.handle_button("0")
    controller.handle_button("=")
    controller.handle_button("MS")
    assert memory.recall() == Decimal("9")
```

### Task 3.2: Implement `StandardModeController`

Objective: Extract Standard button/key routing and memory handling from `CalculatorUI`.

Files:

- Create: `source/mode_controllers.py`
- Modify only if needed: `calculator.py`

Controller API sketch:

```python
from __future__ import annotations

from decimal import Decimal, InvalidOperation

from source.calculator_engine import CalculatorEngine
from source.memory_store import MemoryStore


class StandardModeController:
    name = "Standard"

    def __init__(self, engine: CalculatorEngine, memory: MemoryStore) -> None:
        self.engine = engine
        self.memory = memory

    def enter(self, previous_display: str | None = None) -> str:
        return self.engine.get_display()

    def handle_button(self, label: str) -> str | None:
        # Existing Standard routing plus MC/MR/MS/M+/M-.
        ...

    def handle_key(self, key: str, char: str) -> str | None:
        # Existing Standard keyboard routing.
        ...
```

Important: do not import `CalculatorEngine` from root `calculator.py`. Task 3.0 makes `source.calculator_engine` the stable import boundary, while root `calculator.py` remains a compatibility re-export for existing tests.

### Task 3.3: Define controller tests for Programmer regression

Objective: Ensure extraction preserves PR-02.1 behavior.

Files:

- Modify: `tests/test_mode_controllers.py`
- Existing reference: `tests/test_programmer_ui.py`

Required tests:

- HEX `C` appends digit; `AC` clears.
- 64-bit cap blocks append beyond `FFFFFFFFFFFFFFFF`.
- Base switching converts value correctly.
- Invalid digit is ignored.

### Task 3.4: Implement `ProgrammerModeController`

Objective: Move programmer value/base state and routing from UI into controller.

Files:

- Modify: `source/mode_controllers.py`
- Later modify: `calculator.py`

Controller owns:

- `base_converter`
- `current_base`
- `programmer_value`

Controller exposes:

- `set_base(base: str) -> str | None`
- `handle_button(label: str) -> str | None`
- `handle_key(key: str, char: str) -> str | None`
- Button state helper for valid digits / disabled controls.

Run targeted tests.

### Task 3.2b: Midpoint controller review gate

Objective: Limit refactor risk before extracting Programmer and Date controllers.

Required checkpoint after Task 3.2:

```bash
python3 -m pytest tests/test_calculator.py tests/test_memory_store.py tests/test_mode_controllers.py -q
python3 -m py_compile calculator.py source/calculator_engine.py source/memory_store.py source/mode_controllers.py
```

Expected: Standard Mode and memory controller tests are green before continuing to Programmer controller extraction.

### Task 3.5: Define controller tests for Date Mode

Objective: Verify Date Mode workflows without Tk.

Files:

- Modify: `tests/test_mode_controllers.py`

Required tests:

- Difference workflow formats `1 day`, `2 days`, `-1 day`, and `-2 days` correctly.
- Invalid date returns controlled display `Invalid date`.
- Invalid duration fields such as `abc`, `1.5`, and negative component strings return controlled validation errors.
- Empty/whitespace duration fields are treated as zero.
- Add duration workflow returns ISO date.
- Switching into Date Mode initializes a safe default state.

### Task 3.6: Implement `DateModeController`

Objective: Provide Date Mode command/state layer for UI.

Files:

- Modify: `source/mode_controllers.py`

Recommended state:

- `workflow`: `"difference"` or `"add_subtract"`
- `start_date`
- `end_date`
- `base_date`
- `operation`: `"add"` or `"subtract"`
- `years`, `months`, `weeks`, `days`

The initial UI may update this controller through explicit methods rather than trying to force all date input through calculator number buttons.

---

## Phase 4 — Tkinter UI Integration

### Task 4.1: Add visible Memory Keys

Objective: Add Standard Mode memory controls without changing existing calculator button behavior.

Files:

- Modify: `calculator.py`
- Modify/create tests if fake-widget coverage is practical.

UI requirements:

- Add buttons `MC`, `MR`, `MS`, `M+`, `M-`.
- Enabled in Standard Mode.
- Disabled in Programmer and Date modes for PR-03.
- Display a minimal `M` memory indicator when `MemoryStore.has_value` is true; if implementation constraints force deferral, README/release notes must clearly avoid promising an indicator.

### Task 4.2: Add Date Mode selector

Objective: Add `[Date]` as third mode next to Standard/Programmer.

Files:

- Modify: `calculator.py`

UI requirements:

- Mode buttons become `[Standard] [Programmer] [Date]`.
- Date Mode disables arithmetic and Programmer-specific controls.
- Date Mode shows date workflow controls.

### Task 4.3: Add Date Mode widgets

Objective: Provide minimal Tkinter controls for both Date workflows.

Files:

- Modify: `calculator.py`

Recommended minimal UI:

- Use separate mode frames and show/hide them with `grid()` / `grid_remove()` so Standard, Programmer, and Date controls do not overlap.
- The window may resize when Date Mode is active; keeping the original compact Standard/Programmer footprint is more important than forcing Date fields into the 4-column keypad grid.
- Workflow selector: `Difference` / `Add/Subtract`
- Difference fields: `Start YYYY-MM-DD`, `End YYYY-MM-DD`, `Calculate`
- Add/Subtract fields: `Base YYYY-MM-DD`, operation selector, `Years`, `Months`, `Weeks`, `Days`, `Calculate`
- Result shown in existing display area.

Implementation notes:

- Tkinter imports stay lazy inside `CalculatorUI.__init__`.
- Controller methods do date calculation; UI only reads field values and displays the result.
- Invalid date displays `Invalid date`, not traceback.

### Task 4.4: Preserve Programmer UI behavior after controller extraction

Objective: Ensure PR-02.1 fake-widget UI coordination tests still pass or are updated to controller-based tests.

Files:

- Modify: `tests/test_programmer_ui.py`
- Modify: `tests/test_mode_controllers.py`

Run:

```bash
python3 -m pytest tests/test_programmer_ui.py tests/test_mode_controllers.py -q
```

Expected: pass.

---

## Phase 5 — Documentation and Final Verification

### Task 5.1: Update README and release notes

Objective: Document PR-03 behavior and known limits.

Files:

- Modify: `README.md`
- Modify: `docs/release_notes.md`
- Create: `docs/date_calculator_smoke_checklist.md`

Required notes:

- Date Calculator supports date difference and add/subtract durations.
- Memory Keys are Standard Mode only.
- Date calculations use ISO `YYYY-MM-DD`.
- Month/year arithmetic clamps to last valid day.
- Time zones/time-of-day/business days are out of scope.

### Task 5.2: Run final automated gate

Objective: Verify full project health.

Run:

```bash
python3 -m pytest -q && \
python3 -m py_compile calculator.py source/calculator_engine.py source/base_converter.py source/memory_store.py source/date_calculator.py source/mode_controllers.py tests/conftest.py tests/test_calculator.py tests/test_calculator_engine.py tests/test_base_converter.py tests/test_programmer_ui.py tests/test_memory_store.py tests/test_date_calculator.py tests/test_mode_controllers.py && \
git diff --check
```

Expected:

- All tests pass.
- Compile clean.
- Diff check clean.

### Task 5.3: Create PR3 implementation review package

Objective: Repeat the 3AI review gate after PR3 implementation.

Files to include:

- Changed source files
- Changed tests
- PR3 planning docs
- README/release notes
- Test logs
- Git diff

Reviewers:

- Claude: architecture, maintainability, UI/UX, mode-controller readiness.
- Codex: implementation correctness, tests, edge cases.
- Gemini: product scope, risk summary, roadmap readiness.

Do not merge to `main` until Scott reviews the final Hermes + 3AI summary.
