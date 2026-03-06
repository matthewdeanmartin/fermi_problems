"""fermi_problems — a library for Fermi estimation with units and uncertainty."""

from fermi_problems.units import Unit, UnitRegistry, parse_unit, default_registry
from fermi_problems.core import Quantity, Estimate, EstimateChain, ChainResult, DimensionError
from fermi_problems.core.magnitude import (
    nearest_order_of_magnitude,
    order_of_magnitude,
    log10_distance,
)
from fermi_problems.formatting.notation import to_scientific, to_engineering, to_human
from fermi_problems.formatting.display import format_chain_result, format_estimate

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
