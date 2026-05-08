"""MiniCalc: a small Tkinter calculator with a headless arithmetic engine."""

from __future__ import annotations

from decimal import Decimal, DivisionByZero, InvalidOperation, localcontext


class CalculatorEngine:
    """State-machine calculator engine with no GUI dependencies."""

    WAITING_FIRST = "waiting_for_first_operand"
    WAITING_SECOND = "waiting_for_second_operand"
    RESULT = "result_displayed"
    ERROR = "error"

    OPERATORS = {"+", "-", "*", "/"}
    MAX_DECIMAL_PLACES = 8
    MAX_DISPLAY_DIGITS = 12

    def __init__(self) -> None:
        self.press_clear()

    def press_digit(self, digit: str) -> str:
        if self.state == self.ERROR:
            return self.display
        if digit not in "0123456789" or len(digit) != 1:
            return self.display
        if self.state == self.RESULT:
            self._reset_for_new_input()
        if self.state == self.WAITING_SECOND and self.current_input is None:
            self.current_input = ""
        self.current_input = self._append_digit(self.current_input, digit)
        self.display = self.current_input
        return self.display

    def press_decimal(self) -> str:
        if self.state == self.ERROR:
            return self.display
        if self.state == self.RESULT:
            self._reset_for_new_input()
        if self.state == self.WAITING_SECOND and self.current_input is None:
            self.current_input = ""
        if self.current_input is None or self.current_input == "":
            self.current_input = "0."
        elif "." not in self.current_input:
            self.current_input += "."
        self.display = self.current_input
        return self.display

    def press_operator(self, operator: str) -> str:
        if self.state == self.ERROR:
            return self.display
        if operator not in self.OPERATORS:
            return self.display

        if self.state == self.RESULT:
            self.first_operand = self._decimal_from_display()
            self.pending_operator = operator
            self.current_input = None
            self.state = self.WAITING_SECOND
            return self.display

        if self.first_operand is None:
            if not self._has_active_number():
                return self.display
            self.first_operand = self._parse_current_input()
            if self.first_operand is None:
                return self.display
            self.pending_operator = operator
            self.current_input = None
            self.state = self.WAITING_SECOND
            return self.display

        if self.state == self.WAITING_SECOND and not self._has_active_number():
            self.pending_operator = operator
            return self.display

        result = self._compute_pending()
        if result is None:
            return self.display
        self.display = self._format_decimal(result)
        if self.state == self.ERROR:
            return self.display
        self.first_operand = result
        self.pending_operator = operator
        self.current_input = None
        self.state = self.WAITING_SECOND
        return self.display

    def press_equals(self) -> str:
        if self.state == self.ERROR:
            return self.display
        if self.first_operand is None or self.pending_operator is None:
            return self.display
        if not self._has_active_number():
            return self.display
        result = self._compute_pending()
        if result is None:
            return self.display
        self.display = self._format_decimal(result)
        if self.state != self.ERROR:
            self.first_operand = result
            self.pending_operator = None
            self.current_input = self.display
            self.state = self.RESULT
        return self.display

    def press_clear(self) -> str:
        self.first_operand: Decimal | None = None
        self.pending_operator: str | None = None
        self.current_input: str | None = "0"
        self.display = "0"
        self.state = self.WAITING_FIRST
        return self.display

    def press_backspace(self) -> str:
        if self.state == self.ERROR:
            return self.display
        if self.state == self.RESULT:
            return self.display
        if self.current_input is None or self.current_input in ("", "0"):
            return self.display
        # Remove last character
        if len(self.current_input) <= 1 or (len(self.current_input) == 2 and self.current_input.startswith("-")):
            self.current_input = "0"
        else:
            self.current_input = self.current_input[:-1]
        self.display = self.current_input
        return self.display

    def press_toggle_sign(self) -> str:
        if self.state == self.ERROR:
            return self.display
        if self.state == self.RESULT:
            value = self._decimal_from_display()
            if value is None:
                return self.display
            self.display = self._format_decimal(-value)
            self.current_input = self.display
            return self.display
        if self.state == self.WAITING_SECOND and self.current_input is None:
            self.current_input = "0"
        if self.current_input in (None, "", "0", "0.", "-0", "-0."):
            # Don't show -0
            self.current_input = "0" if self.current_input in ("0", "-0") else "0."
        elif self.current_input.startswith("-"):
            self.current_input = self.current_input[1:]
        else:
            self.current_input = "-" + self.current_input
        self.display = self.current_input
        return self.display

    def press_percent(self) -> str:
        if self.state == self.ERROR or not self._has_active_number():
            return self.display
        value = self._parse_current_input()
        if value is None:
            return self.display
        # Mainstream calculator behavior:
        # For + or -: x op y% → compute x op (x * y / 100) immediately
        # For * or /: y% → y / 100
        if self.first_operand is not None and self.pending_operator in ("+", "-"):
            percent_value = self.first_operand * value / Decimal("100")
            self.current_input = str(percent_value)
            result = self._compute_pending()
            if result is not None:
                self.display = self._format_decimal(result)
                if self.state != self.ERROR:
                    self.first_operand = result
                    self.pending_operator = None
                    self.current_input = self.display
                    self.state = self.RESULT
        else:
            value = value / Decimal("100")
            self.display = self._format_decimal(value)
            if self.state != self.ERROR:
                self.current_input = self.display
        return self.display

    def get_display(self) -> str:
        return self.display

    def get_state(self) -> str:
        return self.state

    def _append_digit(self, current: str | None, digit: str) -> str:
        if current in (None, "", "0"):
            return digit
        if current == "-0":
            return "-" + digit
        numeric_count = sum(ch.isdigit() for ch in current)
        if numeric_count >= self.MAX_DISPLAY_DIGITS:
            return current
        return current + digit

    def _compute_pending(self) -> Decimal | None:
        right = self._parse_current_input()
        if right is None or self.first_operand is None or self.pending_operator is None:
            return None
        try:
            with localcontext() as context:
                context.prec = 40
                if self.pending_operator == "+":
                    return self.first_operand + right
                if self.pending_operator == "-":
                    return self.first_operand - right
                if self.pending_operator == "*":
                    return self.first_operand * right
                if self.pending_operator == "/":
                    if right == 0:
                        self._set_error("Error")
                        return None
                    return self.first_operand / right
        except (DivisionByZero, InvalidOperation, OverflowError):
            self._set_error("Error")
        return None

    def _format_decimal(self, value: Decimal) -> str:
        if not value.is_finite():
            self._set_error("Overflow")
            return self.display

        with localcontext() as context:
            context.prec = 40

            # Check integer part length first
            int_part = abs(value.to_integral_value(rounding="ROUND_DOWN"))
            int_digits = len(str(int(int_part))) if int_part != 0 else 1

            # Integer part exceeds display limit → scientific notation
            if int_digits > self.MAX_DISPLAY_DIGITS:
                scientific = f"{value:.8E}"
                coefficient, exponent = scientific.split("E")
                coefficient = coefficient.rstrip("0").rstrip(".")
                return f"{coefficient}e{int(exponent):+d}"

            # Dynamically allocate remaining space to decimals (max 8)
            available = max(0, self.MAX_DISPLAY_DIGITS - int_digits)
            decimal_places = min(self.MAX_DECIMAL_PLACES, available)

            if decimal_places > 0:
                quantizer = Decimal("1").scaleb(-decimal_places)
                rounded = value.quantize(quantizer)
            else:
                rounded = value.to_integral_value()

        if rounded == 0:
            return "0"

        text = format(rounded, "f")
        if "." in text:
            text = text.rstrip("0").rstrip(".")
        return text or "0"

    def _parse_current_input(self) -> Decimal | None:
        if not self._has_active_number():
            return None
        text = self.current_input or self.display
        try:
            return Decimal(text)
        except InvalidOperation:
            self._set_error("Error")
            return None

    def _decimal_from_display(self) -> Decimal | None:
        try:
            return Decimal(self.display)
        except InvalidOperation:
            self._set_error("Error")
            return None

    def _has_active_number(self) -> bool:
        return self.current_input not in (None, "", "-", ".", "-.")

    def _digit_count(self, text: str) -> int:
        return sum(ch.isdigit() for ch in text)

    def _reset_for_new_input(self) -> None:
        self.first_operand = None
        self.pending_operator = None
        self.current_input = "0"
        self.display = "0"
        self.state = self.WAITING_FIRST

    def _set_error(self, message: str) -> None:
        self.display = message
        self.current_input = None
        self.first_operand = None
        self.pending_operator = None
        self.state = self.ERROR


