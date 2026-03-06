"""Heuristic error bound formula for Fermi estimation."""

import math


def fermi_error_bounds(
    num_steps: int,
    accuracy_factor: float = 2.0,
) -> tuple[float, float]:
    """Heuristic error bounds for a Fermi estimate with N multiplicative steps.

    Rule of thumb: each factor is off by up to `accuracy_factor` in either
    direction. The combined error grows as accuracy_factor^sqrt(num_steps)
    (errors compound in quadrature in log-space).

    Returns (lower_multiplier, upper_multiplier) such that the true answer
    is expected to be between estimate/upper and estimate*upper.

    Example: 9 steps, accuracy=2 -> bounds [0.125, 8]
    """
    error_factor = accuracy_factor ** math.sqrt(num_steps)
    lower_bound = 1.0 / error_factor
    upper_bound = error_factor
    return lower_bound, upper_bound
