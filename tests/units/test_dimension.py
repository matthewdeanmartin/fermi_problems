"""Tests for fermi_problems.units.dimension.Unit"""

from fermi_problems.units.dimension import Unit


def test_dimensionless_creation():
    u = Unit()
    assert u.is_dimensionless
    u2 = Unit(None)
    assert u2.is_dimensionless
    u3 = Unit({})
    assert u3.is_dimensionless


def test_single_dimension():
    u = Unit({"length": 1})
    assert not u.is_dimensionless
    assert u == Unit({"length": 1})


def test_multiply_combines_exponents():
    a = Unit({"length": 1})
    b = Unit({"time": 1})
    c = a * b
    assert c == Unit({"length": 1, "time": 1})


def test_divide_subtracts_exponents():
    a = Unit({"length": 1})
    b = Unit({"time": 1})
    c = a / b
    assert c == Unit({"length": 1, "time": -1})


def test_multiply_to_dimensionless():
    a = Unit({"length": 1})
    b = Unit({"length": -1})
    result = a * b
    assert result.is_dimensionless


def test_power():
    u = Unit({"length": 1})
    assert u**2 == Unit({"length": 2})
    assert u**3 == Unit({"length": 3})
    assert u**-1 == Unit({"length": -1})


def test_inverse():
    u = Unit({"length": 1})
    assert u.inverse() == Unit({"length": -1})

    u2 = Unit({"length": 1, "time": -2})
    assert u2.inverse() == Unit({"length": -1, "time": 2})


def test_zero_exponents_stripped():
    u = Unit({"length": 1, "time": 0})
    assert u == Unit({"length": 1})


def test_equality_and_hash():
    a = Unit({"length": 1, "time": -1})
    b = Unit({"time": -1, "length": 1})  # different insertion order
    assert a == b
    assert hash(a) == hash(b)

    s = {a, b}
    assert len(s) == 1


def test_str_formatting():
    u = Unit({"length": 1, "time": -2})
    s = str(u)
    assert "length" in s
    assert "time" in s
    # numerator/denominator separation
    assert "/" in s


def test_str_dimensionless():
    u = Unit()
    assert str(u) == "dimensionless"


def test_unit_times_unit_dimensionless():
    u = Unit()
    assert (u * u).is_dimensionless


def test_power_zero():
    u = Unit({"length": 2})
    assert (u**0).is_dimensionless
