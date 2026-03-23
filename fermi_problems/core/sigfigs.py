"""Significant figures utilities for Fermi estimation."""

import math


def infer_sig_figs(value: float) -> int:
    """Infer significant figures from a float value.

    Heuristic: examine the float's string representation.
    - 1e6 -> 1 sig fig
    - 1.5e6 -> 2 sig figs
    - 0.01 -> 1 sig fig
    - 250 -> 2 sig figs (trailing zero ambiguous, assume not significant)

    This is inherently imprecise for floats. When precision matters,
    users should specify sig_figs explicitly.
    """
    if value == 0:
        return 1

    # Use the repr to count significant digits
    s = f"{value:.15g}"

    # Remove sign
    s = s.lstrip("-")

    # Handle scientific notation: split at 'e'
    if "e" in s or "E" in s:
        mantissa = s.split("e")[0].split("E")[0]
    else:
        mantissa = s

    # Remove leading zeros and decimal point
    mantissa_clean = mantissa.replace(".", "")
    mantissa_clean = mantissa_clean.lstrip("0")

    # Remove trailing zeros (they are not significant in float repr)
    mantissa_clean = mantissa_clean.rstrip("0")

    if not mantissa_clean:
        return 1

    return len(mantissa_clean)


def round_to_sig_figs(value: float, sig_figs: int) -> float:
    """Round a number to the given number of significant figures."""
    if value == 0:
        return 0.0
    magnitude = math.floor(math.log10(abs(value)))
    factor = 10 ** (sig_figs - 1 - magnitude)
    return round(value * factor) / factor


def format_sig_figs(value: float, sig_figs: int) -> str:
    """Format a number showing exactly sig_figs significant figures.

    Uses scientific notation for very large/small numbers.
    Example: format_sig_figs(12345, 3) -> '1.23e+04'
    Example: format_sig_figs(0.00456, 2) -> '4.6e-03'
    Example: format_sig_figs(42.0, 2) -> '42'
    """
    if value == 0:
        return "0"

    magnitude = math.floor(math.log10(abs(value)))

    # Use plain notation for numbers in a reasonable range
    if -2 <= magnitude < 4:
        rounded = round_to_sig_figs(value, sig_figs)
        # Determine decimal places needed
        decimal_places = max(0, sig_figs - 1 - magnitude)
        if decimal_places == 0:
            return str(int(rounded))
        else:
            formatted = f"{rounded:.{decimal_places}f}"
            return formatted
    else:
        # Scientific notation
        exp = magnitude
        coeff = value / (10**exp)
        decimal_places = sig_figs - 1
        coeff_rounded = round(coeff, decimal_places)
        if decimal_places == 0:
            return f"{coeff_rounded:.0f}e{exp:+03d}"
        return f"{coeff_rounded:.{decimal_places}f}e{exp:+03d}"
