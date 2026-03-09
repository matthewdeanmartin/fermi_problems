"""Estimate — a quantity with associated uncertainty."""

import math

from fermi_problems.units.dimension import Unit
from fermi_problems.units.parser import parse_unit
from fermi_problems.units.registry import UnitRegistry
from fermi_problems.core.sigfigs import infer_sig_figs
from fermi_problems.uncertainty.lognormal import (
    lognormal_from_range,
    lognormal_from_point_estimate,
    lognormal_confidence_interval,
)


class Estimate:
    """A quantity with associated uncertainty.

    Can be created from:
    - A point estimate: Estimate(1e6, "people")
    - A point + range: Estimate(1e6, "people", low=8e5, high=1.2e6)
    - A point + sig figs: Estimate(1e6, "people", sig_figs=1)
    """

    def __init__(
        self,
        value: float,
        unit: "Unit | str",
        *,
        low: float | None = None,
        high: float | None = None,
        sig_figs: int | None = None,
        confidence: float = 0.90,
        registry: UnitRegistry | None = None,
    ):
        """Create an estimate.

        If low/high given: fit lognormal to the range.
        If sig_figs given: infer uncertainty from precision.
        If neither: infer sig_figs from value representation.
        """
        # Resolve unit
        if isinstance(unit, str):
            parsed = parse_unit(unit, registry)
            self._unit: Unit = parsed.unit
            self._display_unit_str: str = unit
            self._display_scale: float = parsed.scale
        else:
            self._unit = unit
            self._display_unit_str = str(unit)
            self._display_scale = 1.0

        # Store SI value
        self._si_value: float = value * self._display_scale
        self._raw_value: float = value  # user-facing value in display unit
        self._low: float | None = low
        self._high: float | None = high

        # Determine lognormal parameters
        if low is not None and high is not None:
            # Convert to SI for internal consistency
            si_low = low * self._display_scale
            si_high = high * self._display_scale
            self._log_mean, self._log_std = lognormal_from_range(si_low, si_high, confidence)
            # Use geometric mean as the "value" in SI
            self._si_value = math.exp(self._log_mean)
            self._raw_value = self._si_value / self._display_scale
            # Infer sig figs from value
            self._sig_figs: int = sig_figs if sig_figs is not None else infer_sig_figs(value)
        elif sig_figs is not None:
            self._sig_figs = sig_figs
            self._log_mean, self._log_std = lognormal_from_point_estimate(self._si_value, sig_figs)
        else:
            # Infer sig figs from the float repr
            self._sig_figs = infer_sig_figs(value)
            self._log_mean, self._log_std = lognormal_from_point_estimate(self._si_value, self._sig_figs)

    @property
    def value(self) -> float:
        """Point estimate (geometric mean if range was given), in SI base units."""
        return self._si_value

    @property
    def unit(self) -> Unit:
        return self._unit

    @property
    def log_mean(self) -> float:
        return self._log_mean

    @property
    def log_std(self) -> float:
        return self._log_std

    @property
    def sig_figs(self) -> int:
        return self._sig_figs

    @property
    def low(self) -> float | None:
        """Lower bound of the input range, if given."""
        return self._low

    @property
    def high(self) -> float | None:
        """Upper bound of the input range, if given."""
        return self._high

    def confidence_interval(self, level: float = 0.90) -> tuple[float, float]:
        """Best-case confidence interval from lognormal model."""
        return lognormal_confidence_interval(self._log_mean, self._log_std, level)

    def _make_estimate_from_params(
        self,
        si_value: float,
        unit: Unit,
        log_mean: float,
        log_std: float,
        sig_figs: int,
        display_unit_str: str = "",
        display_scale: float = 1.0,
    ) -> "Estimate":
        """Internal factory: build an Estimate from pre-computed lognormal params."""
        e = Estimate.__new__(Estimate)
        e._si_value = si_value
        e._raw_value = si_value / display_scale if display_scale != 0 else si_value
        e._unit = unit
        e._display_unit_str = display_unit_str or str(unit)
        e._display_scale = display_scale
        e._log_mean = log_mean
        e._log_std = log_std
        e._sig_figs = sig_figs
        e._low = None
        e._high = None
        return e

    def __mul__(self, other: "Estimate | float | int") -> "Estimate":
        """Multiply estimates: multiply values, combine units, propagate uncertainty."""
        if isinstance(other, (int, float)):
            # Treat scalar as exact
            other_log_mean = math.log(abs(other)) if other != 0 else 0.0
            new_log_mean = self._log_mean + other_log_mean
            new_log_std = self._log_std
            new_si_value = math.exp(new_log_mean)
            new_unit = self._unit
            new_sig_figs = self._sig_figs
            new_display_scale = self._display_scale
            new_display_str = self._display_unit_str
        else:
            new_log_mean = self._log_mean + other._log_mean
            new_log_std = math.sqrt(self._log_std**2 + other._log_std**2)
            new_si_value = math.exp(new_log_mean)
            new_unit = self._unit * other._unit
            new_sig_figs = min(self._sig_figs, other._sig_figs)
            new_display_scale = self._display_scale * other._display_scale
            new_display_str = f"{self._display_unit_str}*{other._display_unit_str}"

        return self._make_estimate_from_params(
            new_si_value, new_unit, new_log_mean, new_log_std, new_sig_figs, new_display_str, new_display_scale
        )

    def __rmul__(self, other: "float | int") -> "Estimate":
        return self.__mul__(other)

    def __truediv__(self, other: "Estimate | float | int") -> "Estimate":
        """Divide estimates: divide values, divide units, propagate uncertainty."""
        if isinstance(other, (int, float)):
            other_log_mean = math.log(abs(other)) if other != 0 else 0.0
            new_log_mean = self._log_mean - other_log_mean
            new_log_std = self._log_std
            new_si_value = math.exp(new_log_mean)
            new_unit = self._unit
            new_sig_figs = self._sig_figs
            new_display_scale = self._display_scale
            new_display_str = self._display_unit_str
        else:
            new_log_mean = self._log_mean - other._log_mean
            new_log_std = math.sqrt(self._log_std**2 + other._log_std**2)
            new_si_value = math.exp(new_log_mean)
            new_unit = self._unit / other._unit
            new_sig_figs = min(self._sig_figs, other._sig_figs)
            new_display_scale = (
                self._display_scale / other._display_scale if other._display_scale != 0 else self._display_scale
            )
            new_display_str = f"{self._display_unit_str}/{other._display_unit_str}"

        return self._make_estimate_from_params(
            new_si_value, new_unit, new_log_mean, new_log_std, new_sig_figs, new_display_str, new_display_scale
        )

    def __rtruediv__(self, other: "float | int") -> "Estimate":
        other_log_mean = math.log(abs(other)) if other != 0 else 0.0
        new_log_mean = other_log_mean - self._log_mean
        new_log_std = self._log_std
        new_si_value = math.exp(new_log_mean)
        new_unit = self._unit.inverse()
        return self._make_estimate_from_params(
            new_si_value,
            new_unit,
            new_log_mean,
            new_log_std,
            self._sig_figs,
            f"1/{self._display_unit_str}",
            1.0 / self._display_scale if self._display_scale != 0 else 1.0,
        )

    def in_unit(self, target: "str | Unit") -> float:
        """Return the numeric value expressed in the given target unit."""
        from fermi_problems.core.quantity import DimensionError

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

    def __repr__(self) -> str:
        return f"Estimate({self._raw_value!r}, {self._display_unit_str!r})"

    def __str__(self) -> str:
        """e.g. '~1.0e+06 people [8.0e+05, 1.2e+06]'"""
        display_val = self._si_value / self._display_scale if self._display_scale != 0 else self._si_value
        low_si, high_si = self.confidence_interval()
        low_disp = low_si / self._display_scale if self._display_scale != 0 else low_si
        high_disp = high_si / self._display_scale if self._display_scale != 0 else high_si
        return f"~{display_val:.3g} {self._display_unit_str} [{low_disp:.3g}, {high_disp:.3g}]"
