"""Session-only calculation history for MiniCalc."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryEntry:
    """Immutable snapshot of one completed calculation history item."""

    mode: str
    expression: str
    result: str
    status: str = "ok"


class HistoryStore:
    """In-memory, bounded calculation history store."""

    def __init__(self, max_entries: int = 100) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        self._max_entries = max_entries
        self._entries: list[HistoryEntry] = []

    def add(self, entry: HistoryEntry) -> None:
        """Append an entry and trim oldest entries beyond the configured cap."""
        self._entries.append(entry)
        overflow = len(self._entries) - self._max_entries
        if overflow > 0:
            del self._entries[:overflow]

    def clear(self) -> None:
        """Remove all history entries."""
        self._entries.clear()

    def entries(self) -> tuple[HistoryEntry, ...]:
        """Return an immutable snapshot of entries in display order."""
        return tuple(self._entries)

    def formatted_lines(self) -> tuple[str, ...]:
        """Return user-facing display lines for all entries."""
        return tuple(self._format_entry(entry) for entry in self._entries)

    @staticmethod
    def _format_entry(entry: HistoryEntry) -> str:
        mode_label = entry.mode if entry.status == "ok" else f"{entry.mode}:{entry.status}"
        return f"[{mode_label}] {entry.expression} = {entry.result}"
