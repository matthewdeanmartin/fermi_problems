"""Interval arithmetic for worst-case bound computation."""


def interval_product(
    intervals: list[tuple[float, float]],
) -> tuple[float, float]:
    """Compute the worst-case product interval.

    Given a list of (low, high) ranges, compute the range of the product
    considering all combinations of extremes.

    Handles negative values correctly.
    """
    if not intervals:
        return (1.0, 1.0)

    product_interval = intervals[0]

    for lower, upper in intervals[1:]:
        candidates = (
            product_interval[0] * lower,
            product_interval[0] * upper,
            product_interval[1] * lower,
            product_interval[1] * upper,
        )
        product_interval = (min(candidates), max(candidates))

    return product_interval


def interval_quotient(
    numerator: tuple[float, float],
    denominator: tuple[float, float],
) -> tuple[float, float]:
    """Compute the interval of a/b.

    Raises ZeroDivisionError if denominator interval contains zero.
    """
    d_low, d_high = denominator
    if d_low <= 0 <= d_high:
        raise ZeroDivisionError(
            f"Denominator interval {denominator} contains zero"
        )
    # Dividing by [d_low, d_high] is same as multiplying by [1/d_high, 1/d_low]
    return interval_product([numerator, (1.0 / d_high, 1.0 / d_low)])
