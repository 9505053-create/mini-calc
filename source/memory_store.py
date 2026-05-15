"""Memory store for MiniCalc Standard Mode memory keys."""

from __future__ import annotations

from decimal import Decimal


class MemoryStore:
    """Store one Decimal memory value for calculator memory keys."""

    def __init__(self) -> None:
        self._value = Decimal("0")
        self._has_value = False

    @property
    def has_value(self) -> bool:
        """Return whether memory should show an active non-zero indicator."""
        return self._has_value

    def recall(self) -> Decimal:
        """Return the current memory value."""
        return self._value

    def store(self, value: Decimal) -> None:
        """Replace memory with ``value``."""
        self._value = value
        self._has_value = value != 0

    def add(self, value: Decimal) -> None:
        """Add ``value`` to memory."""
        self.store(self._value + value)

    def subtract(self, value: Decimal) -> None:
        """Subtract ``value`` from memory."""
        self.store(self._value - value)

    def clear(self) -> None:
        """Reset memory to zero and clear the active indicator."""
        self._value = Decimal("0")
        self._has_value = False
