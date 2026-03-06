"""Lognormal distribution utilities for Fermi estimation.

No scipy dependency — uses a rational approximation for the normal inverse CDF.
"""

import math


def normal_ppf(p: float) -> float:
    """Inverse of the standard normal CDF (percent point function).

    Uses the rational approximation from Abramowitz and Stegun 26.2.23.
    Accurate to ~4.5e-4 relative error.
    """
    if p < 0.5:
        return -normal_ppf(1 - p)
    if p == 0.5:
        return 0.0
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3)


def lognormal_from_range(
    low: float,
    high: float,
    confidence: float = 0.90,
) -> tuple[float, float]:
    """Fit a lognormal distribution to a confidence interval.

    Interprets [low, high] as a symmetric confidence interval
    (e.g., 90% means low=P5, high=P95).

    Returns (log_mean, log_std) — the parameters of the underlying
    normal distribution in ln-space.
    """
    z = normal_ppf((1 + confidence) / 2)
    log_mean = (math.log(low) + math.log(high)) / 2
    log_std = (math.log(high) - math.log(low)) / (2 * z)
    return log_mean, log_std


def lognormal_point_estimate(log_mean: float) -> float:
    """exp(log_mean) — the geometric mean / median of the lognormal."""
    return math.exp(log_mean)


def lognormal_confidence_interval(
    log_mean: float,
    log_std: float,
    confidence: float = 0.90,
) -> tuple[float, float]:
    """Return (low, high) confidence interval for a lognormal distribution."""
    z = normal_ppf((1 + confidence) / 2)
    low = math.exp(log_mean - z * log_std)
    high = math.exp(log_mean + z * log_std)
    return low, high


def combine_lognormals_product(
    params: list[tuple[float, float]],
) -> tuple[float, float]:
    """Combine independent lognormal distributions via multiplication.

    The product of independent lognormals is lognormal with:
        combined_log_mean = sum of log_means
        combined_log_std = sqrt(sum of log_std^2)

    Args:
        params: list of (log_mean, log_std) tuples

    Returns:
        (combined_log_mean, combined_log_std)
    """
    combined_log_mean = sum(lm for lm, _ in params)
    combined_log_std = math.sqrt(sum(ls**2 for _, ls in params))
    return combined_log_mean, combined_log_std


def lognormal_from_point_estimate(
    value: float,
    sig_figs: int = 1,
) -> tuple[float, float]:
    """Infer lognormal parameters from a point estimate.

    With 1 sig fig: assume ±half an order of magnitude (log_std ≈ 0.7)
    With 2 sig figs: assume ±30% (log_std ≈ 0.16)
    With 3+ sig figs: assume ±10% (log_std ≈ 0.06)
    """
    log_mean = math.log(value)
    if sig_figs <= 1:
        log_std = math.log(10) / 2  # ≈ 1.151, half OOM in ln space
    elif sig_figs == 2:
        log_std = math.log(1.3)  # ≈ 0.262, ~30% uncertainty
    else:
        log_std = math.log(1.1)  # ≈ 0.095, ~10% uncertainty
    return log_mean, log_std
