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
