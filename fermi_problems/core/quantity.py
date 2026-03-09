"""Quantity — a numeric value paired with a Unit."""

from fermi_problems.units.dimension import Unit
from fermi_problems.units.parser import parse_unit
from fermi_problems.units.registry import UnitRegistry


class DimensionError(Exception):
    """Raised when units are incompatible for an operation."""


class Quantity:
    """A numeric value with a unit.

    Values are stored internally in SI-base scale.
    """

    __slots__ = ("_si_value", "_unit", "_display_scale", "_display_unit_str")

    def __init__(
        self,
        value: float,
        unit: "Unit | str",
        registry: UnitRegistry | None = None,
    ):
        """Create a quantity.

        If unit is a string, parse it via the registry.
        The value is stored in SI-base scale internally.
        """
        if isinstance(unit, str):
            parsed = parse_unit(unit, registry)
            self._unit: Unit = parsed.unit
            self._display_scale: float = parsed.scale
            self._display_unit_str: str = unit
        else:
            self._unit = unit
            self._display_scale = 1.0
            self._display_unit_str = str(unit)

        # Store value converted to SI base
        self._si_value: float = value * self._display_scale

    @property
    def value(self) -> float:
        """The value in SI-base units."""
        return self._si_value

    @property
    def unit(self) -> Unit:
        """The dimensional unit."""
        return self._unit

    def in_unit(self, target: "str | Unit") -> float:
        """Return the numeric value expressed in the given target unit.

        Raises DimensionError if dimensions don't match.
        """
        if isinstance(target, str):
            parsed = parse_unit(target)
            target_unit = parsed.unit
            target_scale = parsed.scale
        else:
            target_unit = target
            target_scale = 1.0

        if self._unit != target_unit:
            raise DimensionError(f"Cannot convert {self._unit} to {target_unit}: dimensions do not match")
        return self._si_value / target_scale

    def to(self, target: "str | Unit") -> "Quantity":
        """Return a new Quantity expressed in the target unit."""
        converted_value = self.in_unit(target)
        if isinstance(target, str):
            return Quantity(converted_value, target)
        else:
            return Quantity(converted_value / 1.0, target)

    def __mul__(self, other: "Quantity | float | int") -> "Quantity":
        if isinstance(other, (int, float)):
            result = Quantity.__new__(Quantity)
            result._si_value = self._si_value * other
            result._unit = self._unit
            result._display_scale = self._display_scale
            result._display_unit_str = self._display_unit_str
            return result
        new_unit = self._unit * other._unit
        result = Quantity.__new__(Quantity)
        result._si_value = self._si_value * other._si_value
        result._unit = new_unit
        result._display_scale = self._display_scale * other._display_scale
        result._display_unit_str = f"{self._display_unit_str}*{other._display_unit_str}"
        return result

    def __rmul__(self, other: "float | int") -> "Quantity":
        return self.__mul__(other)

    def __truediv__(self, other: "Quantity | float | int") -> "Quantity":
        if isinstance(other, (int, float)):
            result = Quantity.__new__(Quantity)
            result._si_value = self._si_value / other
            result._unit = self._unit
            result._display_scale = self._display_scale
            result._display_unit_str = self._display_unit_str
            return result
        new_unit = self._unit / other._unit
        result = Quantity.__new__(Quantity)
        result._si_value = self._si_value / other._si_value
        result._unit = new_unit
        result._display_scale = self._display_scale / other._display_scale if other._display_scale != 0 else 1.0
        result._display_unit_str = f"{self._display_unit_str}/{other._display_unit_str}"
        return result

    def __rtruediv__(self, other: "float | int") -> "Quantity":
        result = Quantity.__new__(Quantity)
        result._si_value = other / self._si_value
        result._unit = self._unit.inverse()
        result._display_scale = 1.0 / self._display_scale if self._display_scale != 0 else 1.0
        result._display_unit_str = f"1/{self._display_unit_str}"
        return result

    def __add__(self, other: "Quantity") -> "Quantity":
        """Add quantities. Must have same dimensions. Converts to common base."""
        if self._unit != other._unit:
            raise DimensionError(f"Cannot add {self._unit} and {other._unit}: dimensions do not match")
        result = Quantity.__new__(Quantity)
        result._si_value = self._si_value + other._si_value
        result._unit = self._unit
        result._display_scale = self._display_scale
        result._display_unit_str = self._display_unit_str
        return result

    def __sub__(self, other: "Quantity") -> "Quantity":
        """Subtract quantities. Must have same dimensions."""
        if self._unit != other._unit:
            raise DimensionError(f"Cannot subtract {self._unit} and {other._unit}: dimensions do not match")
        result = Quantity.__new__(Quantity)
        result._si_value = self._si_value - other._si_value
        result._unit = self._unit
        result._display_scale = self._display_scale
        result._display_unit_str = self._display_unit_str
        return result

    def __repr__(self) -> str:
        display_value = self._si_value / self._display_scale if self._display_scale != 0 else self._si_value
        return f"Quantity({display_value!r}, {self._display_unit_str!r})"

    def __str__(self) -> str:
        display_value = self._si_value / self._display_scale if self._display_scale != 0 else self._si_value
        return f"{display_value:.6g} {self._display_unit_str}"
