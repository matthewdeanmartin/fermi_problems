"""Tests for fermi_problems.core.estimate.Estimate"""

import math
import pytest
from fermi_problems.units.dimension import Unit
from fermi_problems.core.estimate import Estimate


def test_create_point_estimate():
    e = Estimate(1e6, "people")
    assert e.unit == Unit({"people": 1})
    assert e.value > 0


def test_create_with_range():
    e = Estimate(1e6, "people", low=8e5, high=1.2e6)
    assert e.value == pytest.approx(math.sqrt(8e5 * 1.2e6), rel=0.01)
    assert e.low == 8e5
    assert e.high == 1.2e6


def test_create_with_sig_figs():
    e = Estimate(1e6, "people", sig_figs=2)
    assert e.sig_figs == 2
    assert e.log_std > 0


def test_confidence_interval_round_trip():
    low, high = 100.0, 10000.0
    e = Estimate(1000, "people", low=low, high=high)
    ci_low, ci_high = e.confidence_interval()
    assert ci_low == pytest.approx(low, rel=0.01)
    assert ci_high == pytest.approx(high, rel=0.01)


def test_multiply_estimates():
    a = Estimate(100, "meters")
    b = Estimate(2, "seconds")
    result = a * b
    assert result.unit == Unit({"length": 1, "time": 1})
    assert result.value == pytest.approx(200, rel=0.01)


def test_divide_estimates():
    a = Estimate(100, "meters")
    b = Estimate(10, "seconds")
    result = a / b
    assert result.unit == Unit({"length": 1, "time": -1})
    assert result.value == pytest.approx(10, rel=0.01)


def test_multiply_by_scalar():
    e = Estimate(100, "meters")
    result = e * 3
    assert result.unit == Unit({"length": 1})
    assert result.value == pytest.approx(300, rel=0.01)


def test_uncertainty_propagation_quadrature():
    a = Estimate(100, "meters", sig_figs=2)
    b = Estimate(50, "seconds", sig_figs=2)
    result = a * b
    # log_std should be sqrt(a.log_std^2 + b.log_std^2)
    expected_log_std = math.sqrt(a.log_std**2 + b.log_std**2)
    assert result.log_std == pytest.approx(expected_log_std)


def test_unit_tracking_through_multiplication():
    speed = Estimate(60, "mph")
    time = Estimate(2, "hours")
    distance = speed * time
    # mph = length/time, hours = time, so result = length
    assert distance.unit == Unit({"length": 1})


def test_sig_figs_propagation():
    a = Estimate(1e6, "people", sig_figs=2)
    b = Estimate(0.02, "pianos/person", sig_figs=1)
    result = a * b
    assert result.sig_figs == 1  # min(2, 1)


def test_str_representation():
    e = Estimate(1e6, "people")
    s = str(e)
    assert "people" in s
    assert "~" in s
