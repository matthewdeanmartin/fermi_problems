"""Unit expression parser — parses 'meters/second^2' into a Unit + scale factor."""

from dataclasses import dataclass

from fermi_problems.units.dimension import Unit
from fermi_problems.units.registry import UnitDef, UnitRegistry, UnknownUnitError, default_registry


@dataclass
class ParsedUnit:
    """Result of parsing a unit expression string."""

    unit: Unit
    scale: float  # aggregate scale factor relative to SI bases


def parse_unit(expr: str, registry: UnitRegistry | None = None) -> ParsedUnit:
    """Parse a unit expression string.

    Grammar:
        unit_expr  = term ("/" term)*
        term       = atom ("*" atom)*
        atom       = NAME ("^" INTEGER)?

    Examples:
        "meters/second"      -> Unit(length=1, time=-1), scale=1.0
        "feet/year"          -> Unit(length=1, time=-1), scale=0.3048/31557600
        "meters/second^2"    -> Unit(length=1, time=-2), scale=1.0
        "km*kg"              -> Unit(length=1, mass=1), scale=1000.0
    """
    if registry is None:
        registry = default_registry()

    expr = expr.strip()

    if not expr or expr in ("1", "dimensionless"):
        return ParsedUnit(unit=Unit(), scale=1.0)

    # Split on '/' — first part is numerator, rest are denominators
    slash_parts = [p.strip() for p in expr.split("/")]
    numerator_str = slash_parts[0]
    denominator_strs = slash_parts[1:]

    combined_dims: dict[str, int] = {}
    combined_scale = 1.0

    def apply_term(term_str: str, sign: int) -> None:
        """Parse one term (atoms joined by *) and apply to combined_dims/scale."""
        nonlocal combined_scale
        for atom_str in term_str.split("*"):
            atom_str = atom_str.strip()
            if not atom_str:
                continue
            # Parse atom: NAME or NAME^INTEGER
            if "^" in atom_str:
                name_part, exp_str = atom_str.split("^", 1)
                name_part = name_part.strip()
                exp = int(exp_str.strip())
            else:
                name_part = atom_str
                exp = 1

            unit_def = registry.lookup(name_part)
            # Apply exponent * sign to dimensions
            for dim_name, dim_exp in unit_def.dimensions.items():
                combined_dims[dim_name] = combined_dims.get(dim_name, 0) + dim_exp * exp * sign
            # Scale: scale^exp, applied with sign direction
            if sign > 0:
                combined_scale *= unit_def.scale ** exp
            else:
                combined_scale /= unit_def.scale ** exp

    apply_term(numerator_str, 1)
    for den_str in denominator_strs:
        apply_term(den_str, -1)

    return ParsedUnit(unit=Unit(combined_dims), scale=combined_scale)
