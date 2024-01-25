import pytest

import fermi_problems.rounding as rounding


# Test cases for larger numbers
@pytest.mark.parametrize(
    "number, expected_order",
    [
        (4e6, 7),
        (1.7e8, 8),
        (3.7e8, 9),
    ],
)
def test_rounding_large(number, expected_order):
    order = rounding.order_of_magnitude(number)
    assert order == expected_order, f"The order of magnitude for {number} should be {expected_order}, got {order}"


# Test cases for smaller numbers
@pytest.mark.parametrize(
    "number, expected_order",
    [
        (0.2, -1),
        (1, 0),
        # (5, 1),
        (6, 1),
        (31, 1),
        (32, 2),
        (999, 3),
        (1000, 3),
    ],
)
def test_rounding_small(number, expected_order):
    order = rounding.order_of_magnitude(number)
    assert order == expected_order, f"The order of magnitude for {number} should be {expected_order}, got {order}"


@pytest.mark.parametrize(
    "number, expected_order",
    [
        (5, 1),
    ],
)
def test_rounding_midpoint(number, expected_order):
    # The midpoint is logarithmic, so 3.16 or so, round down
    order = rounding.order_of_magnitude(number)
    assert order == expected_order, f"The order of magnitude for {number} should be {expected_order}, got {order}"


# nearest_order_of_magnitude
@pytest.mark.parametrize(
    "number, expected_magnitude",
    [
        (4e6, 7),
        (1.7e8, 8),
        (3.7e8, 9),
    ],
)
def test_nearest_order_of_magnitude(number, expected_magnitude):
    nearest_order = rounding.nearest_order_of_magnitude(number)
    assert (
        nearest_order == expected_magnitude
    ), f"The nearest order of magnitude for {number} should be {expected_magnitude}, got {nearest_order}"


def test_order_of_magnitude_range():
    range = rounding.order_of_magnitude_range(5)
    assert range == (1, 10)
