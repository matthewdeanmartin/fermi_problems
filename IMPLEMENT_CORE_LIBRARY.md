# Implement Core Library — Task Breakdown

This document is the work order for rebuilding the fermi_problems core library from
scratch, as described in DESIGN.md. Every task includes what to build, the exact file
path, the public interface, edge cases to handle, and the tests that prove it works.

Tasks are ordered by dependency. Do them in sequence.

---

## Prerequisites

Before writing any code:

### P1. Create the package skeleton

Create empty `__init__.py` files so imports work:

```
fermi_problems/units/__init__.py
fermi_problems/core/__init__.py
fermi_problems/uncertainty/__init__.py
fermi_problems/formatting/__init__.py
```

Create corresponding test directories:

```
tests/units/__init__.py
tests/core/__init__.py
tests/uncertainty/__init__.py
```

### P2. Clean up old modules

Do NOT delete old files yet. The old modules stay in place until their replacements are
tested and working. At the end (task F1), old modules are removed and `compat/legacy.py`
wrappers are added if needed.

---

## Part 1: The Unit System

Everything else depends on this. Get it right.

### Task 1.1 — Unit class

**File:** `fermi_problems/units/dimension.py`

**What it is:** An immutable value object representing a compound unit as a mapping from
dimension names to integer exponents.

**Public interface:**

```python
class Unit:
    """Immutable compound unit.

    A unit is a sorted tuple of (dimension_name, exponent) pairs.
    Dimensionless is the empty tuple.
    """

    def __init__(self, dimensions: dict[str, int] | None = None):
        """Create a unit from a dict of {dimension: exponent}.
        Zero-exponent entries are stripped.
        None or empty dict = dimensionless."""

    @property
    def is_dimensionless(self) -> bool: ...

    def __mul__(self, other: "Unit") -> "Unit":
        """Combine dimensions: add exponents."""

    def __truediv__(self, other: "Unit") -> "Unit":
        """Combine dimensions: subtract other's exponents."""

    def __pow__(self, n: int) -> "Unit":
        """Multiply all exponents by n."""

    def inverse(self) -> "Unit":
        """Negate all exponents. Unit("length":1) -> Unit("length":-1)."""

    def __eq__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str:
        """Human-readable: 'length/time^2'."""
```

**Implementation notes:**

- Store dimensions internally as `tuple[tuple[str, int], ...]`, sorted by dimension name.
  This makes equality comparison and hashing trivial.
- Strip zero-exponent entries in the constructor. `Unit({"length": 1, "time": 0})`
  equals `Unit({"length": 1})`.
- `__str__` should produce readable output: numerator dimensions first (positive exponents),
  then `/` then denominator dimensions. Exponents > 1 shown as `^2`, `^3` etc.
  Example: `"people*pianos/time^2"`. Dimensionless prints as `"dimensionless"`.

**Edge cases:**

- Multiplying two units where all exponents cancel → dimensionless
- `Unit() * Unit()` → dimensionless
- `Unit({"length": 2}) ** 0` → dimensionless
- `Unit({"length": 1}) ** -1` → `Unit({"length": -1})`

**Tests:** `tests/units/test_dimension.py`

```
- test_dimensionless_creation
- test_single_dimension
- test_multiply_combines_exponents
- test_divide_subtracts_exponents
- test_multiply_to_dimensionless
- test_power
- test_inverse
- test_zero_exponents_stripped
- test_equality_and_hash
- test_str_formatting
- test_str_dimensionless
```

---

### Task 1.2 — UnitDef and Registry

**File:** `fermi_problems/units/registry.py`

**What it is:** A registry mapping surface-level unit names (strings like `"meters"`,
`"feet"`, `"year"`, `"people"`) to their canonical dimension and scale factor relative
to the base unit for that dimension.

**Public interface:**

```python
@dataclass(frozen=True)
class UnitDef:
    """Definition of a named unit."""
    dimensions: dict[str, int]   # e.g. {"length": 1}
    scale: float                 # relative to base unit (meters=1.0, feet=0.3048)
    canonical_name: str          # e.g. "meters" (for display)

class UnitRegistry:
    """Mutable registry of known unit names."""

    def __init__(self):
        """Initialize with built-in units."""

    def lookup(self, name: str) -> UnitDef:
        """Look up a unit name. Raises UnknownUnitError if not found."""

    def register(self, name: str, unit_def: UnitDef) -> None:
        """Register a new unit name."""

    def auto_register_counting_unit(self, name: str) -> UnitDef:
        """Register an unknown name as a new counting dimension.
        'widgets' -> UnitDef(dimensions={'widgets': 1}, scale=1.0)
        Returns the new UnitDef."""

    def aliases(self, canonical_name: str) -> list[str]:
        """Return all registered names for a given canonical name."""

class UnknownUnitError(Exception): ...
```

