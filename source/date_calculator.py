"""Date arithmetic helpers for MiniCalc Date Mode."""

from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Any


class DateCalculator:
    """Parse ISO dates and perform deterministic date arithmetic."""

    def parse_date(self, text: str) -> date:
        """Parse an ISO YYYY-MM-DD date string."""
        try:
            return date.fromisoformat(str(text).strip())
        except ValueError as exc:
            raise ValueError("invalid ISO date; expected YYYY-MM-DD") from exc

    def days_between(self, start: str, end: str) -> int:
        """Return day difference as end_date - start_date."""
        start_date = self.parse_date(start)
        end_date = self.parse_date(end)
        return (end_date - start_date).days

    def add_duration(
        self,
        base_date: str,
        *,
        years: Any = 0,
        months: Any = 0,
        weeks: Any = 0,
        days: Any = 0,
        operation: str = "add",
    ) -> str:
        """Add or subtract a duration and return an ISO date string.

        Duration is applied deterministically in this order:
        years, months, then weeks/days.
        """
        if operation not in {"add", "subtract"}:
            raise ValueError("operation must be 'add' or 'subtract'")
        sign = 1 if operation == "add" else -1
        year_count = self._duration_component(years)
        month_count = self._duration_component(months)
        week_count = self._duration_component(weeks)
        day_count = self._duration_component(days)

        result = self.parse_date(base_date)
        if year_count:
            result = self._add_years(result, sign * year_count)
        if month_count:
            result = self._add_months(result, sign * month_count)
        day_delta = sign * ((week_count * 7) + day_count)
        if day_delta:
            result = result + timedelta(days=day_delta)
        return result.isoformat()

    def _duration_component(self, value: Any) -> int:
        if isinstance(value, str):
            text = value.strip()
            if text == "":
                return 0
            if not text.isdigit():
                raise ValueError("duration components must be non-negative integers")
            return int(text)
        try:
            number = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("duration components must be non-negative integers") from exc
        if number < 0 or number != value:
            raise ValueError("duration components must be non-negative integers")
        return number

    def _add_years(self, current: date, years: int) -> date:
        target_year = current.year + years
        return self._replace_clamped(current, target_year, current.month)

    def _add_months(self, current: date, months: int) -> date:
        month_index = current.year * 12 + (current.month - 1) + months
        target_year, zero_based_month = divmod(month_index, 12)
        target_month = zero_based_month + 1
        return self._replace_clamped(current, target_year, target_month)

    def _replace_clamped(self, current: date, year: int, month: int) -> date:
        last_day = calendar.monthrange(year, month)[1]
        return current.replace(year=year, month=month, day=min(current.day, last_day))
