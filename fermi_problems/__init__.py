"""fermi_problems — a library for Fermi estimation with units and uncertainty."""

from fermi_problems.core import ChainResult, DimensionError, Estimate, EstimateChain, Quantity
from fermi_problems.core.magnitude import log10_distance, nearest_order_of_magnitude, order_of_magnitude
from fermi_problems.formatting.display import format_chain_result, format_estimate
from fermi_problems.formatting.notation import to_engineering, to_human, to_scientific
from fermi_problems.units import Unit, UnitRegistry, default_registry, parse_unit

__all__ = [
    "Unit",
    "UnitRegistry",
    "parse_unit",
    "default_registry",
    "Quantity",
    "Estimate",
    "EstimateChain",
    "ChainResult",
    "DimensionError",
    "nearest_order_of_magnitude",
    "order_of_magnitude",
    "log10_distance",
    "to_scientific",
    "to_engineering",
    "to_human",
    "format_chain_result",
    "format_estimate",
]
