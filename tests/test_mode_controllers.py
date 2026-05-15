from decimal import Decimal

from source.calculator_engine import CalculatorEngine
from source.history_store import HistoryEntry
from source.memory_store import MemoryStore
from source.mode_controllers import DateModeController, ProgrammerModeController, StandardModeController


def test_standard_controller_memory_store_and_recall():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)

    controller.handle_button("1")
    controller.handle_button("2")
    assert controller.handle_button("MS") == "12"
    assert memory.recall() == Decimal("12")

    controller.handle_button("AC")
    assert controller.handle_button("MR") == "12"


def test_standard_controller_memory_add_and_subtract():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)

    controller.handle_button("1")
    controller.handle_button("0")
    controller.handle_button("MS")
    controller.handle_button("AC")
    controller.handle_button("2")
    controller.handle_button("M+")
    assert memory.recall() == Decimal("12")
    controller.handle_button("3")
    controller.handle_button("M-")
    assert memory.recall() == Decimal("-11")


def test_standard_controller_memory_recall_preserves_pending_operation():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)

    controller.handle_button("5")
    controller.handle_button("+")
    memory.store(Decimal("12"))
    assert controller.handle_button("MR") == "12"
    assert controller.handle_button("=") == "17"


def test_standard_controller_memory_store_ignores_error_display():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)

    memory.store(Decimal("9"))
    controller.handle_button("5")
    controller.handle_button("÷")
    controller.handle_button("0")
    controller.handle_button("=")
    assert engine.get_display() == "Error"
    assert controller.handle_button("MS") == "Error"
    assert memory.recall() == Decimal("9")


def test_standard_controller_memory_clear():
    engine = CalculatorEngine()
    memory = MemoryStore()
    controller = StandardModeController(engine, memory)

    memory.store(Decimal("9"))
    assert controller.handle_button("MC") == "0"
    assert memory.recall() == Decimal("0")
    assert not memory.has_value




def test_standard_controller_records_equals_history_entry():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("2")
    controller.handle_button("+")
    controller.handle_button("3")
    assert controller.handle_button("=") == "5"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="2 + 3", result="5"
    )
    assert controller.pop_history_entry() is None


def test_standard_controller_records_keyboard_enter_history_entry():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("8")
    controller.handle_button("÷")
    controller.handle_button("4")
    assert controller.handle_key("Return", "") == "2"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="8 ÷ 4", result="2"
    )


def test_standard_controller_records_controlled_error_history_entry():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("5")
    controller.handle_button("÷")
    controller.handle_button("0")
    assert controller.handle_button("=") == "Error"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="5 ÷ 0", result="Error", status="error"
    )


def test_standard_controller_does_not_record_digit_or_memory_actions():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("1")
    controller.handle_button("MS")

    assert controller.pop_history_entry() is None


def test_standard_controller_records_chaining_operator_history_entry():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("1")
    controller.handle_button("+")
    controller.handle_button("2")
    assert controller.handle_button("+") == "3"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="1 + 2", result="3"
    )
    assert controller.pop_history_entry() is None

    controller.handle_button("3")
    assert controller.handle_button("=") == "6"
    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="3 + 3", result="6"
    )


def test_standard_controller_operator_replacement_does_not_record_history():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("1")
    controller.handle_button("+")
    assert controller.handle_button("-") == "1"

    assert controller.pop_history_entry() is None


def test_standard_controller_records_chaining_controlled_error_history_entry():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_button("5")
    controller.handle_button("÷")
    controller.handle_button("0")
    assert controller.handle_button("+") == "Error"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="5 ÷ 0", result="Error", status="error"
    )


def test_standard_controller_records_keyboard_operator_chaining_history_entry():
    controller = StandardModeController(CalculatorEngine(), MemoryStore())

    controller.handle_key("", "4")
    controller.handle_key("", "*")
    controller.handle_key("", "5")
    assert controller.handle_key("", "+") == "20"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Standard", expression="4 × 5", result="20"
    )

def test_programmer_controller_hex_c_is_digit_and_ac_clears():
    controller = ProgrammerModeController()
    controller.set_base("HEX")
    controller.programmer_value = "AB"

    assert controller.handle_button("C") == "ABC"
    assert controller.programmer_value == "ABC"
    assert controller.handle_button("AC") == "0"
    assert controller.programmer_value == "0"


def test_programmer_controller_blocks_64_bit_overflow():
    controller = ProgrammerModeController()
    controller.set_base("HEX")
    controller.programmer_value = "F" * 16

    assert controller.handle_button("F") == "F" * 16
    assert controller.programmer_value == "F" * 16


