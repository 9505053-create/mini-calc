import pytest

from source.date_calculator import DateCalculator


def test_days_between_adjacent_dates():
    calc = DateCalculator()
    assert calc.days_between("2026-05-15", "2026-05-16") == 1


def test_days_between_same_date_is_zero():
    calc = DateCalculator()
    assert calc.days_between("2026-05-15", "2026-05-15") == 0


def test_days_between_allows_negative_result():
    calc = DateCalculator()
    assert calc.days_between("2026-05-16", "2026-05-15") == -1


def test_days_between_leap_year_boundary():
    calc = DateCalculator()
    assert calc.days_between("2024-02-28", "2024-03-01") == 2


def test_invalid_date_raises_value_error():
    calc = DateCalculator()
    with pytest.raises(ValueError):
        calc.days_between("2026-02-30", "2026-03-01")


def test_add_days():
    calc = DateCalculator()
    assert calc.add_duration("2026-05-15", days=10) == "2026-05-25"


def test_subtract_weeks():
    calc = DateCalculator()
    assert calc.add_duration("2026-05-15", weeks=2, operation="subtract") == "2026-05-01"


def test_add_month_clamps_leap_year_february():
    calc = DateCalculator()
    assert calc.add_duration("2024-01-31", months=1) == "2024-02-29"


def test_add_month_clamps_non_leap_february():
    calc = DateCalculator()
    assert calc.add_duration("2025-01-31", months=1) == "2025-02-28"


def test_subtract_month_clamps_end_of_month():
    calc = DateCalculator()
    assert calc.add_duration("2024-03-31", months=1, operation="subtract") == "2024-02-29"


def test_add_year_from_leap_day_clamps():
    calc = DateCalculator()
    assert calc.add_duration("2024-02-29", years=1) == "2025-02-28"


def test_subtract_year_from_leap_day_clamps():
    calc = DateCalculator()
    assert calc.add_duration("2024-02-29", years=1, operation="subtract") == "2023-02-28"


def test_multi_component_duration_applies_years_months_then_days():
    calc = DateCalculator()
    assert calc.add_duration("2024-01-31", years=1, months=1, days=5) == "2025-03-05"


def test_month_rollover_beyond_one_year():
    calc = DateCalculator()
    assert calc.add_duration("2024-01-31", months=13) == "2025-02-28"


@pytest.mark.parametrize("component", ["abc", "1.5", "-1"])
def test_invalid_duration_component_raises_value_error(component):
    calc = DateCalculator()
    with pytest.raises(ValueError):
        calc.add_duration("2026-05-15", days=component)


@pytest.mark.parametrize("component", ["", "   "])
def test_empty_duration_component_is_zero(component):
    calc = DateCalculator()
    assert calc.add_duration("2026-05-15", days=component) == "2026-05-15"


def test_invalid_operation_raises_value_error():
    calc = DateCalculator()
    with pytest.raises(ValueError):
        calc.add_duration("2026-05-15", days=1, operation="multiply")
