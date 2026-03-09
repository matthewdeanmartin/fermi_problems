"""EstimateChain — a named collection of Estimates representing a Fermi decomposition."""

from dataclasses import dataclass

from fermi_problems.units.dimension import Unit
from fermi_problems.units.parser import parse_unit
from fermi_problems.uncertainty.interval import interval_product
from fermi_problems.core.estimate import Estimate


@dataclass
class ChainResult:
    """Result of computing an EstimateChain."""

    estimate: Estimate
    worst_case: tuple[float, float]
    best_case: tuple[float, float]
    unit_check: bool
    unit_mismatch_detail: str | None
    sig_figs: int


class EstimateChain:
    """A Fermi decomposition: a sequence of estimates that multiply to an answer."""

    def __init__(self, target_unit: "Unit | str | None" = None):
        """Create an empty chain, optionally with a target unit."""
        if isinstance(target_unit, str):
            parsed = parse_unit(target_unit)
            self._target_unit: Unit | None = parsed.unit
            self._target_unit_str: str = target_unit
        elif isinstance(target_unit, Unit):
            self._target_unit = target_unit
            self._target_unit_str = str(target_unit)
        else:
            self._target_unit = None
            self._target_unit_str = ""

        self._factors: list[tuple[str, Estimate, bool]] = []

    def add(self, name: str, estimate: Estimate, *, divide: bool = False) -> None:
        """Add a named factor to the chain.

        If divide=True, this factor divides rather than multiplies.
        """
        self._factors.append((name, estimate, divide))

    def add_factor(
        self,
        name: str,
        value: float,
        unit: str,
        *,
        low: float | None = None,
        high: float | None = None,
        sig_figs: int | None = None,
        divide: bool = False,
    ) -> None:
        """Convenience: create an Estimate and add it in one call."""
        estimate = Estimate(value, unit, low=low, high=high, sig_figs=sig_figs)
        self.add(name, estimate, divide=divide)

    @property
    def factors(self) -> list[tuple[str, Estimate, bool]]:
        """List of (name, estimate, is_divisor) triples."""
        return list(self._factors)

    def compute(self, confidence: float = 0.90) -> ChainResult:
        """Multiply all factors, propagate uncertainty, check units."""
        if not self._factors:
            # Empty chain: return a dimensionless 1
            from fermi_problems.units.dimension import Unit as _Unit

            dummy = Estimate(1.0, _Unit())
            return ChainResult(
                estimate=dummy,
                worst_case=(1.0, 1.0),
                best_case=(1.0, 1.0),
                unit_check=(self._target_unit is None or self._target_unit.is_dimensionless),
                unit_mismatch_detail=None,
                sig_figs=1,
            )

        # Combine all estimates
        combined: Estimate | None = None
        interval_list: list[tuple[float, float]] = []

        for _name, est, is_divisor in self._factors:
            # Build worst-case interval range in SI units
            ci_low_si, ci_high_si = est.confidence_interval(0.90)
            # Use specified low/high if available, else use CI
            if est.low is not None and est.high is not None:
                interval_low = est.low * est._display_scale
                interval_high = est.high * est._display_scale
            else:
                interval_low = ci_low_si
                interval_high = ci_high_si

            if is_divisor:
                # Dividing: invert the interval
                if interval_low > 0:
                    interval_list.append((1.0 / interval_high, 1.0 / interval_low))
            else:
                interval_list.append((interval_low, interval_high))

            if combined is None:
                combined = est if not is_divisor else (1.0 / est)  # type: ignore[operator]
            else:
                if is_divisor:
                    combined = combined / est
                else:
                    combined = combined * est

        assert combined is not None

        # Worst case: interval arithmetic
        worst_case = interval_product(interval_list)

        # Best case: lognormal CI
        best_case = combined.confidence_interval(confidence)

        # Unit check
        unit_ok, result_unit, mismatch_detail = self.validate_units()

        return ChainResult(
            estimate=combined,
            worst_case=worst_case,
            best_case=best_case,
            unit_check=unit_ok,
            unit_mismatch_detail=mismatch_detail,
            sig_figs=combined.sig_figs,
        )

    def validate_units(self) -> tuple[bool, Unit, str | None]:
        """Check if factor units cancel to the target.

        Returns (ok, resulting_unit, error_message_or_none).
        """
        if not self._factors:
            result_unit = Unit()
        else:
            result_unit = Unit()
            for _name, est, is_divisor in self._factors:
                if is_divisor:
                    result_unit = result_unit / est.unit
                else:
                    result_unit = result_unit * est.unit

        if self._target_unit is None:
            return True, result_unit, None

        if result_unit == self._target_unit:
            return True, result_unit, None

        msg = f"Expected unit '{self._target_unit_str}' ({self._target_unit}), " f"got {result_unit}"
        return False, result_unit, msg

    def __repr__(self) -> str:
        factor_names = [name for name, _, _ in self._factors]
        return f"EstimateChain(target={self._target_unit_str!r}, factors={factor_names!r})"
