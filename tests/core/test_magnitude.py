"""Tests for fermi_problems.core.magnitude — ported from tests/test_rounding.py + new tests."""

import pytest
from fermi_problems.core.magnitude import (
    nearest_order_of_magnitude,
    order_of_magnitude,
    order_of_magnitude_range,
    log10_distance,
)


@pytest.mark.parametrize(
    "number, expected_order",
    [
        (4e6, 7),
        (1.7e8, 8),
        (3.7e8, 9),
    ],
)
def test_order_of_magnitude_large(number, expected_order):
    assert order_of_magnitude(number) == expected_order


@pytest.mark.parametrize(
    "number, expected_order",
    [
        (0.2, -1),
        (1, 0),
        (6, 1),
        (31, 1),
        (32, 2),
        (999, 3),
        (1000, 3),
    ],
)
def test_order_of_magnitude_small(number, expected_order):
    assert order_of_magnitude(number) == expected_order


def test_order_of_magnitude_midpoint():
    # Logarithmic midpoint between 1 and 10 is sqrt(10) ≈ 3.16; 5 > sqrt(10), rounds up
    assert order_of_magnitude(5) == 1


@pytest.mark.parametrize(
    "number, expected_magnitude",
    [
        (4e6, 7),
        (1.7e8, 8),
        (3.7e8, 9),
    ],
)
def test_nearest_order_of_magnitude(number, expected_magnitude):
    assert nearest_order_of_magnitude(number) == expected_magnitude


def test_order_of_magnitude_range():
    r = order_of_magnitude_range(5)
    assert r == (1, 10)


def test_log10_distance():
    # 10 to 100 is 1 OOM apart
    assert log10_distance(10, 100) == pytest.approx(1.0)
    assert log10_distance(100, 10) == pytest.approx(1.0)  # absolute


def test_log10_distance_same_oom():
    # Same number: distance 0
    assert log10_distance(1000, 1000) == pytest.approx(0.0)
    # Close numbers
    assert log10_distance(1000, 2000) < 1.0
