"""Lightweight tests for Programmer Mode UI coordination without opening Tk."""

from __future__ import annotations

from types import MethodType, SimpleNamespace

from calculator import CalculatorUI
from source.base_converter import BaseConverter
from source.calculator_engine import CalculatorEngine
from source.memory_store import MemoryStore
from source.mode_controllers import DateModeController, ProgrammerModeController, StandardModeController


class FakeDisplayVar:
    def __init__(self) -> None:
        self.value = None

    def set(self, value: str) -> None:
        self.value = value


class FakeButton:
    def __init__(self, text: str) -> None:
        self.text = text
        self.options = {}
        self.visible = True

    def configure(self, **kwargs) -> None:
        self.options.update(kwargs)

    def cget(self, key: str) -> str:
        if key == "text":
            return self.text
        raise KeyError(key)

    def grid(self) -> None:
        self.visible = True

    def grid_remove(self) -> None:
        self.visible = False


def make_programmer_ui() -> SimpleNamespace:
    ui = SimpleNamespace()
    ui.base_converter = BaseConverter()
    ui.programmer_controller = ProgrammerModeController(ui.base_converter)
    ui.programmer_controller.current_base = "HEX"
    ui.mode = "Programmer"
    ui.current_base = "HEX"
    ui.programmer_value = "0"
    ui.display_var = FakeDisplayVar()
    ui.mode_buttons = {label: FakeButton(label) for label in ("Standard", "Programmer")}
    ui.base_buttons = {label: FakeButton(label) for label in BaseConverter.BASES}
    ui.buttons = {label: FakeButton(label) for label in ("AC", "+/-", "%", "÷", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "=", "+", "-", "×")}
    ui.hex_buttons = [FakeButton(label) for label in "ABCDEF"]
    ui.update_display = MethodType(CalculatorUI.update_display, ui)
    ui.set_base = MethodType(CalculatorUI.set_base, ui)
    ui._refresh_mode_controls = MethodType(CalculatorUI._refresh_mode_controls, ui)
    ui._sync_programmer_state = MethodType(CalculatorUI._sync_programmer_state, ui)
    ui._handle_programmer_button = MethodType(CalculatorUI._handle_programmer_button, ui)
    ui._handle_programmer_key = MethodType(CalculatorUI._handle_programmer_key, ui)
    return ui


def test_programmer_mode_ac_button_clears_without_conflicting_with_hex_c():
    ui = make_programmer_ui()
    ui.programmer_value = "AB"

    ui._handle_programmer_button("C")
    assert ui.programmer_value == "ABC"
    assert ui.display_var.value == "ABC"

    ui._handle_programmer_button("AC")
    assert ui.programmer_value == "0"
    assert ui.display_var.value == "0"


def test_programmer_mode_ignores_digits_beyond_64_bit_limit():
    ui = make_programmer_ui()
    ui.programmer_value = "F" * 16

    ui._handle_programmer_button("F")

    assert ui.programmer_value == "F" * 16
    assert ui.display_var.value == "F" * 16


def test_refresh_mode_controls_disables_invalid_digits_per_base():
    ui = make_programmer_ui()
    ui.current_base = "BIN"

    ui._refresh_mode_controls()

    assert ui.buttons["0"].options["state"] == "normal"
    assert ui.buttons["1"].options["state"] == "normal"
    assert ui.buttons["2"].options["state"] == "disabled"
    assert all(button.options["state"] == "disabled" for button in ui.hex_buttons)



def make_standard_ui() -> SimpleNamespace:
    ui = SimpleNamespace()
    ui.engine = CalculatorEngine()
    ui.memory = MemoryStore()
    ui.standard_controller = StandardModeController(ui.engine, ui.memory)
    ui.mode = "Standard"
    ui.display_var = FakeDisplayVar()
    ui.memory_indicator_var = FakeDisplayVar()
    ui.update_display = MethodType(CalculatorUI.update_display, ui)
    ui.handle_button = MethodType(CalculatorUI.handle_button, ui)
    return ui


def make_date_ui() -> SimpleNamespace:
    ui = SimpleNamespace()
    ui.mode = "Date"
    ui.date_controller = DateModeController()
    ui.display_var = FakeDisplayVar()
    ui.memory = MemoryStore()
    ui.memory_indicator_var = FakeDisplayVar()
    ui.date_start_var = SimpleNamespace(get=lambda: "2026-05-15")
    ui.date_end_var = SimpleNamespace(get=lambda: "2026-05-17")
    ui.date_base_var = SimpleNamespace(get=lambda: "2024-01-31")
    ui.date_operation_var = SimpleNamespace(get=lambda: "add")
    ui.date_years_var = SimpleNamespace(get=lambda: "1")
    ui.date_months_var = SimpleNamespace(get=lambda: "1")
    ui.date_weeks_var = SimpleNamespace(get=lambda: "")
    ui.date_days_var = SimpleNamespace(get=lambda: "5")
    ui.update_display = MethodType(CalculatorUI.update_display, ui)
    ui.calculate_date_difference = MethodType(CalculatorUI.calculate_date_difference, ui)
    ui.calculate_date_duration = MethodType(CalculatorUI.calculate_date_duration, ui)
    return ui


def test_standard_ui_memory_buttons_update_display_and_indicator():
    ui = make_standard_ui()

    ui.handle_button("1")
    ui.handle_button("2")
    ui.handle_button("MS")
    assert ui.display_var.value == "12"
    assert ui.memory_indicator_var.value == "M"

    ui.handle_button("AC")
    ui.handle_button("MR")
    assert ui.display_var.value == "12"

    ui.handle_button("MC")
    assert ui.memory_indicator_var.value == ""


def test_date_ui_calculate_difference_updates_display():
    ui = make_date_ui()

    ui.calculate_date_difference()

    assert ui.display_var.value == "2 days"


def test_date_ui_calculate_duration_updates_display():
    ui = make_date_ui()

    ui.calculate_date_duration()

    assert ui.display_var.value == "2025-03-05"
