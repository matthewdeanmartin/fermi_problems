"""Tests for fermi_problems.core.chain.EstimateChain"""

import pytest
from fermi_problems.core.chain import EstimateChain


def test_piano_tuners_example():
    """The classic Fermi problem, end to end."""
    chain = EstimateChain(target_unit="tuners")
    chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
    chain.add_factor("pianos_per_person", 0.02, "pianos/person", low=0.01, high=0.05)
    chain.add_factor("tunings_per_year", 1.5, "tunings/piano/year", low=1, high=2)
    chain.add_factor("tuner_capacity", 4, "tunings/tuner/day", low=3, high=5, divide=True)
    chain.add_factor("work_days", 250, "days/year", low=240, high=260, divide=True)

    result = chain.compute()

    assert 50 < result.estimate.value < 500
    assert result.unit_check is True
    low, high = result.best_case
    assert low < result.estimate.value < high
    wlow, whigh = result.worst_case
    assert wlow <= low
    assert whigh >= high


def test_empty_chain():
    chain = EstimateChain()
    result = chain.compute()
    assert result.estimate.value == pytest.approx(1.0)


def test_single_factor():
    chain = EstimateChain()
    chain.add_factor("population", 1e6, "people")
    result = chain.compute()
    assert result.estimate.value == pytest.approx(1e6, rel=0.01)


def test_unit_validation_pass():
    chain = EstimateChain(target_unit="people")
    chain.add_factor("x", 1e6, "people")
    ok, unit, msg = chain.validate_units()
    assert ok is True
    assert msg is None


def test_unit_validation_fail():
    chain = EstimateChain(target_unit="tuners")
    chain.add_factor("x", 1e6, "people")
    ok, unit, msg = chain.validate_units()
    assert ok is False
    assert msg is not None


def test_worst_case_bounds():
    chain = EstimateChain()
    chain.add_factor("a", 10, "people", low=5, high=20)
    chain.add_factor("b", 3, "pianos/person", low=2, high=5)
    result = chain.compute()
    # Worst case should span wider than best case
    assert result.worst_case[0] <= result.best_case[0]
    assert result.worst_case[1] >= result.best_case[1]


def test_best_case_bounds():
    chain = EstimateChain()
    chain.add_factor("x", 100, "people", low=80, high=120)
    result = chain.compute()
    low, high = result.best_case
    assert low < result.estimate.value < high


def test_divide_factor():
    chain = EstimateChain()
    chain.add_factor("total", 1000, "people")
    chain.add_factor("per_group", 10, "people/tuner", divide=True)
    result = chain.compute()
    assert result.estimate.value == pytest.approx(100, rel=0.05)


def test_add_factor_convenience():
    chain = EstimateChain()
    chain.add_factor("pop", 1e6, "people", low=0.9e6, high=1.1e6)
    assert len(chain.factors) == 1
    name, est, is_div = chain.factors[0]
    assert name == "pop"
    assert est.low == 0.9e6
    assert is_div is False
