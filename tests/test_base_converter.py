import pathlib
import sys

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "source"))

from base_converter import BaseConverter


def test_decimal_conversions():
    converter = BaseConverter()
    assert converter.convert("255", "DEC", "HEX") == "FF"
    assert converter.convert("10", "DEC", "BIN") == "1010"
    assert converter.convert("8", "DEC", "OCT") == "10"


def test_convert_to_decimal():
    converter = BaseConverter()
    assert converter.convert("FF", "HEX", "DEC") == "255"
    assert converter.convert("1010", "BIN", "DEC") == "10"
    assert converter.convert("10", "OCT", "DEC") == "8"


def test_hex_input_is_uppercase():
    converter = BaseConverter()
    assert converter.normalize("ff", "HEX") == "FF"
    assert converter.convert("ff", "HEX", "DEC") == "255"
    assert converter.convert("255", "DEC", "HEX") == "FF"


def test_leading_zeroes_normalize():
    converter = BaseConverter()
    assert converter.normalize("000F", "HEX") == "F"
    assert converter.normalize("0000", "DEC") == "0"


@pytest.mark.parametrize(
    ("value", "base"),
    [("2", "BIN"), ("8", "OCT"), ("A", "DEC"), ("G", "HEX")],
)
def test_invalid_digits_are_rejected(value, base):
    converter = BaseConverter()
    assert not converter.is_valid(value, base)
    with pytest.raises(ValueError):
        converter.convert(value, base, "DEC")


def test_unsupported_base_raises():
    converter = BaseConverter()
    with pytest.raises(ValueError):
        converter.convert("10", "DEC", "BASE3")


def test_append_digit_ignores_invalid_input():
    converter = BaseConverter()
    assert converter.append_digit("10", "2", "BIN") == "10"
    assert converter.append_digit("10", "F", "HEX") == "10F"


def test_empty_input_is_invalid():
    converter = BaseConverter()
    assert not converter.is_valid("", "DEC")
    assert converter.normalize("", "DEC") == "0"


def test_convert_all_returns_all_bases():
    converter = BaseConverter()
    assert converter.convert_all("15", "DEC") == {
        "DEC": "15",
        "HEX": "F",
        "BIN": "1111",
        "OCT": "17",
    }


def test_backspace_returns_zero_when_empty():
    converter = BaseConverter()
    assert converter.backspace("F") == "0"
    assert converter.backspace("FF") == "F"
