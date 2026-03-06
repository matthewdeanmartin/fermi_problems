"""Tests for fermi_problems.units.registry.UnitRegistry"""

import pytest
from fermi_problems.units.registry import UnitRegistry, UnitDef, UnknownUnitError


def test_lookup_known_unit():
    reg = UnitRegistry()
    ud = reg.lookup("meters")
    assert ud.scale == 1.0
    assert ud.dimensions == {"length": 1}


def test_lookup_alias():
    reg = UnitRegistry()
    m = reg.lookup("m")
    meter = reg.lookup("meter")
    meters = reg.lookup("meters")
    assert m.scale == meter.scale == meters.scale


def test_lookup_case_insensitive():
    reg = UnitRegistry()
    ud = reg.lookup("Meters")
    assert ud.scale == 1.0
    ud2 = reg.lookup("METERS")
    assert ud2.scale == 1.0


def test_lookup_unknown_raises():
    reg = UnitRegistry()
    with pytest.raises(UnknownUnitError):
        reg.lookup("widgets")


def test_register_custom_unit():
    reg = UnitRegistry()
    ud = UnitDef({"widgets": 1}, 1.0, "widgets")
    reg.register("widgets", ud)
    result = reg.lookup("widgets")
    assert result.dimensions == {"widgets": 1}


def test_auto_register_counting_unit():
    reg = UnitRegistry()
    ud = reg.auto_register_counting_unit("sprockets")
    assert ud.dimensions == {"sprockets": 1}
    assert ud.scale == 1.0
    # Can look it up now
    assert reg.lookup("sprockets") == ud


def test_scale_factors_consistent():
    """feet * scale should equal 0.3048 meters."""
    reg = UnitRegistry()
    feet_ud = reg.lookup("feet")
    meters_ud = reg.lookup("meters")
    assert abs(feet_ud.scale / meters_ud.scale - 0.3048) < 1e-6


def test_aliases_returns_all_names():
    reg = UnitRegistry()
    aliases = reg.aliases("meters")
    assert "m" in aliases
    assert "meter" in aliases
    assert "meters" in aliases
