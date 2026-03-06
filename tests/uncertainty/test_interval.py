"""Tests for fermi_problems.uncertainty.interval"""

import pytest
from fermi_problems.uncertainty.interval import interval_product, interval_quotient


def test_interval_product_basic():
    ranges = [(2, 5), (10, 20), (1, 2)]
    low, high = interval_product(ranges)
    assert low == 20
    assert high == 200


def test_interval_product_single():
    result = interval_product([(3, 7)])
    assert result == (3, 7)


def test_interval_product_many():
    result = interval_product([(1, 2), (1, 2), (1, 2)])
    assert result == (1, 8)


def test_interval_quotient():
    low, high = interval_quotient((10, 20), (2, 5))
    assert low == pytest.approx(2.0)
    assert high == pytest.approx(10.0)


def test_interval_quotient_zero_denominator_raises():
    with pytest.raises(ZeroDivisionError):
        interval_quotient((1, 10), (-1, 1))


def test_interval_product_with_negatives():
    # (-2, -1) * (-2, -1) -> (1, 4)
    result = interval_product([(-2, -1), (-2, -1)])
    assert result[0] == pytest.approx(1.0)
    assert result[1] == pytest.approx(4.0)
