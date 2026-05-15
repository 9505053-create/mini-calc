"""Executable Tkinter smoke for MiniCalc PR-05 final release.

Run from repo root with:
    PYTHONPATH=. xvfb-run -a python3 scripts/minicalc_pr5_tk_smoke.py
"""

from __future__ import annotations

from types import SimpleNamespace

from calculator import CalculatorUI


def history_text(ui: CalculatorUI) -> str:
    return ui.history_text.get("1.0", "end-1c")


def press(ui: CalculatorUI, *labels: str) -> None:
    for label in labels:
        ui.handle_button(label)


def key(ui: CalculatorUI, keysym: str, char: str = "") -> None:
    ui.handle_key(SimpleNamespace(keysym=keysym, char=char))


def main() -> None:
    ui = CalculatorUI()
    try:
        ui.root.update_idletasks()
        assert ui.root.title() == "MiniCalc"
        assert ui.display_var.get() == "0"
        assert ui.history_frame.winfo_ismapped() == 1
        assert ui.history_text.cget("state") == "disabled"

        # PR-05 Standard chaining history.
        press(ui, "1", "+", "2", "+")
        ui.root.update_idletasks()
        assert ui.display_var.get() == "3"
        assert history_text(ui) == "[Standard] 1 + 2 = 3"

        press(ui, "3", "=")
        ui.root.update_idletasks()
        assert ui.display_var.get() == "6"
        assert history_text(ui).splitlines()[-1] == "[Standard] 3 + 3 = 6"

        ui.clear_history()
        assert history_text(ui) == ""

        # Operator replacement should not append history.
        press(ui, "AC", "1", "+", "-")
        assert ui.display_var.get() == "1"
        assert history_text(ui) == ""

        # Controlled chaining error and recovery.
        press(ui, "AC", "5", "÷", "0", "+")
        assert ui.display_var.get() == "Error"
        assert history_text(ui) == "[Standard:error] 5 ÷ 0 = Error"
        press(ui, "AC")
        assert ui.display_var.get() == "0"

        # Keyboard Enter history still works.
        ui.clear_history()
        key(ui, "", "8")
        key(ui, "", "/")
        key(ui, "", "4")
        key(ui, "Return", "")
        assert ui.display_var.get() == "2"
        assert history_text(ui) == "[Standard] 8 ÷ 4 = 2"

        # Memory smoke.
        press(ui, "AC", "1", "2", "MS")
        assert ui.memory_indicator_var.get() == "M"
        press(ui, "AC", "MR")
        assert ui.display_var.get() == "12"
        press(ui, "MC")
        assert ui.memory_indicator_var.get() == ""

        # Date smoke.
        ui.set_mode("Date")
        ui.date_start_var.set("2026-05-15")
        ui.date_end_var.set("2026-05-17")
        ui.calculate_date_difference()
        assert ui.display_var.get() == "2 days"
        assert "[Date] 2026-05-15 → 2026-05-17 = 2 days" in history_text(ui)

        # Programmer smoke.
        ui.set_mode("Programmer")
        press(ui, "AC", "2", "5", "5")
        ui.set_base("HEX")
        assert ui.display_var.get() == "FF"
        assert "[Programmer] DEC 255 → HEX = FF" in history_text(ui)

        print("PASS: Tkinter UI instantiated and PR-05 smoke checklist exercised under Xvfb")
    finally:
        ui.root.destroy()


if __name__ == "__main__":
    main()
