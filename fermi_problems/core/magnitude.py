"""Order-of-magnitude functions for Fermi estimation."""

import math


def nearest_order_of_magnitude(number: float) -> int:
    """Round log10(number) to nearest integer."""
    if number <= 0:
        raise ValueError("Number must be positive.")
    return round(math.log10(number))


def order_of_magnitude(number: float) -> int:
    """Order of magnitude using geometric midpoint rounding."""
    if number <= 0:
        raise ValueError("Number must be positive.")
    b = math.floor(math.log10(number))
    a = number / (10**b)

    # Adjust b if a is outside the range [1/sqrt(10), sqrt(10)]
    if a < 1 / math.sqrt(10):
        a *= 10
        b -= 1
    elif a >= math.sqrt(10):
        a /= 10
        b += 1

    return b


def order_of_magnitude_range(number: float) -> tuple[float, float]:
    """Range of numbers that share the same order of magnitude."""
    nearest_order = nearest_order_of_magnitude(number)

    lower_bound = 10**nearest_order
    upper_bound = 10 ** (nearest_order + 1)

    # If the number is closer to the lower bound, adjust the range
    if number < math.sqrt(lower_bound * upper_bound):
        upper_bound = lower_bound
        lower_bound = 10 ** (nearest_order - 1)

    return lower_bound, upper_bound


def log10_distance(a: float, b: float) -> float:
    """Absolute distance in log10 space. |log10(a) - log10(b)|.

    This is the fundamental 'how close' metric for Fermi estimation.
    """
    return abs(math.log10(a) - math.log10(b))
