import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from calculator import CalculatorEngine


def press_sequence(engine, sequence):
    display = engine.get_display()
    for item in sequence:
        if item.isdigit():
            display = engine.press_digit(item)
        elif item == ".":
            display = engine.press_decimal()
        elif item in "+-*/":
            display = engine.press_operator(item)
        elif item == "=":
            display = engine.press_equals()
        elif item == "C":
            display = engine.press_clear()
        elif item == "+/-":
            display = engine.press_toggle_sign()
        elif item == "%":
            display = engine.press_percent()
        elif item == "BS":
            display = engine.press_backspace()
    return display


def test_basic_addition():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["2", "+", "3", "="]) == "5"


def test_basic_subtraction():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["1", "0", "-", "4", "="]) == "6"


def test_basic_multiplication():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["6", "*", "7", "="]) == "42"


def test_basic_division():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["8", "/", "2", "="]) == "4"


def test_divide_by_zero_and_clear_recovery():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["5", "/", "0", "="]) == "Error"
    assert engine.get_state() == CalculatorEngine.ERROR
    assert engine.press_digit("1") == "Error"
    assert engine.press_clear() == "0"
    assert engine.get_state() == CalculatorEngine.WAITING_FIRST


def test_float_precision_is_normalized():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["0", ".", "1", "+", "0", ".", "2", "="]) == "0.3"


def test_continuous_operations_compute_on_second_operator():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["1", "+", "2", "+"]) == "3"
    assert press_sequence(engine, ["3", "="]) == "6"


def test_negative_result():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["3", "-", "5", "="]) == "-2"


def test_consecutive_operators_replace_pending_operator():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["5", "+", "-", "2", "="]) == "3"


def test_decimal_guard_ignores_second_decimal_point():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["1", ".", ".", "2"]) == "1.2"


def test_result_continuation():
    engine = CalculatorEngine()
    assert press_sequence(engine, ["2", "+", "3", "="]) == "5"
    assert press_sequence(engine, ["*", "4", "="]) == "20"


def test_large_result_uses_scientific_notation():
    engine = CalculatorEngine()
    result = press_sequence(
        engine,
        ["9", "9", "9", "9", "9", "9", "9", "*", "9", "9", "9", "9", "9", "9", "9", "="],
    )
    assert "e+" in result


# ══════════════════════════════════════════════════════════════
# PR-01 v1.1 Regression Tests
# ══════════════════════════════════════════════════════════════

class TestScientificNotationFix:
    """P0: Scientific notation should NOT trigger for numbers that fit with fewer decimals."""

    def test_100000_div_3_no_scientific(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "0", "0", "0", "0", "0", "/", "3", "="])
        assert "e+" not in result
        assert result.startswith("33333")

    def test_1000000_div_3_no_scientific(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "0", "0", "0", "0", "0", "0", "/", "3", "="])
        assert "e+" not in result
        assert result.startswith("333333")

    def test_10000_div_3_correct(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "0", "0", "0", "0", "/", "3", "="])
        assert result == "3333.33333333"

    def test_very_large_int_still_scientific(self):
        """Numbers whose integer part alone exceeds 12 digits should still use scientific."""
        engine = CalculatorEngine()
        result = press_sequence(
            engine,
            ["9", "9", "9", "9", "9", "9", "9", "*", "9", "9", "9", "9", "9", "9", "9", "="],
        )
        assert "e+" in result


class TestPercentLogic:
    """P1: Percentage should follow mainstream calculator behavior."""

    def test_100_plus_10_percent(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "0", "0", "+", "1", "0", "%"])
        assert result == "110"

    def test_100_minus_10_percent(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "0", "0", "-", "1", "0", "%"])
        assert result == "90"

    def test_200_multiply_10_percent(self):
        engine = CalculatorEngine()
        # For *, % just computes y/100. Then = computes the multiplication.
        result = press_sequence(engine, ["2", "0", "0", "*", "1", "0", "%"])
        assert result == "0.1"
        result = press_sequence(engine, ["="])
        assert result == "20"

    def test_percent_alone(self):
        """Without pending operator, % just divides by 100."""
        engine = CalculatorEngine()
        result = press_sequence(engine, ["5", "0", "%"])
        assert result == "0.5"


class TestBackspace:
    """P1: Backspace should remove last digit."""

    def test_backspace_single_digit(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "2", "3", "BS"])
        assert result == "12"

    def test_backspace_to_zero(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["5", "BS"])
        assert result == "0"

    def test_backspace_negative(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "2", "+/-", "BS"])
        assert result == "-0" or result == "0" or result == "-1"

    def test_backspace_on_result_noop(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["1", "+", "2", "=", "BS"])
        assert result == "3"

    def test_backspace_after_error_noop(self):
        engine = CalculatorEngine()
        result = press_sequence(engine, ["5", "/", "0", "=", "BS"])
        assert result == "Error"


class TestNegativeZero:
    """P2: Toggling sign on 0 should not show -0."""

    def test_toggle_sign_on_zero(self):
        engine = CalculatorEngine()
        result = engine.press_toggle_sign()
        assert result == "0"

    def test_toggle_sign_on_zero_decimal(self):
        engine = CalculatorEngine()
        engine.press_decimal()
        result = engine.press_toggle_sign()
        assert result == "0."

    def test_toggle_sign_on_negative_zero(self):
        engine = CalculatorEngine()
        engine.press_toggle_sign()
        result = engine.press_toggle_sign()
        assert result == "0"
