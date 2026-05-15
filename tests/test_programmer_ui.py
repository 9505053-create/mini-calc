"""Lightweight tests for Programmer Mode UI coordination without opening Tk."""

from __future__ import annotations

from types import MethodType, SimpleNamespace

from calculator import CalculatorUI
from source.base_converter import BaseConverter


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
