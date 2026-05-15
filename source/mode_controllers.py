"""Headless mode controllers for MiniCalc UI routing."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from source.base_converter import BaseConverter
from source.calculator_engine import CalculatorEngine
from source.date_calculator import DateCalculator
from source.memory_store import MemoryStore


class StandardModeController:
    """Route Standard Mode commands and coordinate calculator memory."""

    name = "Standard"

    def __init__(self, engine: CalculatorEngine, memory: MemoryStore) -> None:
        self.engine = engine
        self.memory = memory

    def enter(self, previous_display: str | None = None) -> str:
        return self.engine.get_display()

    def handle_button(self, label: str) -> str:
        operator_map = {"×": "*", "÷": "/"}
        if label.isdigit():
            return self.engine.press_digit(label)
        if label == ".":
            return self.engine.press_decimal()
        if label in {"+", "-", "×", "÷"}:
            return self.engine.press_operator(operator_map.get(label, label))
        if label == "=":
            return self.engine.press_equals()
        if label in {"CLEAR", "AC", "C"}:
            return self.engine.press_clear()
        if label == "+/-":
            return self.engine.press_toggle_sign()
        if label == "%":
            return self.engine.press_percent()
        if label == "BS":
            return self.engine.press_backspace()
        if label in {"MC", "MR", "MS", "M+", "M-"}:
            return self._handle_memory_button(label)
        return self.engine.get_display()

    def handle_key(self, key: str, char: str) -> str | None:
        if char and char.isdigit():
            return self.engine.press_digit(char)
        if char == ".":
            return self.engine.press_decimal()
        if char in "+-*/":
            return self.engine.press_operator(char)
        if char == "%":
            return self.engine.press_percent()
        if key in ("Return", "KP_Enter"):
            return self.engine.press_equals()
        if key == "Escape":
            return self.engine.press_clear()
        if key == "BackSpace":
            return self.engine.press_backspace()
        return None

    def _handle_memory_button(self, label: str) -> str:
        display = self.engine.get_display()
        if label == "MC":
            self.memory.clear()
            return display
        if label == "MR":
            return self.engine.replace_current_input(str(self.memory.recall()))

        value = self._decimal_from_display()
        if value is None:
            return display
        if label == "MS":
            self.memory.store(value)
        elif label == "M+":
            self.memory.add(value)
        elif label == "M-":
            self.memory.subtract(value)
        return display

    def _decimal_from_display(self) -> Decimal | None:
        try:
            return Decimal(self.engine.get_display())
        except InvalidOperation:
            return None


class ProgrammerModeController:
    """Route Programmer Mode commands and own base-conversion state."""

    name = "Programmer"

    def __init__(self, base_converter: BaseConverter | None = None) -> None:
        self.base_converter = base_converter or BaseConverter()
        self.current_base = "DEC"
        self.programmer_value = "0"

    def enter(self, previous_display: str | None = None) -> str:
        self.current_base = "DEC"
        self.programmer_value = previous_display if previous_display and previous_display.isdigit() else "0"
        return self.programmer_value

    def set_base(self, base: str) -> str:
        if base == self.current_base:
            return self.programmer_value
        self.programmer_value = self.base_converter.convert(
            self.programmer_value, self.current_base, base
        )
        self.current_base = base
        return self.programmer_value

    def handle_button(self, label: str) -> str:
        if label in BaseConverter.BASES:
            return self.set_base(label)
        if label in {"CLEAR", "AC"}:
            self.programmer_value = "0"
        elif label in BaseConverter.VALID_DIGITS["HEX"]:
            self.programmer_value = self.base_converter.append_digit(
                self.programmer_value, label, self.current_base
            )
        elif label == "BS":
            self.programmer_value = self.base_converter.backspace(self.programmer_value)
        return self.programmer_value

    def handle_key(self, key: str, char: str) -> str | None:
        if char:
            upper = char.upper()
            if upper in BaseConverter.VALID_DIGITS["HEX"]:
                return self.handle_button(upper)
        if key == "Escape":
            return self.handle_button("AC")
        if key == "BackSpace":
            return self.handle_button("BS")
        return None

    def button_states(self) -> dict[str, str]:
        disabled = {".", "%", "+/-", "=", "+", "-", "×", "÷"}
        states: dict[str, str] = {}
        for label in ["AC", *list("0123456789ABCDEF"), *disabled]:
            if label in disabled:
                states[label] = "disabled"
            elif label in BaseConverter.VALID_DIGITS["HEX"]:
                states[label] = (
                    "normal" if label in BaseConverter.VALID_DIGITS[self.current_base] else "disabled"
                )
            else:
                states[label] = "normal"
        return states


class DateModeController:
    """Coordinate Date Mode workflows without Tkinter dependencies."""

    name = "Date"

    def __init__(self, date_calculator: DateCalculator | None = None) -> None:
        self.date_calculator = date_calculator or DateCalculator()
        self.workflow = "difference"

    def enter(self, previous_display: str | None = None) -> str:
        return "Date Mode"

    def calculate_difference(self, start_date: str, end_date: str) -> str:
        try:
            days = self.date_calculator.days_between(start_date, end_date)
        except ValueError:
            return "Invalid date"
        suffix = "day" if abs(days) == 1 else "days"
        return f"{days} {suffix}"

    def calculate_duration(
        self,
        base_date: str,
        *,
        operation: str,
        years: str = "0",
        months: str = "0",
        weeks: str = "0",
        days: str = "0",
    ) -> str:
        try:
            return self.date_calculator.add_duration(
                base_date,
                operation=operation,
                years=years,
                months=months,
                weeks=weeks,
                days=days,
            )
        except ValueError as exc:
            message = str(exc)
            if "invalid ISO date" in message:
                return "Invalid date"
            return "Invalid duration"