class CalculatorUI:
    """Tkinter UI wrapper for CalculatorEngine."""

    def __init__(self, engine: CalculatorEngine | None = None) -> None:
        import tkinter as tk
        from tkinter import font

        self.tk = tk
        self.engine = engine or CalculatorEngine()
        self.root = tk.Tk()
        self.root.title("MiniCalc")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        display_font = font.Font(family="Segoe UI", size=28, weight="bold")
        button_font = font.Font(family="Segoe UI", size=14, weight="bold")

        self.display_var = tk.StringVar(value=self.engine.get_display())
        display = tk.Label(
            self.root,
            textvariable=self.display_var,
            anchor="e",
            bg="#1e1e1e",
            fg="#ffffff",
            font=display_font,
            padx=16,
            pady=18,
            width=12,
        )
        display.grid(row=0, column=0, columnspan=4, sticky="nsew")

        layout = [
            ["C", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="],
        ]

        for row_index, row in enumerate(layout, start=1):
            column_index = 0
            for label in row:
                column_span = 2 if label == "0" else 1
                button = tk.Button(
                    self.root,
                    text=label,
                    font=button_font,
                    bd=0,
                    relief="flat",
                    command=lambda value=label: self.handle_button(value),
                    bg=self._button_color(label),
                    fg="#ffffff",
                    activebackground=self._active_color(label),
                    activeforeground="#ffffff",
                    width=5,
                    height=2,
                )
                button.grid(
                    row=row_index,
                    column=column_index,
                    columnspan=column_span,
                    padx=4,
                    pady=4,
                    sticky="nsew",
                )
                column_index += column_span

        for column in range(4):
            self.root.grid_columnconfigure(column, weight=1, minsize=72)
        for row in range(6):
            self.root.grid_rowconfigure(row, weight=1)

        self.root.bind("<Key>", self.handle_key)

    def run(self) -> None:
        self.root.mainloop()

    def handle_button(self, label: str) -> None:
        operator_map = {"×": "*", "÷": "/"}
        if label.isdigit():
            text = self.engine.press_digit(label)
        elif label == ".":
            text = self.engine.press_decimal()
        elif label in {"+", "-", "×", "÷"}:
            text = self.engine.press_operator(operator_map.get(label, label))
        elif label == "=":
            text = self.engine.press_equals()
        elif label == "C":
            text = self.engine.press_clear()
        elif label == "+/-":
            text = self.engine.press_toggle_sign()
        elif label == "%":
            text = self.engine.press_percent()
        else:
            text = self.engine.get_display()
        self.update_display(text)

    def handle_key(self, event) -> None:
        key = event.keysym
        char = event.char
        if char and char.isdigit():
            text = self.engine.press_digit(char)
        elif char == ".":
            text = self.engine.press_decimal()
        elif char in "+-*/":
            text = self.engine.press_operator(char)
        elif char == "%":
            text = self.engine.press_percent()
        elif key in ("Return", "KP_Enter"):
            text = self.engine.press_equals()
        elif key == "Escape":
            text = self.engine.press_clear()
        elif key == "BackSpace":
            text = self.engine.press_backspace()
        else:
            return
        self.update_display(text)

    def update_display(self, text: str) -> None:
        self.display_var.set(text)

    def _button_color(self, label: str) -> str:
        if label in {"=", "+", "-", "×", "÷"}:
            return "#007acc"
        if label == "C":
            return "#a83232"
        if label in {"+/-", "%"}:
            return "#3a3a3a"
        return "#2d2d2d"

    def _active_color(self, label: str) -> str:
        if label in {"=", "+", "-", "×", "÷"}:
            return "#168ddd"
        if label == "C":
            return "#c23d3d"
        return "#454545"


if __name__ == "__main__":
    CalculatorUI().run()
