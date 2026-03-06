"""Unit class — immutable compound unit as a mapping of dimension names to exponents."""


class Unit:
    """Immutable compound unit.

    A unit is a sorted tuple of (dimension_name, exponent) pairs.
    Dimensionless is the empty tuple.
    """

    __slots__ = ("_dims",)

    def __init__(self, dimensions: dict[str, int] | None = None):
        """Create a unit from a dict of {dimension: exponent}.

        Zero-exponent entries are stripped.
        None or empty dict = dimensionless.
        """
        if dimensions:
            self._dims: tuple[tuple[str, int], ...] = tuple(
                sorted((k, v) for k, v in dimensions.items() if v != 0)
            )
        else:
            self._dims = ()

    @property
    def is_dimensionless(self) -> bool:
        return len(self._dims) == 0

    def __mul__(self, other: "Unit") -> "Unit":
        """Combine dimensions: add exponents."""
        combined: dict[str, int] = dict(self._dims)
        for name, exp in other._dims:
            combined[name] = combined.get(name, 0) + exp
        return Unit(combined)

    def __truediv__(self, other: "Unit") -> "Unit":
        """Combine dimensions: subtract other's exponents."""
        combined: dict[str, int] = dict(self._dims)
        for name, exp in other._dims:
            combined[name] = combined.get(name, 0) - exp
        return Unit(combined)

    def __pow__(self, n: int) -> "Unit":
        """Multiply all exponents by n."""
        return Unit({name: exp * n for name, exp in self._dims})

    def inverse(self) -> "Unit":
        """Negate all exponents. Unit({'length': 1}) -> Unit({'length': -1})."""
        return Unit({name: -exp for name, exp in self._dims})

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Unit):
            return NotImplemented
        return self._dims == other._dims

    def __hash__(self) -> int:
        return hash(self._dims)

    def __repr__(self) -> str:
        if self.is_dimensionless:
            return "Unit()"
        return f"Unit({dict(self._dims)!r})"

    def __str__(self) -> str:
        """Human-readable: 'length/time^2'."""
        if self.is_dimensionless:
            return "dimensionless"

        numerator = [(name, exp) for name, exp in self._dims if exp > 0]
        denominator = [(name, -exp) for name, exp in self._dims if exp < 0]

        def fmt_parts(parts: list[tuple[str, int]]) -> str:
            tokens = []
            for name, exp in parts:
                if exp == 1:
                    tokens.append(name)
                else:
                    tokens.append(f"{name}^{exp}")
            return "*".join(tokens)

        num_str = fmt_parts(numerator) if numerator else ""
        den_str = fmt_parts(denominator) if denominator else ""

        if num_str and den_str:
            return f"{num_str}/{den_str}"
        elif num_str:
            return num_str
        else:
            # All negative exponents — show as 1/denom
            return f"1/{den_str}"
