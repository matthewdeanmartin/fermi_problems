"""Tests for fermi_problems.core.quantity.Quantity"""

import pytest
from fermi_problems.units.dimension import Unit
from fermi_problems.core.quantity import Quantity, DimensionError


def test_create_with_string_unit():
    q = Quantity(10, "meters")
    assert q.unit == Unit({"length": 1})
    assert q.value == pytest.approx(10.0)


def test_create_with_unit_object():
    u = Unit({"length": 1})
    q = Quantity(5.0, u)
    assert q.unit == u
    assert q.value == pytest.approx(5.0)


def test_multiply_quantities():
    q1 = Quantity(3.0, "meters")
    q2 = Quantity(4.0, "seconds")
    result = q1 * q2
    assert result.unit == Unit({"length": 1, "time": 1})
    assert result.value == pytest.approx(12.0)


def test_divide_quantities():
    q1 = Quantity(10.0, "meters")
    q2 = Quantity(2.0, "seconds")
    result = q1 / q2
    assert result.unit == Unit({"length": 1, "time": -1})
    assert result.value == pytest.approx(5.0)


def test_multiply_by_scalar():
    q = Quantity(5.0, "meters")
    result = q * 3
    assert result.unit == Unit({"length": 1})
    assert result.value == pytest.approx(15.0)

    result2 = 3 * q
    assert result2.value == pytest.approx(15.0)


def test_divide_by_scalar():
    q = Quantity(10.0, "meters")
    result = q / 2
    assert result.value == pytest.approx(5.0)


def test_add_same_units():
    q1 = Quantity(3.0, "meters")
    q2 = Quantity(4.0, "meters")
    result = q1 + q2
    assert result.value == pytest.approx(7.0)
    assert result.unit == Unit({"length": 1})


def test_add_compatible_units_converts():
    q1 = Quantity(1.0, "meters")
    q2 = Quantity(1.0, "feet")
    # Both convert to SI (meters), then add
    # q1.value = 1.0, q2.value = 0.3048
    result = q1 + q2
    assert result.value == pytest.approx(1.0 + 0.3048)


def test_add_incompatible_units_raises():
    q1 = Quantity(1.0, "meters")
    q2 = Quantity(1.0, "seconds")
    with pytest.raises(DimensionError):
        q1 + q2


def test_in_unit_conversion():
    q = Quantity(1.0, "miles")
    feet = q.in_unit("feet")
    assert feet == pytest.approx(5280.0, rel=1e-3)


def test_to_conversion():
    q = Quantity(1000.0, "meters")
    q2 = q.to("km")
    assert q2.value == pytest.approx(1000.0)  # SI value unchanged
    assert q2.in_unit("km") == pytest.approx(1.0)


def test_multiply_to_dimensionless():
    q1 = Quantity(10.0, "meters")
    q2 = Quantity(2.0, "meters")
    result = q1 / q2
    assert result.unit.is_dimensionless
    assert result.value == pytest.approx(5.0)


def test_str_representation():
    q = Quantity(3.0, "meters")
    s = str(q)
    assert "3" in s
    assert "meters" in s
