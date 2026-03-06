"""Formatting package public API."""

from fermi_problems.formatting.notation import to_scientific, to_engineering, to_human, to_order_of_magnitude
from fermi_problems.formatting.display import format_chain_result, format_estimate

__all__ = [
    "to_scientific",
    "to_engineering",
    "to_human",
    "to_order_of_magnitude",
    "format_chain_result",
    "format_estimate",
]
