"""Number formatting functions for Fermi estimation."""

import math


def to_scientific(value: float, sig_figs: int = 3) -> str:
    """Format in scientific notation: '1.23e+06'."""
    if value == 0:
        return "0"
    magnitude = math.floor(math.log10(abs(value)))
    coeff = value / (10**magnitude)
    decimal_places = sig_figs - 1
    return f"{coeff:.{decimal_places}f}e{magnitude:+03d}"


def to_engineering(value: float, sig_figs: int = 3) -> str:
    """Format in engineering notation (exponent multiple of 3): '1.23M'.

    Uses suffixes: k (10^3), M (10^6), B (10^9), T (10^12).
    """
    if value == 0:
        return "0"

    suffixes = {
        12: "T",
        9: "B",
        6: "M",
        3: "k",
        0: "",
    }

    magnitude = math.floor(math.log10(abs(value)))
    # Round down to nearest multiple of 3
    eng_exp = (magnitude // 3) * 3
    # Cap at known suffixes
    if eng_exp > 12:
        eng_exp = 12
    elif eng_exp < 0:
        eng_exp = 0

    suffix = suffixes.get(eng_exp, "")
    coeff = value / (10**eng_exp)
    decimal_places = max(0, sig_figs - len(str(int(abs(coeff)))))
    return f"{coeff:.{decimal_places}f}{suffix}"


def to_human(value: float, sig_figs: int = 2) -> str:
    """Format for human reading.

    - Small/medium numbers as-is: '42', '1,500'
    - Large numbers with suffix: '10M', '2.5B'
    - Very large/small in scientific notation: '3.0e+23'
    """
    if value == 0:
        return "0"

    magnitude = math.floor(math.log10(abs(value)))

    if magnitude >= 12:
        return to_scientific(value, sig_figs)
    elif magnitude >= 9:
        coeff = value / 1e9
        decimal_places = max(0, sig_figs - len(str(int(abs(coeff)))))
        return f"{coeff:.{decimal_places}f}B"
    elif magnitude >= 6:
        coeff = value / 1e6
        decimal_places = max(0, sig_figs - len(str(int(abs(coeff)))))
        return f"{coeff:.{decimal_places}f}M"
    elif magnitude >= 3:
        coeff = value / 1e3
        decimal_places = max(0, sig_figs - len(str(int(abs(coeff)))))
        return f"{coeff:.{decimal_places}f}k"
    elif magnitude >= -3:
        # Plain number
        if magnitude >= 0:
            decimal_places = max(0, sig_figs - magnitude - 1)
            formatted = f"{value:.{decimal_places}f}"
            # Add thousands separator for large numbers
            parts = formatted.split(".")
            try:
                parts[0] = f"{int(parts[0]):,}"
            except ValueError:
                pass
            return ".".join(parts) if len(parts) > 1 else parts[0]
        else:
            decimal_places = sig_figs - magnitude - 1
            return f"{value:.{decimal_places}f}"
    else:
        return to_scientific(value, sig_figs)


def to_order_of_magnitude(value: float) -> str:
    """Format as '~10^N'. Example: 1.5e6 -> '~10^6'."""
    if value <= 0:
        raise ValueError("Value must be positive.")
    magnitude = round(math.log10(value))
    return f"~10^{magnitude}"
