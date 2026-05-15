"""Base conversion helpers for MiniCalc programmer mode."""

from __future__ import annotations


class BaseConverter:
    """Validate and convert non-negative integers across common bases."""

    MAX_BITS = 64
    MAX_UNSIGNED_VALUE = (1 << MAX_BITS) - 1
    BASES = {"DEC": 10, "HEX": 16, "BIN": 2, "OCT": 8}
    VALID_DIGITS = {
        "DEC": "0123456789",
        "HEX": "0123456789ABCDEF",
        "BIN": "01",
        "OCT": "01234567",
    }

    def normalize(self, value: str, base: str) -> str:
        self._radix(base)
        text = str(value).strip().upper()
        text = text.lstrip("0")
        return text or "0"

    def is_valid(self, value: str, base: str) -> bool:
        self._radix(base)
        text = str(value).strip().upper()
        return bool(text) and all(char in self.VALID_DIGITS[base] for char in text)

    def convert(self, value: str, from_base: str, to_base: str) -> str:
        from_radix = self._radix(from_base)
        self._radix(to_base)
        text = self.normalize(value, from_base)
        if not self.is_valid(text, from_base):
            raise ValueError(f"invalid {from_base} input")
        number = int(text, from_radix)
        self._ensure_within_limit(number)
        return self._format(number, to_base)

    def convert_all(self, value: str, from_base: str) -> dict[str, str]:
        return {base: self.convert(value, from_base, base) for base in self.BASES}

    def append_digit(self, current: str, digit: str, base: str) -> str:
        radix = self._radix(base)
        char = str(digit).strip().upper()
        if len(char) != 1 or char not in self.VALID_DIGITS[base]:
            return self.normalize(current, base)
        if not self.is_valid(str(current).strip().upper(), base):
            return "0"
        candidate = self.normalize(self.normalize(current, base) + char, base)
        if int(candidate, radix) > self.MAX_UNSIGNED_VALUE:
            return self.normalize(current, base)
        return candidate

    def backspace(self, current: str) -> str:
        text = str(current).strip().upper()
        return text[:-1] or "0"

    def _radix(self, base: str) -> int:
        if base not in self.BASES:
            raise ValueError(f"unsupported base: {base}")
        return self.BASES[base]

    def _ensure_within_limit(self, number: int) -> None:
        if number < 0 or number > self.MAX_UNSIGNED_VALUE:
            raise ValueError(f"value exceeds {self.MAX_BITS}-bit unsigned range")

    def _format(self, number: int, base: str) -> str:
        if base == "DEC":
            return str(number)
        if base == "HEX":
            return format(number, "X")
        if base == "BIN":
            return format(number, "b")
        if base == "OCT":
            return format(number, "o")
        raise ValueError(f"unsupported base: {base}")
