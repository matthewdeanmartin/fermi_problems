"""Tests for fermi_problems.uncertainty.lognormal"""

import math
import pytest
from fermi_problems.uncertainty.lognormal import (
    normal_ppf,
    lognormal_from_range,
    lognormal_point_estimate,
    lognormal_confidence_interval,
    combine_lognormals_product,
    lognormal_from_point_estimate,
)


def test_normal_ppf_symmetry():
    assert normal_ppf(0.5) == 0.0
    assert normal_ppf(0.95) == pytest.approx(-normal_ppf(0.05), rel=1e-4)
    assert normal_ppf(0.975) == pytest.approx(-normal_ppf(0.025), rel=1e-4)


def test_normal_ppf_known_values():
    assert normal_ppf(0.95) == pytest.approx(1.645, abs=0.01)
    assert normal_ppf(0.975) == pytest.approx(1.96, abs=0.01)
    assert normal_ppf(0.5) == 0.0


def test_lognormal_from_range():
    # 90% CI: [10, 1000]
    log_mean, log_std = lognormal_from_range(10, 1000, confidence=0.90)
    # Geometric mean should be sqrt(10 * 1000) = 100
    assert math.exp(log_mean) == pytest.approx(100.0, rel=1e-3)
    assert log_std > 0


def test_lognormal_from_range_round_trip():
    low, high = 100, 10000
    log_mean, log_std = lognormal_from_range(low, high, confidence=0.90)
    ci_low, ci_high = lognormal_confidence_interval(log_mean, log_std, confidence=0.90)
    assert ci_low == pytest.approx(low, rel=1e-3)
    assert ci_high == pytest.approx(high, rel=1e-3)


def test_lognormal_point_estimate():
    assert lognormal_point_estimate(math.log(100)) == pytest.approx(100.0)


def test_combine_lognormals_product():
    params = [(math.log(10), 0.5), (math.log(100), 0.3)]
    combined_mean, combined_std = combine_lognormals_product(params)
    expected_mean = math.log(10) + math.log(100)
    expected_std = math.sqrt(0.5**2 + 0.3**2)
    assert combined_mean == pytest.approx(expected_mean)
    assert combined_std == pytest.approx(expected_std)


def test_lognormal_from_point_estimate_1_sig_fig():
    log_mean, log_std = lognormal_from_point_estimate(1000, sig_figs=1)
    assert log_mean == pytest.approx(math.log(1000))
    # ~half order of magnitude
    assert log_std == pytest.approx(math.log(10) / 2, rel=0.1)


def test_lognormal_from_point_estimate_2_sig_figs():
    log_mean, log_std = lognormal_from_point_estimate(1000, sig_figs=2)
    assert log_mean == pytest.approx(math.log(1000))
    # ~30% uncertainty
    assert log_std == pytest.approx(math.log(1.3), rel=0.1)
