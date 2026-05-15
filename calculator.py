"""MiniCalc: a small Tkinter calculator with a headless arithmetic engine."""

from __future__ import annotations

from source.base_converter import BaseConverter
from source.calculator_engine import CalculatorEngine


class CalculatorUI:
    """Tkinter UI wrapper for CalculatorEngine."""

    def __init__(self, engine: CalculatorEngine | None = None) -> None:
        import tkinter as tk
        from tkinter import font

        self.tk = tk
        self.engine = engine or CalculatorEngine()
        self.base_converter = BaseConverter()
        self.mode = "Standard"
        self.current_base = "DEC"
        self.programmer_value = "0"
        self.base_buttons = {}
        self.hex_buttons = []
        self.root = tk.Tk()
        self.root.title("MiniCalc")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        display_font = font.Font(family="Segoe UI", size=28, weight="bold")
        button_font = font.Font(family="Segoe UI", size=14, weight="bold")
        small_button_font = font.Font(family="Segoe UI", size=10, weight="bold")

        self.mode_buttons = {}
        for column, label in enumerate(("Standard", "Programmer")):
            button = tk.Button(
                self.root,
                text=label,
                font=small_button_font,
                bd=0,
                relief="flat",
                command=lambda value=label: self.set_mode(value),
                bg="#3a3a3a",
                fg="#ffffff",
                activebackground="#454545",
                activeforeground="#ffffff",
                height=2,
            )
            button.grid(row=0, column=column * 2, columnspan=2, padx=4, pady=4, sticky="nsew")
            self.mode_buttons[label] = button

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
        display.grid(row=1, column=0, columnspan=4, sticky="nsew")

        for column, label in enumerate(("DEC", "HEX", "BIN", "OCT")):
            button = tk.Button(
                self.root,
                text=label,
                font=small_button_font,
                bd=0,
                relief="flat",
                command=lambda value=label: self.set_base(value),
                bg="#3a3a3a",
                fg="#ffffff",
                activebackground="#454545",
                activeforeground="#ffffff",
                height=2,
            )
            button.grid(row=2, column=column, padx=4, pady=4, sticky="nsew")
            self.base_buttons[label] = button

        layout = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="],
        ]
        self.buttons = {}

        for row_index, row in enumerate(layout, start=3):
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
                self.buttons[label] = button
                column_index += column_span

        for index, label in enumerate(("A", "B", "C", "D", "E", "F")):
            row_index = 8 + (index // 3)
            column_index = index % 3
            button = tk.Button(
                self.root,
                text=label,
                font=button_font,
                bd=0,
                relief="flat",
                command=lambda value=label: self.handle_button(value),
                bg="#2d2d2d",
                fg="#ffffff",
                activebackground="#454545",
                activeforeground="#ffffff",
                width=5,
                height=2,
            )
            button.grid(row=row_index, column=column_index, padx=4, pady=4, sticky="nsew")
            self.hex_buttons.append(button)

        for column in range(4):
            self.root.grid_columnconfigure(column, weight=1, minsize=72)
        for row in range(10):
            self.root.grid_rowconfigure(row, weight=1)

        self.root.bind("<Key>", self.handle_key)
        self._refresh_mode_controls()

    def run(self) -> None:
        self.root.mainloop()

    def handle_button(self, label: str) -> None:
        if self.mode == "Programmer":
            self._handle_programmer_button(label)
            return

        operator_map = {"×": "*", "÷": "/"}
        if label.isdigit():
            text = self.engine.press_digit(label)
        elif label == ".":
            text = self.engine.press_decimal()
        elif label in {"+", "-", "×", "÷"}:
            text = self.engine.press_operator(operator_map.get(label, label))
        elif label == "=":
            text = self.engine.press_equals()
        elif label in {"CLEAR", "AC"}:
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
        if self.mode == "Programmer":
            self._handle_programmer_key(key, char)
            return

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

    def set_mode(self, mode: str) -> None:
        if mode not in {"Standard", "Programmer"}:
            return
        if mode == self.mode:
            return
        self.mode = mode
        if mode == "Programmer":
            display = self.engine.get_display()
            self.current_base = "DEC"
            self.programmer_value = display if display.isdigit() else "0"
            text = self.programmer_value
        else:
            text = self.engine.get_display()
        self._refresh_mode_controls()
        self.update_display(text)

    def set_base(self, base: str) -> None:
        if self.mode != "Programmer" or base == self.current_base:
            return
        try:
            self.programmer_value = self.base_converter.convert(
                self.programmer_value, self.current_base, base
            )
        except ValueError:
            return
        self.current_base = base
        self._refresh_mode_controls()
        self.update_display(self.programmer_value)

    def update_display(self, text: str) -> None:
        self.display_var.set(text)

    def _handle_programmer_button(self, label: str) -> None:
        if label in BaseConverter.BASES:
            self.set_base(label)
            return
        if label in {"CLEAR", "AC"}:
            self.programmer_value = "0"
        elif label in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"}:
            self.programmer_value = self.base_converter.append_digit(
                self.programmer_value, label, self.current_base
            )
        elif label == "BS":
            self.programmer_value = self.base_converter.backspace(self.programmer_value)
        else:
            return
        self.update_display(self.programmer_value)

    def _handle_programmer_key(self, key: str, char: str) -> None:
        if char:
            upper = char.upper()
            if upper in BaseConverter.VALID_DIGITS["HEX"]:
                self._handle_programmer_button(upper)
                return
        if key == "Escape":
            self._handle_programmer_button("CLEAR")
        elif key == "BackSpace":
            self._handle_programmer_button("BS")

    def _refresh_mode_controls(self) -> None:
        for label, button in self.mode_buttons.items():
            button.configure(bg="#007acc" if label == self.mode else "#3a3a3a")
        for label, button in self.base_buttons.items():
            button.configure(
                bg="#007acc" if label == self.current_base and self.mode == "Programmer" else "#3a3a3a",
                state="normal" if self.mode == "Programmer" else "disabled",
            )
        for label, button in self.buttons.items():
            enabled = True
            if self.mode == "Programmer":
                if label in {".", "%", "+/-", "=", "+", "-", "×", "÷"}:
                    enabled = False
                elif label.isdigit():
                    enabled = label in BaseConverter.VALID_DIGITS[self.current_base]
            button.configure(state="normal" if enabled else "disabled")
        for button in self.hex_buttons:
            label = button.cget("text")
            if self.mode == "Programmer":
                button.grid()
                button.configure(
                    state="normal" if label in BaseConverter.VALID_DIGITS[self.current_base] else "disabled"
                )
            else:
                button.grid_remove()

    def _button_color(self, label: str) -> str:
        if label in {"=", "+", "-", "×", "÷"}:
            return "#007acc"
        if label == "AC":
            return "#a83232"
        if label in {"+/-", "%"}:
            return "#3a3a3a"
        return "#2d2d2d"

    def _active_color(self, label: str) -> str:
        if label in {"=", "+", "-", "×", "÷"}:
            return "#168ddd"
        if label == "AC":
            return "#c23d3d"
        return "#454545"


if __name__ == "__main__":
    CalculatorUI().run()