**Built-in units to register:**

Length: m, meter, meters, km, kilometer, kilometers, cm, centimeter, centimeters,
mm, millimeter, millimeters, ft, foot, feet, in, inch, inches, mi, mile, miles, yd,
yard, yards

Time: s, sec, second, seconds, ms, millisecond, milliseconds, min, minute, minutes,
hr, hour, hours, day, days, week, weeks, month, months, year, years, yr, yrs

Mass: kg, kilogram, kilograms, g, gram, grams, mg, milligram, milligrams,
lb, lbs, pound, pounds, oz, ounce, ounces, ton, tons, tonne, tonnes

Area: acre, acres, hectare, hectares (these are `{"length": 2}` with appropriate scales)

Volume: liter, liters, L, mL, milliliter, milliliters, gallon, gallons, gal

Currency: dollar, dollars, USD, euro, euros, EUR, pound_sterling, GBP, yen, JPY

Energy: joule, joules, J, kJ, kilojoule, kilojoules, calorie, calories, cal, kcal,
kWh, kilowatt_hour, BTU

Power: watt, watts, W, kW, kilowatt, kilowatts, MW, megawatt, megawatts, hp, horsepower

Speed: mph (length/time, scale for miles/hour), kph (km/hour)

Temperature: (skip for now — temperature conversions are affine not multiplicative,
which breaks the "everything is products" model)

**Scale factors** — use SI base as scale=1.0 for each dimension:
- length: meters
- time: seconds
- mass: kilograms
- currency: dollars (arbitrary but needed)
- energy: joules
- power: watts

**Important:** The registry is a singleton-ish default instance but also instantiable
for testing. Provide a module-level `default_registry()` function.

**Edge cases:**

- Looking up `"Meters"` (capitalized) — normalize to lowercase
- Looking up `"person"` vs `"people"` — both should map to `{"people": 1}`
- Looking up `"widgets"` — not found, caller can choose to auto-register

**Tests:** `tests/units/test_registry.py`

```
- test_lookup_known_unit
- test_lookup_alias (meter vs meters vs m)
- test_lookup_case_insensitive
- test_lookup_unknown_raises
- test_register_custom_unit
- test_auto_register_counting_unit
- test_scale_factors_consistent (feet * 1 = 0.3048 meters)
- test_aliases_returns_all_names
```

---

### Task 1.3 — Unit Parser

**File:** `fermi_problems/units/parser.py`

**What it is:** Parses a string like `"meters/second^2"` into a resolved `Unit` object
plus an aggregate scale factor, using the registry.

**Public interface:**

```python
@dataclass
class ParsedUnit:
    """Result of parsing a unit expression string."""
    unit: Unit           # the dimension structure
    scale: float         # aggregate scale factor relative to SI bases

def parse_unit(expr: str, registry: UnitRegistry | None = None) -> ParsedUnit:
    """Parse a unit expression string.

    Grammar:
        unit_expr  = term ("/" term)*
        term       = atom ("*" atom)*
        atom       = NAME ("^" INTEGER)?

    Examples:
        "meters/second"      -> Unit(length=1, time=-1), scale=1.0
        "feet/year"          -> Unit(length=1, time=-1), scale=0.3048/31557600
        "pianos/person"      -> Unit(pianos=1, people=-1), scale=1.0
        "meters/second^2"    -> Unit(length=1, time=-2), scale=1.0
        "km*kg"              -> Unit(length=1, mass=1), scale=1000.0
    """
```

**Parsing rules:**

1. Split on `/` first (each part after the first `/` is a denominator term)
2. Split each term on `*`
3. Each atom is `name` optionally followed by `^integer`
4. Look up each name in the registry to get dimensions and scale
5. Combine: multiply all numerator dimensions/scales, divide by all denominator ones
6. For exponents: raise the atom's dimensions and scale to that power

**Edge cases:**

