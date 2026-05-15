"""MiniCalc: a small Tkinter calculator with headless mode controllers."""

from __future__ import annotations

from source.base_converter import BaseConverter
from source.calculator_engine import CalculatorEngine
from source.memory_store import MemoryStore
from source.mode_controllers import DateModeController, ProgrammerModeController, StandardModeController


class CalculatorUI:
    """Tkinter UI wrapper that delegates mode logic to headless controllers."""

    def __init__(self, engine: CalculatorEngine | None = None) -> None:
        import tkinter as tk
        from tkinter import font

        self.tk = tk
        self.engine = engine or CalculatorEngine()
        self.memory = MemoryStore()
        self.base_converter = BaseConverter()
        self.standard_controller = StandardModeController(self.engine, self.memory)
        self.programmer_controller = ProgrammerModeController(self.base_converter)
        self.date_controller = DateModeController()
        self.mode = "Standard"
        self.current_base = self.programmer_controller.current_base
        self.programmer_value = self.programmer_controller.programmer_value

        self.base_buttons = {}
        self.hex_buttons = []
        self.memory_buttons = {}
        self.date_widgets = []

        self.root = tk.Tk()
        self.root.title("MiniCalc")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        display_font = font.Font(family="Segoe UI", size=28, weight="bold")
        button_font = font.Font(family="Segoe UI", size=14, weight="bold")
        small_button_font = font.Font(family="Segoe UI", size=10, weight="bold")

        self.mode_buttons = {}
        mode_layout = (("Standard", 0, 2), ("Programmer", 2, 2), ("Date", 4, 1))
        for label, column, column_span in mode_layout:
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
            button.grid(row=0, column=column, columnspan=column_span, padx=4, pady=4, sticky="nsew")
            self.mode_buttons[label] = button

        self.memory_indicator_var = tk.StringVar(value="")
        memory_indicator = tk.Label(
            self.root,
            textvariable=self.memory_indicator_var,
            anchor="center",
            bg="#1e1e1e",
            fg="#f0c674",
            font=small_button_font,
            width=2,
        )
        memory_indicator.grid(row=1, column=0, sticky="nsew")

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
        display.grid(row=1, column=1, columnspan=4, sticky="nsew")

        for column, label in enumerate(("MC", "MR", "MS", "M+", "M-")):
            button = tk.Button(
                self.root,
                text=label,
                font=small_button_font,
                bd=0,
                relief="flat",
                command=lambda value=label: self.handle_button(value),
                bg="#3a3a3a",
                fg="#ffffff",
                activebackground="#454545",
                activeforeground="#ffffff",
                height=2,
            )
            button.grid(row=2, column=column, padx=4, pady=4, sticky="nsew")
            self.memory_buttons[label] = button

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
            button.grid(row=3, column=column, padx=4, pady=4, sticky="nsew")
            self.base_buttons[label] = button

        layout = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="],
        ]
        self.buttons = {}
        for row_index, row in enumerate(layout, start=4):
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
            row_index = 9 + (index // 3)
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

        self._build_date_widgets(tk, small_button_font)

        for column in range(5):
            self.root.grid_columnconfigure(column, weight=1, minsize=72)
        for row in range(13):
            self.root.grid_rowconfigure(row, weight=1)

        self.root.bind("<Key>", self.handle_key)
        self._refresh_mode_controls()

    def _build_date_widgets(self, tk, small_button_font) -> None:
        self.date_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.date_frame.grid(row=11, column=0, columnspan=5, padx=4, pady=4, sticky="nsew")

        self.date_start_var = tk.StringVar(value="2026-05-15")
        self.date_end_var = tk.StringVar(value="2026-05-16")
        self.date_base_var = tk.StringVar(value="2026-05-15")
        self.date_operation_var = tk.StringVar(value="add")
        self.date_years_var = tk.StringVar(value="0")
        self.date_months_var = tk.StringVar(value="0")
        self.date_weeks_var = tk.StringVar(value="0")
        self.date_days_var = tk.StringVar(value="0")

        def label(text: str, row: int, column: int) -> None:
            tk.Label(self.date_frame, text=text, font=small_button_font, bg="#1e1e1e", fg="#ffffff").grid(
                row=row, column=column, padx=2, pady=2, sticky="w"
            )

        def entry(variable, row: int, column: int, width: int = 10) -> None:
            tk.Entry(self.date_frame, textvariable=variable, width=width).grid(
                row=row, column=column, padx=2, pady=2, sticky="ew"
            )

        label("Diff", 0, 0)
        entry(self.date_start_var, 0, 1)
        entry(self.date_end_var, 0, 2)
        tk.Button(self.date_frame, text="Calculate", command=self.calculate_date_difference).grid(
            row=0, column=3, padx=2, pady=2, sticky="ew"
        )

        label("Date +/-", 1, 0)
        entry(self.date_base_var, 1, 1)
        tk.OptionMenu(self.date_frame, self.date_operation_var, "add", "subtract").grid(
            row=1, column=2, padx=2, pady=2, sticky="ew"
        )
        tk.Button(self.date_frame, text="Calculate", command=self.calculate_date_duration).grid(
            row=1, column=3, padx=2, pady=2, sticky="ew"
        )

        for column, (name, variable) in enumerate(
            (("Y", self.date_years_var), ("M", self.date_months_var), ("W", self.date_weeks_var), ("D", self.date_days_var))
        ):
            label(name, 2, column)
            entry(variable, 3, column, width=5)

    def run(self) -> None:
        self.root.mainloop()

    def handle_button(self, label: str) -> None:
        if self.mode == "Programmer":
            self._handle_programmer_button(label)
            return
        if self.mode == "Date":
            return
        text = self.standard_controller.handle_button(label)
        self.update_display(text)

    def handle_key(self, event) -> None:
        key = event.keysym
        char = event.char
        if self.mode == "Programmer":
            self._handle_programmer_key(key, char)
            return
        if self.mode == "Date":
            return
        text = self.standard_controller.handle_key(key, char)
        if text is not None:
            self.update_display(text)

    def set_mode(self, mode: str) -> None:
        if mode not in {"Standard", "Programmer", "Date"}:
            return
        if mode == self.mode:
            return
        self.mode = mode
        if mode == "Programmer":
            text = self.programmer_controller.enter(self.engine.get_display())
            self._sync_programmer_state()
        elif mode == "Date":
            text = self.date_controller.enter(self.display_var.get())
        else:
            text = self.standard_controller.enter()
        self._refresh_mode_controls()
        self.update_display(text)

    def set_base(self, base: str) -> None:
        if self.mode != "Programmer" or base == self.current_base:
            return
        try:
            text = self.programmer_controller.set_base(base)
        except ValueError:
            return
        self._sync_programmer_state()
        self._refresh_mode_controls()
        self.update_display(text)

    def calculate_date_difference(self) -> None:
        text = self.date_controller.calculate_difference(
            self.date_start_var.get(), self.date_end_var.get()
        )
        self.update_display(text)

    def calculate_date_duration(self) -> None:
        text = self.date_controller.calculate_duration(
            self.date_base_var.get(),
            operation=self.date_operation_var.get(),
            years=self.date_years_var.get(),
            months=self.date_months_var.get(),
            weeks=self.date_weeks_var.get(),
            days=self.date_days_var.get(),
        )
        self.update_display(text)

    def update_display(self, text: str) -> None:
        self.display_var.set(text)
        if hasattr(self, "memory_indicator_var"):
            self.memory_indicator_var.set("M" if self.memory.has_value else "")

    def _sync_programmer_state(self) -> None:
        self.current_base = self.programmer_controller.current_base
        self.programmer_value = self.programmer_controller.programmer_value

    def _handle_programmer_button(self, label: str) -> None:
        if hasattr(self, "programmer_controller"):
            self.programmer_controller.current_base = self.current_base
            self.programmer_controller.programmer_value = self.programmer_value
            text = self.programmer_controller.handle_button(label)
            self._sync_programmer_state()
            self.update_display(text)
            return
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
        if hasattr(self, "programmer_controller"):
            text = self.programmer_controller.handle_key(key, char)
            if text is not None:
                self._sync_programmer_state()
                self.update_display(text)
            return
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
        for button in getattr(self, "memory_buttons", {}).values():
            button.configure(state="normal" if self.mode == "Standard" else "disabled")

        programmer_states = None
        if hasattr(self, "programmer_controller"):
            self.programmer_controller.current_base = self.current_base
            programmer_states = self.programmer_controller.button_states()
        for label, button in self.buttons.items():
            enabled = self.mode == "Standard"
            if self.mode == "Programmer":
                if programmer_states is not None and label in programmer_states:
                    enabled = programmer_states[label] == "normal"
                elif label.isdigit():
                    enabled = label in BaseConverter.VALID_DIGITS[self.current_base]
                else:
                    enabled = label == "AC"
            if self.mode == "Date":
                enabled = False
            button.configure(state="normal" if enabled else "disabled")

        for button in self.hex_buttons:
            label = button.cget("text")
            if self.mode == "Programmer":
                button.grid()
                state = "normal" if label in BaseConverter.VALID_DIGITS[self.current_base] else "disabled"
                button.configure(state=state)
            else:
                button.grid_remove()

        if hasattr(self, "date_frame"):
            if self.mode == "Date":
                self.date_frame.grid()
            else:
                self.date_frame.grid_remove()

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
