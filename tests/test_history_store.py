import pytest

from source.history_store import HistoryEntry, HistoryStore


def test_history_starts_empty():
    store = HistoryStore()

    assert store.entries() == ()
    assert store.formatted_lines() == ()


def test_add_entry_returns_immutable_snapshot():
    store = HistoryStore()
    entry = HistoryEntry(mode="Standard", expression="2 + 3", result="5")

    store.add(entry)
    snapshot = store.entries()

    assert snapshot == (entry,)
    assert isinstance(snapshot, tuple)
    with pytest.raises(AttributeError):
        snapshot[0].result = "6"


def test_clear_removes_entries():
    store = HistoryStore()
    store.add(HistoryEntry(mode="Standard", expression="2 + 3", result="5"))

    store.clear()

    assert store.entries() == ()
    assert store.formatted_lines() == ()


def test_max_entries_keeps_newest_entries():
    store = HistoryStore(max_entries=2)

    store.add(HistoryEntry(mode="Standard", expression="1 + 1", result="2"))
    store.add(HistoryEntry(mode="Date", expression="2026-05-15 → 2026-05-20", result="5 days"))
    store.add(HistoryEntry(mode="Programmer", expression="DEC 255 → HEX", result="FF"))

    assert store.entries() == (
        HistoryEntry(mode="Date", expression="2026-05-15 → 2026-05-20", result="5 days"),
        HistoryEntry(mode="Programmer", expression="DEC 255 → HEX", result="FF"),
    )


def test_formatted_lines_include_mode_expression_result_and_status():
    store = HistoryStore()
    store.add(HistoryEntry(mode="Standard", expression="2 + 3", result="5"))
    store.add(HistoryEntry(mode="Standard", expression="5 ÷ 0", result="Error", status="error"))

    assert store.formatted_lines() == (
        "[Standard] 2 + 3 = 5",
        "[Standard:error] 5 ÷ 0 = Error",
    )


@pytest.mark.parametrize("max_entries", [0, -1])
def test_invalid_max_entries_rejected(max_entries):
    with pytest.raises(ValueError, match="max_entries"):
        HistoryStore(max_entries=max_entries)