- Empty string → dimensionless, scale=1.0
- `"1"` or `"dimensionless"` → dimensionless
- Unknown unit name → raise `UnknownUnitError` (caller decides whether to auto-register)
- Whitespace tolerance: `"meters / second"` should work
- No implicit multiplication: `"meters seconds"` is an error (ambiguous with unit names
  that contain spaces — there aren't any, but be explicit)

**Tests:** `tests/units/test_parser.py`

```
- test_parse_single_unit
- test_parse_ratio
- test_parse_with_exponent
- test_parse_compound_numerator
- test_parse_compound_denominator
- test_parse_mixed_units_with_conversion (feet/year)
- test_parse_dimensionless
- test_parse_unknown_unit_raises
- test_parse_whitespace_tolerance
- test_scale_factor_composition
```

---

### Task 1.4 — Unit package __init__.py

**File:** `fermi_problems/units/__init__.py`

Export the public API:

```python
from fermi_problems.units.dimension import Unit
from fermi_problems.units.registry import UnitDef, UnitRegistry, UnknownUnitError, default_registry
from fermi_problems.units.parser import ParsedUnit, parse_unit
```

---

### Task 1.5 — Quantity

**File:** `fermi_problems/core/quantity.py`

**What it is:** A numeric value paired with a Unit. Arithmetic on quantities tracks and
converts units automatically.

**Public interface:**

```python
class Quantity:
    """A numeric value with a unit."""

    def __init__(self, value: float, unit: Unit | str, registry: UnitRegistry | None = None):
        """Create a quantity.
        If unit is a string, parse it via the registry.
        The value is stored in SI-base scale internally."""

    @property
    def value(self) -> float:
        """The value in SI-base units."""

    @property
    def unit(self) -> Unit:
        """The dimensional unit."""

    def in_unit(self, target: str | Unit) -> float:
        """Return the numeric value expressed in the given target unit.
        Raises DimensionError if dimensions don't match."""

    def to(self, target: str | Unit) -> "Quantity":
        """Return a new Quantity expressed in the target unit."""

    def __mul__(self, other: "Quantity | float | int") -> "Quantity":
        """Multiply quantities: multiply values, combine units."""

    def __rmul__(self, other: float | int) -> "Quantity":
        """Support scalar * Quantity."""

    def __truediv__(self, other: "Quantity | float | int") -> "Quantity":
        """Divide quantities: divide values, divide units."""

    def __rtruediv__(self, other: float | int) -> "Quantity":
        """Support scalar / Quantity."""

    def __add__(self, other: "Quantity") -> "Quantity":
        """Add quantities. Must have same dimensions. Converts to common base."""

    def __sub__(self, other: "Quantity") -> "Quantity":
        """Subtract quantities. Must have same dimensions."""

    def __repr__(self) -> str: ...
    def __str__(self) -> str:
        """e.g. '3.0e+08 meters/second'"""

class DimensionError(Exception):
    """Raised when units are incompatible for an operation."""
```

**Internal storage decision:** Store value in SI-base scale internally. When the user
creates `Quantity(60, "miles/hour")`, internally store value as `60 * 1609.34 / 3600`
meters/second. This makes all arithmetic trivial — just multiply/divide the raw floats.
Display conversion happens in `in_unit()` and `to()`.

BUT also store the "display unit" (the parsed unit info) so that `str()` can show the
value in the unit the user originally specified, not always in SI.

**Edge cases:**

- Adding `Quantity(1, "meters") + Quantity(1, "feet")` → result in meters (left operand's unit)
- `Quantity(5, "meters") * Quantity(3, "seconds")` → 15 meter*seconds
- `Quantity(10, "meters") / Quantity(2, "meters")` → 5 dimensionless
- Multiplying by a scalar: `Quantity(5, "meters") * 3` → 15 meters
- Division by zero → raise `ZeroDivisionError` (don't catch it)

**Tests:** `tests/core/test_quantity.py`

```
- test_create_with_string_unit
- test_create_with_unit_object
- test_multiply_quantities
- test_divide_quantities
- test_multiply_by_scalar
- test_divide_by_scalar
- test_add_same_units
- test_add_compatible_units_converts
- test_add_incompatible_units_raises
- test_in_unit_conversion
- test_to_conversion
- test_multiply_to_dimensionless
- test_str_representation
```

---

## Part 2: Uncertainty Propagation

### Task 2.1 — Lognormal Utilities

**File:** `fermi_problems/uncertainty/lognormal.py`

**What it is:** Functions for working with lognormal distributions in the context of
Fermi estimation. No scipy dependency — implement the needed stats functions directly.

**Public interface:**

```python
def normal_ppf(p: float) -> float:
    """Inverse of the standard normal CDF (percent point function).
    Uses the rational approximation from Abramowitz and Stegun.
    Accurate to ~4.5e-4 relative error, which is more than enough
    for Fermi estimation."""

def lognormal_from_range(
    low: float,
    high: float,
    confidence: float = 0.90,
) -> tuple[float, float]:
    """Fit a lognormal distribution to a confidence interval.

    Interprets [low, high] as a symmetric confidence interval
    (e.g., 90% means low=P5, high=P95).

    Returns (log_mean, log_std) — the parameters of the underlying
    normal distribution in ln-space.

    log_mean = (ln(low) + ln(high)) / 2
    log_std = (ln(high) - ln(low)) / (2 * z)
    where z = normal_ppf((1 + confidence) / 2)
    """

def lognormal_point_estimate(log_mean: float) -> float:
    """exp(log_mean) — the geometric mean / median of the lognormal."""

def lognormal_confidence_interval(
    log_mean: float,
    log_std: float,
    confidence: float = 0.90,
) -> tuple[float, float]:
    """Return (low, high) confidence interval for a lognormal distribution."""

def combine_lognormals_product(
    params: list[tuple[float, float]],
) -> tuple[float, float]:
    """Combine independent lognormal distributions via multiplication.

    The product of independent lognormals is lognormal with:
        combined_log_mean = sum of log_means
        combined_log_std = sqrt(sum of log_std^2)

    Args:
        params: list of (log_mean, log_std) tuples

    Returns:
        (combined_log_mean, combined_log_std)
    """

def lognormal_from_point_estimate(
    value: float,
    sig_figs: int = 1,
) -> tuple[float, float]:
    """Infer lognormal parameters from a point estimate.

    With 1 sig fig: assume ±half an order of magnitude (log_std ≈ 0.7)
    With 2 sig figs: assume ±30% (log_std ≈ 0.16)
    With 3+ sig figs: assume ±10% (log_std ≈ 0.06)

    These are heuristics. The idea is that stating '1 million' (1 sig fig)
    means you're less sure than stating '1.2 million' (2 sig figs).
    """
```

**Implementation note on `normal_ppf`:** Use the Abramowitz & Stegun rational
approximation (formula 26.2.23). This avoids the scipy dependency entirely. The
approximation is:

```python
def normal_ppf(p: float) -> float:
    """Rational approximation of the inverse standard normal CDF."""
    # For p < 0.5, use symmetry: ppf(p) = -ppf(1-p)
    if p < 0.5:
        return -normal_ppf(1 - p)
    if p == 0.5:
        return 0.0
    # Abramowitz & Stegun 26.2.23
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3)
```

**Tests:** `tests/uncertainty/test_lognormal.py`

```
- test_normal_ppf_symmetry
- test_normal_ppf_known_values (0.95 ≈ 1.645, 0.975 ≈ 1.96, 0.5 = 0)
- test_lognormal_from_range
- test_lognormal_from_range_round_trip (fit then get CI back)
- test_lognormal_point_estimate
- test_combine_lognormals_product
- test_lognormal_from_point_estimate_1_sig_fig
- test_lognormal_from_point_estimate_2_sig_figs
```

---

### Task 2.2 — Interval Arithmetic

**File:** `fermi_problems/uncertainty/interval.py`

**What it is:** Worst-case bound computation via interval arithmetic. Refactored from
the existing `bounds.py:calculate_interval_product`.

**Public interface:**

```python
def interval_product(
    intervals: list[tuple[float, float]],
) -> tuple[float, float]:
    """Compute the worst-case product interval.

    Given a list of (low, high) ranges, compute the range of the product
    considering all combinations of extremes.

    Handles negative values correctly (relevant if someone has a negative
    factor, though unusual in Fermi problems).
    """

def interval_quotient(
    numerator: tuple[float, float],
    denominator: tuple[float, float],
) -> tuple[float, float]:
    """Compute the interval of a/b.
    Raises ZeroDivisionError if denominator interval contains zero."""
```

**Salvage:** Port `calculate_interval_product` from `bounds.py`, add the quotient
function and negative-value handling.

**Tests:** `tests/uncertainty/test_interval.py`

```
- test_interval_product_basic (existing test case: [(2,5),(10,20),(1,2)] -> [20,200])
- test_interval_product_single
- test_interval_product_many
- test_interval_quotient
- test_interval_quotient_zero_denominator_raises
- test_interval_product_with_negatives
```

---

### Task 2.3 — Error Bound Heuristics

**File:** `fermi_problems/uncertainty/bounds.py`

**What it is:** The heuristic error bound formula from the existing `bounds.py`.

**Public interface:**

```python
def fermi_error_bounds(
    num_steps: int,
    accuracy_factor: float = 2.0,
) -> tuple[float, float]:
    """Heuristic error bounds for a Fermi estimate with N multiplicative steps.

    Rule of thumb: each factor is off by up to `accuracy_factor` in either
    direction. The combined error grows as accuracy_factor^sqrt(num_steps)
    (errors compound in quadrature in log-space).

    Returns (lower_multiplier, upper_multiplier) such that the true answer
    is expected to be between estimate/upper and estimate*upper.

    Example: 9 steps, accuracy=2 -> bounds [0.125, 8]
    """
```

**Salvage:** Directly from existing `bounds.py:fermi_error_bounds`. Simplify the
signature (remove `std_dev` parameter which was unused in the calculation).

**Tests:** `tests/uncertainty/test_bounds.py`

```
- test_fermi_error_bounds_9_steps (existing: [0.125, 8])
- test_fermi_error_bounds_1_step
- test_fermi_error_bounds_symmetry (lower * upper ≈ 1)
- test_fermi_error_bounds_increases_with_steps
```

---

### Task 2.4 — Uncertainty package __init__.py

**File:** `fermi_problems/uncertainty/__init__.py`

Export the public API.

---

## Part 3: Estimate and EstimateChain

### Task 3.1 — Estimate

**File:** `fermi_problems/core/estimate.py`

**What it is:** The central type of the library. A quantity with uncertainty. This is
what users create when they say "about 10 million people, give or take."

**Public interface:**

```python
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
        unit: Unit | str,
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

    @property
    def value(self) -> float:
        """Point estimate (geometric mean if range was given)."""

    @property
    def unit(self) -> Unit: ...

    @property
    def log_mean(self) -> float: ...

    @property
    def log_std(self) -> float: ...

    @property
    def sig_figs(self) -> int: ...

    @property
    def low(self) -> float | None:
        """Lower bound of the input range, if given."""

    @property
    def high(self) -> float | None:
        """Upper bound of the input range, if given."""

    def confidence_interval(self, level: float = 0.90) -> tuple[float, float]:
        """Best-case confidence interval from lognormal model."""

    def __mul__(self, other: "Estimate | Quantity | float | int") -> "Estimate":
        """Multiply estimates: multiply values, combine units, propagate uncertainty."""

    def __rmul__(self, other: float | int) -> "Estimate": ...

    def __truediv__(self, other: "Estimate | Quantity | float | int") -> "Estimate":
        """Divide estimates: divide values, divide units, propagate uncertainty."""

    def __rtruediv__(self, other: float | int) -> "Estimate": ...

    def __repr__(self) -> str: ...
    def __str__(self) -> str:
        """e.g. '~1.0e+06 people [8.0e+05, 1.2e+06]'"""
```

**Uncertainty propagation rules for multiplication/division:**

When multiplying `a * b`:
- `result.log_mean = a.log_mean + b.log_mean`
- `result.log_std = sqrt(a.log_std^2 + b.log_std^2)`
- `result.value = exp(result.log_mean)`
- `result.unit = a.unit * b.unit`
- `result.sig_figs = min(a.sig_figs, b.sig_figs)`

When dividing `a / b`:
- Same but `b.log_mean` is subtracted and `b.unit` is divided.
- `log_std` still adds in quadrature (uncertainty grows either way).

When multiplying/dividing by a scalar (no uncertainty):
- Treat the scalar as an exact value (log_std = 0).

**Tests:** `tests/core/test_estimate.py`

```
- test_create_point_estimate
- test_create_with_range
- test_create_with_sig_figs
- test_confidence_interval_round_trip
- test_multiply_estimates
- test_divide_estimates
- test_multiply_by_scalar
- test_uncertainty_propagation_quadrature
- test_unit_tracking_through_multiplication
- test_sig_figs_propagation
- test_str_representation
```

---

### Task 3.2 — EstimateChain

**File:** `fermi_problems/core/chain.py`

**What it is:** A named collection of Estimates that represent a full Fermi
decomposition. Multiplies them together and provides both best-case and worst-case
bounds.

**Public interface:**

```python
@dataclass
class ChainResult:
    """Result of computing an EstimateChain."""
    estimate: Estimate                          # combined point estimate + uncertainty
    worst_case: tuple[float, float]             # interval arithmetic bounds
    best_case: tuple[float, float]              # lognormal CI (90% default)
    unit_check: bool                            # do units cancel to target?
    unit_mismatch_detail: str | None            # explanation if they don't
    sig_figs: int                               # significant figures in result

class EstimateChain:
    """A Fermi decomposition: a sequence of estimates that multiply to an answer."""

    def __init__(self, target_unit: Unit | str | None = None):
        """Create an empty chain, optionally with a target unit."""

    def add(self, name: str, estimate: Estimate, *, divide: bool = False) -> None:
        """Add a named factor to the chain.
        If divide=True, this factor divides rather than multiplies."""

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

    @property
    def factors(self) -> list[tuple[str, Estimate, bool]]:
        """List of (name, estimate, is_divisor) triples."""

    def compute(self, confidence: float = 0.90) -> ChainResult:
        """Multiply all factors, propagate uncertainty, check units."""

    def validate_units(self) -> tuple[bool, Unit, str | None]:
        """Check if factor units cancel to the target.
        Returns (ok, resulting_unit, error_message_or_none)."""

    def __repr__(self) -> str: ...
```

**The compute() method does:**

1. Multiply/divide all Estimate values (producing a combined Estimate)
2. Get worst-case bounds via interval arithmetic on each factor's [low, high]
3. Get best-case bounds via the combined lognormal CI
4. Check if resulting unit matches target_unit
5. Package everything into ChainResult

**Tests:** `tests/core/test_chain.py`

```
- test_piano_tuners_example (the classic problem, end to end)
- test_empty_chain
- test_single_factor
- test_unit_validation_pass
- test_unit_validation_fail
- test_worst_case_bounds
- test_best_case_bounds
- test_divide_factor
- test_add_factor_convenience
```

---

### Task 3.3 — Significant Figures (simplified)

**File:** `fermi_problems/core/sigfigs.py`

**What it is:** A minimal significant figures tracker for Fermi estimation. Since Fermi
problems are exclusively multiplicative, we only need the multiplication rule: result
has min(sig_figs of operands) significant figures.

**Public interface:**

```python
def infer_sig_figs(value: float) -> int:
    """Infer significant figures from a float value.

    Heuristic: examine the float's string representation.
    - 1e6 -> 1 sig fig
    - 1.5e6 -> 2 sig figs
    - 1.50e6 -> 3 sig figs (if Decimal used)
    - 0.01 -> 1 sig fig
    - 250 -> 2 sig figs (trailing zero ambiguous, assume not significant)

    This is inherently imprecise for floats. When precision matters,
    users should specify sig_figs explicitly.
    """

def round_to_sig_figs(value: float, sig_figs: int) -> float:
    """Round a number to the given number of significant figures."""

def format_sig_figs(value: float, sig_figs: int) -> str:
    """Format a number showing exactly sig_figs significant figures.
    Uses scientific notation for very large/small numbers.
    Example: format_sig_figs(12345, 3) -> '1.23e+04'
    Example: format_sig_figs(0.00456, 2) -> '4.6e-03'
    Example: format_sig_figs(42.0, 2) -> '42'
    """
```

**Salvage:** Take the rounding logic from `significant_numbers.py:SigFig.round_to_sigfigs`.
Do NOT port the full SigFig class or DeferredExpression — those are overengineered for
Fermi use. The Estimate class handles sig fig tracking internally.

**Tests:** `tests/core/test_sigfigs.py`

```
- test_infer_sig_figs_scientific_notation
- test_infer_sig_figs_integer
- test_infer_sig_figs_decimal
- test_round_to_sig_figs
- test_format_sig_figs_large
- test_format_sig_figs_small
- test_format_sig_figs_normal
```

---

### Task 3.4 — Core package __init__.py

**File:** `fermi_problems/core/__init__.py`

Export: `Quantity`, `Estimate`, `EstimateChain`, `ChainResult`, `DimensionError`

---

## Part 4: Formatting

### Task 4.1 — Number Formatting

**File:** `fermi_problems/formatting/notation.py`

**What it is:** Functions for displaying numbers in human-friendly ways appropriate for
Fermi estimation.

**Public interface:**

```python
def to_scientific(value: float, sig_figs: int = 3) -> str:
    """Format in scientific notation: '1.23e+06'."""

def to_engineering(value: float, sig_figs: int = 3) -> str:
    """Format in engineering notation (exponent multiple of 3): '1.23M'.
    Uses suffixes: k, M, B (billion), T (trillion)."""

def to_human(value: float, sig_figs: int = 2) -> str:
    """Format for human reading. Picks the best representation:
    - Small/medium numbers as-is: '42', '1,500'
    - Large numbers with suffix: '10M', '2.5B'
    - Very large/small in scientific notation: '3.0e+23'
    """

def to_order_of_magnitude(value: float) -> str:
    """Format as '~10^N'. Example: 1.5e6 -> '~10^6'."""
```

**Salvage:** Replace the `engineering_notation` dependency entirely.

**Tests:** `tests/formatting/test_notation.py`

```
- test_to_scientific
- test_to_engineering_with_suffixes
- test_to_human_small
- test_to_human_large
- test_to_human_very_large
- test_to_order_of_magnitude
```

---

### Task 4.2 — Result Display

**File:** `fermi_problems/formatting/display.py`

**What it is:** Formats a `ChainResult` into human-readable text output.

**Public interface:**

```python
def format_chain_result(result: ChainResult, show_factors: bool = True) -> str:
    """Format a ChainResult as a multi-line string.

    Example output:
        Estimate: ~108 tuners
        90% CI: [25, 460] tuners (best case, lognormal)
        Worst case: [11, 1080] tuners (interval arithmetic)
        Significant figures: 1
        Unit check: PASS

    If show_factors:
        Factors:
          population       = 2.7e+06 people [2.5e+06, 3.0e+06]
          pianos_per_person = 0.02 pianos/person
          ...
    """

def format_estimate(estimate: Estimate, style: str = "human") -> str:
    """Format a single estimate.
    style: 'human', 'scientific', 'engineering'."""
```

**Tests:** `tests/formatting/test_display.py`

```
- test_format_chain_result_basic
- test_format_chain_result_with_factors
- test_format_estimate_styles
```

---

## Part 5: Order of Magnitude (Salvage)

### Task 5.1 — Move rounding.py

**File:** `fermi_problems/core/magnitude.py`

**What it is:** The existing order-of-magnitude functions from `rounding.py`, cleaned up.

**Public interface:**

```python
def nearest_order_of_magnitude(number: float) -> int:
    """Round log10(number) to nearest integer."""

def order_of_magnitude(number: float) -> int:
    """Order of magnitude using geometric midpoint rounding."""

def order_of_magnitude_range(number: float) -> tuple[float, float]:
    """Range of numbers that share the same order of magnitude."""

def log10_distance(a: float, b: float) -> float:
    """Absolute distance in log10 space. |log10(a) - log10(b)|.
    This is the fundamental 'how close' metric for Fermi estimation."""
```

**Salvage:** Port directly from `rounding.py`. Add `log10_distance` which is used by
scoring. Existing tests should pass with minimal changes.

**Tests:** `tests/core/test_magnitude.py` — port from `tests/test_rounding.py`, add:

```
- (all existing tests from test_rounding.py)
- test_log10_distance
- test_log10_distance_same_oom
```

---

## Part 6: Public API

### Task 6.1 — Package __init__.py

**File:** `fermi_problems/__init__.py`

**What it is:** The public API. Users should be able to do:

```python
from fermi_problems import Estimate, EstimateChain, Quantity, Unit
```

**Exports:**

```python
from fermi_problems.units import Unit, UnitRegistry, parse_unit, default_registry
from fermi_problems.core import Quantity, Estimate, EstimateChain, ChainResult, DimensionError
from fermi_problems.core.magnitude import (
    nearest_order_of_magnitude,
    order_of_magnitude,
    log10_distance,
)
from fermi_problems.formatting.notation import to_scientific, to_engineering, to_human
from fermi_problems.formatting.display import format_chain_result, format_estimate
```

---

## Part 7: Integration Test

### Task 7.1 — Piano Tuners End-to-End

**File:** `tests/test_integration.py`

**What it is:** The classic piano tuners problem, exercising the entire library.

```python
def test_piano_tuners_chicago():
    """End-to-end: How many piano tuners in Chicago?"""
    chain = EstimateChain(target_unit="tuners")

    chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
    chain.add_factor("pianos_per_person", 0.02, "pianos/person", low=0.01, high=0.05)
    chain.add_factor("tunings_per_year", 1.5, "tunings/piano/year", low=1, high=2)
    chain.add_factor("tuner_capacity", 4, "tunings/tuner/day", low=3, high=5, divide=True)
    chain.add_factor("work_days", 250, "days/year", low=240, high=260, divide=True)

    result = chain.compute()

    # Point estimate should be in the right ballpark (50-500 tuners)
    assert 50 < result.estimate.value < 500

    # Units should cancel to "tuners"
    assert result.unit_check is True

    # Best case CI should contain 225 (the commonly cited answer)
    low, high = result.best_case
    assert low < 225 < high

    # Worst case CI should be wider than best case
    wlow, whigh = result.worst_case
    assert wlow <= low
    assert whigh >= high
```

### Task 7.2 — Programmatic API Smoke Test

**File:** `tests/test_integration.py` (continued)

```python
def test_simple_multiplication():
    """Basic estimate multiplication with units."""
    speed = Estimate(60, "miles/hour")
    time = Estimate(2.5, "hours")
    distance = speed * time

    assert distance.unit == Unit({"length": 1})
    assert abs(distance.in_unit("miles") - 150) < 1

def test_unit_conversion():
    """Converting between compatible units."""
    d = Quantity(1, "miles")
    assert abs(d.in_unit("feet") - 5280) < 1
    assert abs(d.in_unit("km") - 1.609) < 0.01
```

---

## Part 8: Cleanup

### Task 8.1 — Remove old modules

Once all new code is tested and working, remove the following old files:

- `fermi_problems/means.py`
- `fermi_problems/use_file.py`
- `fermi_problems/significant.py`
- `fermi_problems/simple_dimensional.py`
- `fermi_problems/inferred_moments.py`
- Dead code (commented-out parser) in `fermi_problems/files.py`

Keep but deprecate (they'll be rewritten in the Game phase):

- `fermi_problems/bounds.py` — functionality moved to `uncertainty/`
- `fermi_problems/game.py` — will be rewritten as `game/session.py`
- `fermi_problems/files.py` — will be rewritten as `game/problems.py`
- `fermi_problems/score.py` — will be rewritten as `game/scoring.py`
- `fermi_problems/rounding.py` — functionality moved to `core/magnitude.py`
- `fermi_problems/significant_numbers.py` — functionality moved to `core/sigfigs.py`

### Task 8.2 — Update pyproject.toml

- Remove `engineering_notation` from dependencies
- Remove `scipy` from dependencies (replaced by `normal_ppf` in lognormal.py)
- Update version number
- Update entry points if needed

### Task 8.3 — Verify all tests pass

Run the full test suite. Every old test that tested math that was ported should have a
corresponding new test. The old tests can remain temporarily (testing the old modules
which still exist) or be migrated.

```bash
make test
```

---

## Summary: File Inventory

New files to create (in order):

| # | File | Depends On |
|---|---|---|
| P1 | Package `__init__.py` files (4 files) | nothing |
| 1.1 | `fermi_problems/units/dimension.py` | nothing |
| 1.2 | `fermi_problems/units/registry.py` | 1.1 |
| 1.3 | `fermi_problems/units/parser.py` | 1.1, 1.2 |
| 1.4 | `fermi_problems/units/__init__.py` | 1.1, 1.2, 1.3 |
| 1.5 | `fermi_problems/core/quantity.py` | 1.* |
| 2.1 | `fermi_problems/uncertainty/lognormal.py` | nothing |
| 2.2 | `fermi_problems/uncertainty/interval.py` | nothing |
| 2.3 | `fermi_problems/uncertainty/bounds.py` | nothing |
| 2.4 | `fermi_problems/uncertainty/__init__.py` | 2.1, 2.2, 2.3 |
| 3.1 | `fermi_problems/core/estimate.py` | 1.*, 2.* |
| 3.2 | `fermi_problems/core/chain.py` | 3.1, 2.2 |
| 3.3 | `fermi_problems/core/sigfigs.py` | nothing |
| 3.4 | `fermi_problems/core/__init__.py` | 3.1, 3.2, 1.5 |
| 4.1 | `fermi_problems/formatting/notation.py` | nothing |
| 4.2 | `fermi_problems/formatting/display.py` | 3.2, 4.1 |
| 5.1 | `fermi_problems/core/magnitude.py` | nothing |
| 6.1 | `fermi_problems/__init__.py` | all above |
| 7.1 | `tests/test_integration.py` | all above |

New test files:

| File | Tests For |
|---|---|
| `tests/units/test_dimension.py` | Task 1.1 |
| `tests/units/test_registry.py` | Task 1.2 |
| `tests/units/test_parser.py` | Task 1.3 |
| `tests/core/test_quantity.py` | Task 1.5 |
| `tests/uncertainty/test_lognormal.py` | Task 2.1 |
| `tests/uncertainty/test_interval.py` | Task 2.2 |
| `tests/uncertainty/test_bounds.py` | Task 2.3 |
| `tests/core/test_estimate.py` | Task 3.1 |
| `tests/core/test_chain.py` | Task 3.2 |
| `tests/core/test_sigfigs.py` | Task 3.3 |
| `tests/formatting/test_notation.py` | Task 4.1 |
| `tests/formatting/test_display.py` | Task 4.2 |
| `tests/core/test_magnitude.py` | Task 5.1 |
| `tests/test_integration.py` | Tasks 7.1, 7.2 |

**Total: ~19 source files, ~14 test files.**
