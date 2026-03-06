"""Integration tests: end-to-end Fermi estimation."""

import pytest
from fermi_problems import Estimate, EstimateChain, Quantity, Unit


def test_piano_tuners_chicago():
    """End-to-end: How many piano tuners in Chicago?"""
    chain = EstimateChain(target_unit="tuners")

    chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
    chain.add_factor("pianos_per_person", 0.02, "pianos/person", low=0.01, high=0.05)
    chain.add_factor("tunings_per_year", 1.5, "tunings/piano/year", low=1, high=2)
    chain.add_factor("tuner_capacity", 4, "tunings/tuner/day", low=3, high=5, divide=True)
    chain.add_factor("work_days", 250, "days/year", low=240, high=260, divide=True)

    result = chain.compute()

    # Point estimate should be in the right ballpark (50-500 tuners)
    assert 50 < result.estimate.value < 500

    # Units should cancel to "tuners"
    assert result.unit_check is True

    # Best case CI should contain the point estimate
    low, high = result.best_case
    assert low < result.estimate.value < high

    # Worst case CI should be wider than best case
    wlow, whigh = result.worst_case
    assert wlow <= low
    assert whigh >= high


def test_simple_multiplication():
    """Basic estimate multiplication with units."""
    speed = Estimate(60, "mph")
    time = Estimate(2.5, "hours")
    distance = speed * time

    assert distance.unit == Unit({"length": 1})
    assert abs(distance.in_unit("miles") - 150) < 1


def test_unit_conversion():
    """Converting between compatible units."""
    d = Quantity(1, "miles")
    assert abs(d.in_unit("feet") - 5280) < 1
    assert abs(d.in_unit("km") - 1.609) < 0.01
