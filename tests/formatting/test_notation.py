"""Tests for fermi_problems.formatting.notation"""

from fermi_problems.formatting.notation import (
    to_scientific,
    to_engineering,
    to_human,
    to_order_of_magnitude,
)


def test_to_scientific():
    assert to_scientific(1234567, 3) == "1.23e+06"
    assert to_scientific(0.001234, 3) == "1.23e-03"
    assert to_scientific(1.0, 1) == "1e+00"


def test_to_engineering_with_suffixes():
    s = to_engineering(1234567, 3)
    assert "M" in s
    s2 = to_engineering(1234, 3)
    assert "k" in s2
    s3 = to_engineering(1.5e9, 2)
    assert "B" in s3


def test_to_human_small():
    s = to_human(42, 2)
    assert "42" in s


def test_to_human_large():
    s = to_human(1.5e6, 2)
    assert "M" in s or "1.5" in s


def test_to_human_very_large():
    s = to_human(3e23, 2)
    # Should use scientific notation
    assert "e" in s or "E" in s


def test_to_order_of_magnitude():
    assert to_order_of_magnitude(1.5e6) == "~10^6"
    assert to_order_of_magnitude(1e3) == "~10^3"
    assert to_order_of_magnitude(1) == "~10^0"
