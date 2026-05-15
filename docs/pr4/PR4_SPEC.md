# PR-04 Specification — Calculation History / Session Tape

Date: 2026-05-15
Branch: `pr4-planning`
Base: `a6c68e3 docs: resolve PR3 review package hygiene notes`
Status: Planning draft for 3AI review

## 1. Goal

PR-04 adds a lightweight, session-only calculation history feature to MiniCalc.

The feature should make MiniCalc more useful for checking recent calculations while continuing to serve the broader Hermes + 3AI workflow goal: clear scope, headless logic, TDD, traceable commits, and reviewable artifacts.

## 2. User-facing scope

### 2.1 Standard Mode history

Record one history entry whenever a Standard Mode calculation is explicitly completed by `=` / `Enter`.

Examples:

- `2 + 3 = 5`
- `5 ÷ 0 = Error`

PR-04 intentionally does **not** require immediate-execution chaining history. For example, `1 + 2 +` may update the display to `3`, but it should not create a history entry in PR-04. Chaining can become a PR-05+ enhancement after the engine exposes explicit completion events for operator-press evaluations.

Required PR-04 behavior:

- Completed `=` / `Enter` operations are recorded.
- Controlled Standard errors such as divide-by-zero are recorded with `status="error"`.
- Repeated `=` does not add a new entry unless the engine later defines repeat-equals semantics.
- Percent/sign/backspace/clear/digit-only input alone does not create history.

### 2.2 Date Mode history

Record Date Mode completed calculations:

- Date difference: `2026-05-15 → 2026-05-20 = 5 days`
- Date add/subtract: `2026-01-31 + 1 month = 2026-02-28`

Invalid Date Mode calculations should not add successful history entries. Optional controlled error entries may be added only if the UI already surfaces the error consistently.

### 2.3 Programmer Mode history

Record base-switch conversions, not every digit press.

Examples:

- `DEC 255 → HEX FF`
- `HEX FF → BIN 11111111`

Invalid ignored inputs should not create history entries.

### 2.4 History UI

Add a compact History panel or toggleable History area to the Tkinter UI.

Required controls:

- Visible history list/text area.
- `Clear History` button.

Optional only if low risk:

- Copy selected/all history to clipboard.
- Collapse/expand history panel.

### 2.5 Session-only behavior

PR-04 history is in-memory only:

- Closing the app clears history.
- No disk persistence.
- No export file.
- No cloud sync.

Persistence can be PR-05+ if Scott wants it.

## 3. Architecture scope

### 3.1 New headless module

Create `source/history_store.py`.

Suggested public API:

```python
@dataclass(frozen=True)
class HistoryEntry:
    mode: str
    expression: str
    result: str
    status: str = "ok"

class HistoryStore:
    def __init__(self, max_entries: int = 100): ...
    def add(self, entry: HistoryEntry) -> None: ...
    def clear(self) -> None: ...
    def entries(self) -> tuple[HistoryEntry, ...]: ...
    def formatted_lines(self) -> tuple[str, ...]: ...
```

Rules:

- `max_entries` keeps only newest N entries.
- Store immutable snapshots, not references to mutable UI state.
- No Tkinter imports.
- No filesystem writes.

### 3.2 Controller integration

Preferred approach:

- Keep `HistoryStore` owned by `CalculatorUI` or a small history controller.
- Preserve existing display-string return values from controller methods where possible.
- Add a narrow history-event drain seam such as `pop_history_entry()` / `last_history_entry` on controllers that can emit history.
- Tkinter callback code should only drain already-formed events and append them to `HistoryStore`; it should not reconstruct complex business logic.

Avoid:

- Rebuilding Standard Mode expressions by scraping Tkinter button labels after the fact.
- Coupling `HistoryStore` directly to `CalculatorEngine` internals.
- Introducing persistence or serialization in PR-04.

### 3.3 Standard engine consideration

If Standard history requires expression metadata, introduce a minimal public completion-event API rather than reading private fields from the UI.

Required low-risk path:

- Keep `StandardModeController.handle_button(label)` returning the display string.
- `StandardModeController` captures the expression context before invoking `press_equals()` for `=` / `Enter`.
- After the action, the UI or tests can call `pop_history_entry()` to retrieve and clear the pending history event.
- This seam must be covered by headless tests.

## 4. Testing scope

New tests:

- `tests/test_history_store.py`
- Add controller/history tests to `tests/test_mode_controllers.py` or a new `tests/test_history_integration.py`
- Extend lightweight UI coordination tests only where useful and headless.

Required coverage:

- Add / clear / formatted lines.
- Max-entry trimming.
- Standard completed calculation creates one entry.
- Standard digit-only input creates no entry.
- Standard error calculation records controlled result or explicitly skips according to final acceptance criteria.
- Date difference creates a history entry.
- Date duration calculation creates a history entry.
- Programmer base-switch conversion creates a history entry only when the base actually changes.
- Programmer same-base click, digit entry, backspace, clear, and ignored invalid input create no entry.

## 5. Non-goals

- Persistent history across app restarts.
- Export/import history files.
- Search/filter history.
- Undo from history.
- Re-click history item to restore calculation.
- Full GUI screenshot automation.
- Changing PR-03 Date/Memory behavior except where needed to emit history events.

## 6. Quality gates

Before PR-04 implementation review:

```bash
python3 -m pytest -q
python3 -m py_compile calculator.py source/calculator_engine.py source/base_converter.py source/memory_store.py source/date_calculator.py source/mode_controllers.py source/history_store.py tests/conftest.py tests/test_calculator.py tests/test_base_converter.py tests/test_programmer_ui.py tests/test_memory_store.py tests/test_date_calculator.py tests/test_mode_controllers.py tests/test_history_store.py
git diff --check
```

Manual GUI smoke should include:

- History panel visible and readable.
- Standard history records completed calculation.
- Clear History empties the panel.
- Date and Programmer history entries render without layout breakage.

## 7. Open questions for 3AI review

1. Is deferring Standard immediate-execution chaining to PR-05+ the right risk tradeoff?
2. Is recording controlled Standard errors with `status="error"` sufficient while skipping invalid Date/Programmer no-op errors?
3. Is the `pop_history_entry()` seam preferable to broad `ModeResult` migration for PR-04?
4. Is a persistent history out-of-scope decision correct for PR-04?