def test_programmer_controller_switches_base_and_ignores_invalid_digit():
    controller = ProgrammerModeController()
    assert controller.handle_button("1") == "1"
    assert controller.handle_button("5") == "15"
    assert controller.set_base("HEX") == "F"
    assert controller.current_base == "HEX"
    assert controller.set_base("BIN") == "1111"
    assert controller.handle_button("2") == "1111"




def test_programmer_controller_records_base_switch_history_entry():
    controller = ProgrammerModeController()
    controller.handle_button("2")
    controller.handle_button("5")
    controller.handle_button("5")

    assert controller.set_base("HEX") == "FF"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Programmer", expression="DEC 255 → HEX", result="FF"
    )


def test_programmer_controller_records_normalized_base_switch_history_entry():
    controller = ProgrammerModeController()
    controller.programmer_value = "000255"

    assert controller.set_base("HEX") == "FF"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Programmer", expression="DEC 255 → HEX", result="FF"
    )


def test_programmer_controller_same_base_digits_and_clear_do_not_record_history():
    controller = ProgrammerModeController()

    controller.handle_button("1")
    controller.handle_button("BS")
    controller.handle_button("AC")
    assert controller.set_base("DEC") == "0"

    assert controller.pop_history_entry() is None

def test_programmer_controller_button_state_rules():
    controller = ProgrammerModeController()
    controller.set_base("BIN")
    states = controller.button_states()

    assert states["0"] == "normal"
    assert states["1"] == "normal"
    assert states["2"] == "disabled"
    assert states["A"] == "disabled"





def test_date_controller_enter_initializes_safe_display():
    controller = DateModeController()
    assert controller.enter() == "Date Mode"


def test_date_controller_difference_formats_day_singular_plural_and_negative():
    controller = DateModeController()
    assert controller.calculate_difference("2026-05-15", "2026-05-16") == "1 day"
    assert controller.calculate_difference("2026-05-15", "2026-05-17") == "2 days"
    assert controller.calculate_difference("2026-05-16", "2026-05-15") == "-1 day"
    assert controller.calculate_difference("2026-05-17", "2026-05-15") == "-2 days"


def test_date_controller_invalid_date_returns_controlled_message():
    controller = DateModeController()
    assert controller.calculate_difference("2026-02-30", "2026-03-01") == "Invalid date"


def test_date_controller_add_duration_returns_iso_date():
    controller = DateModeController()
    assert controller.calculate_duration(
        "2024-01-31", operation="add", years="1", months="1", weeks="", days="5"
    ) == "2025-03-05"


def test_date_controller_invalid_duration_returns_controlled_message():
    controller = DateModeController()
    assert controller.calculate_duration(
        "2026-05-15", operation="add", years="", months="", weeks="", days="abc"
    ) == "Invalid duration"


def test_date_controller_subtract_duration_returns_iso_date():
    controller = DateModeController()
    assert controller.calculate_duration(
        "2024-03-31", operation="subtract", years="", months="1", weeks="", days=""
    ) == "2024-02-29"



def test_date_controller_records_difference_history_entry():
    controller = DateModeController()

    assert controller.calculate_difference("2026-05-15", "2026-05-20") == "5 days"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Date", expression="2026-05-15 → 2026-05-20", result="5 days"
    )


def test_date_controller_records_duration_add_history_entry():
    controller = DateModeController()

    assert controller.calculate_duration(
        "2026-01-31", operation="add", years="", months="1", weeks="", days=""
    ) == "2026-02-28"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Date", expression="2026-01-31 + 1 month", result="2026-02-28"
    )


def test_date_controller_records_duration_subtract_history_entry():
    controller = DateModeController()

    assert controller.calculate_duration(
        "2026-03-31", operation="subtract", years="", months="1", weeks="", days=""
    ) == "2026-02-28"

    assert controller.pop_history_entry() == HistoryEntry(
        mode="Date", expression="2026-03-31 - 1 month", result="2026-02-28"
    )


def test_date_controller_invalid_inputs_do_not_record_history():
    controller = DateModeController()

    assert controller.calculate_difference("2026-02-30", "2026-03-01") == "Invalid date"
    assert controller.pop_history_entry() is None
    assert controller.calculate_duration(
        "2026-05-15", operation="add", years="", months="", weeks="", days="abc"
    ) == "Invalid duration"
    assert controller.pop_history_entry() is None
