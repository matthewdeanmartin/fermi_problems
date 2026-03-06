"""Tests for fermi_problems.units.parser.parse_unit"""

import pytest
from fermi_problems.units.dimension import Unit
from fermi_problems.units.parser import parse_unit
from fermi_problems.units.registry import UnknownUnitError


def test_parse_single_unit():
    result = parse_unit("meters")
    assert result.unit == Unit({"length": 1})
    assert result.scale == pytest.approx(1.0)


def test_parse_ratio():
    result = parse_unit("meters/second")
    assert result.unit == Unit({"length": 1, "time": -1})
    assert result.scale == pytest.approx(1.0)


def test_parse_with_exponent():
    result = parse_unit("meters/second^2")
    assert result.unit == Unit({"length": 1, "time": -2})
    assert result.scale == pytest.approx(1.0)


def test_parse_compound_numerator():
    result = parse_unit("km*kg")
    assert result.unit == Unit({"length": 1, "mass": 1})
    assert result.scale == pytest.approx(1000.0)


def test_parse_compound_denominator():
    result = parse_unit("meters/second^2")
    assert result.unit == Unit({"length": 1, "time": -2})


def test_parse_mixed_units_with_conversion():
    result = parse_unit("feet/year")
    assert result.unit == Unit({"length": 1, "time": -1})
    expected_scale = 0.3048 / 31557600.0
    assert result.scale == pytest.approx(expected_scale, rel=1e-4)


def test_parse_dimensionless():
    result = parse_unit("")
    assert result.unit.is_dimensionless
    assert result.scale == 1.0

    result2 = parse_unit("1")
    assert result2.unit.is_dimensionless

    result3 = parse_unit("dimensionless")
    assert result3.unit.is_dimensionless


def test_parse_unknown_unit_raises():
    with pytest.raises(UnknownUnitError):
        parse_unit("widgets")


def test_parse_whitespace_tolerance():
    result = parse_unit("meters / second")
    assert result.unit == Unit({"length": 1, "time": -1})


def test_scale_factor_composition():
    result = parse_unit("km")
    assert result.scale == pytest.approx(1000.0)

    result2 = parse_unit("km^2")
    assert result2.scale == pytest.approx(1000.0**2)
