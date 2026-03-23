# fermi_problems Manual

A Python library for Fermi estimation — quick order-of-magnitude calculations
with unit tracking and uncertainty propagation.

---

## Installation

```bash
pip install fermi_problems
# or with uv:
uv add fermi_problems
```

No external dependencies. Pure Python 3.14+.

---

## Quick Start

```python
from fermi_problems import Estimate, EstimateChain

chain = EstimateChain(target_unit="tuners")
chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
chain.add_factor("pianos_per_person", 0.02, "pianos/person", low=0.01, high=0.05)
chain.add_factor("tunings_per_year", 1.5, "tunings/piano/year", low=1, high=2)
chain.add_factor("tuner_capacity", 4, "tunings/tuner/day", low=3, high=5, divide=True)
chain.add_factor("work_days", 250, "days/year", low=240, high=260, divide=True)

result = chain.compute()
print(result.estimate.value)  # ~90 tuners
print(result.best_case)  # (35, 224) — 90% lognormal CI
print(result.worst_case)  # (19, 416) — interval arithmetic bounds
print(result.unit_check)  # True — units cancel correctly
```

---

## Core Concepts

### Values are stored in SI base units internally

When you create `Estimate(60, "mph")`, the value is converted to meters/second
internally. This makes all arithmetic exact — no unit juggling mid-calculation.
Display conversion happens when you call `in_unit()` or look at `str()`.

### Uncertainty is tracked as a lognormal distribution

Every `Estimate` carries a `(log_mean, log_std)` pair representing a lognormal
distribution in natural-log space. When you multiply two estimates, uncertainties
combine in quadrature:

```
result.log_std = sqrt(a.log_std² + b.log_std²)
```

This is the statistically correct model for multiplicative quantities.

### Units are dimensional, not named

`Unit({"length": 1, "time": -1})` is the dimension "length per time". It does not
care whether you called it "meters/second" or "feet/year" — those are just scale
factors on the same dimension. This means unit checking catches real errors:
if your Fermi chain doesn't cancel to the right dimensions, you'll know.

---

## Module Reference

### `fermi_problems.units`

#### `Unit`

An immutable compound unit stored as a sorted tuple of `(dimension, exponent)` pairs.

```python
from fermi_problems import Unit

# Create units
length = Unit({"length": 1})
time = Unit({"time": 1})
speed = Unit({"length": 1, "time": -1})
area = Unit({"length": 2})
dimensionless = Unit()  # or Unit(None) or Unit({})

# Arithmetic
velocity = length / time  # Unit({"length": 1, "time": -1})
accel = length / time**2  # Unit({"length": 1, "time": -2})
combined = length * time  # Unit({"length": 1, "time": 1})

# Zero exponents are stripped automatically
u = Unit({"length": 1, "time": 0})
assert u == Unit({"length": 1})

# Cancellation
ratio = length / length
assert ratio.is_dimensionless

# Display
print(length / time**2)  # "length/time^2"
print(Unit())  # "dimensionless"

# Inverse
inv = speed.inverse()  # Unit({"length": -1, "time": 1})

# Equality and hashing — safe to use in sets/dicts
assert Unit({"length": 1, "time": -1}) == Unit({"time": -1, "length": 1})
```

---

#### `UnitRegistry`

Maps string names to their canonical `(dimensions, scale_factor)`. The registry
is how string unit expressions like `"miles/hour"` get resolved to actual dimensions
and scale factors.

```python
from fermi_problems.units import UnitRegistry, UnitDef, UnknownUnitError

reg = UnitRegistry()  # comes pre-loaded with ~80 built-in units

# Look up a unit
ud = reg.lookup("feet")
print(ud.scale)  # 0.3048 (relative to meters)
print(ud.dimensions)  # {"length": 1}
print(ud.canonical_name)  # "feet"

# Case-insensitive
reg.lookup("Meters")  # same as "meters"
reg.lookup("METERS")  # same

# Unknown unit raises
try:
    reg.lookup("furlongs")
except UnknownUnitError:
    print("not found")

# Register a custom unit
reg.register(
    "furlong", UnitDef({"length": 1}, scale=201.168, canonical_name="furlongs")
)
reg.lookup("furlong")  # now works

# Auto-register a new counting dimension (no scale conversion needed)
reg.auto_register_counting_unit("widgets")
reg.lookup("widgets")  # UnitDef({"widgets": 1}, scale=1.0)

# List all names for a canonical unit
reg.aliases("meters")  # ["m", "meter", "meters"]
```

**Built-in unit categories:**

| Category | Base unit | Examples |
|---|---|---|
| Length | meters | m, km, cm, mm, ft, in, mi, yd |
| Time | seconds | s, ms, min, hr, day, week, month, year, yr |
| Mass | kilograms | kg, g, mg, lb, oz, ton, tonne |
| Area | m² | acre, hectare |
| Volume | m³ | liter, mL, gallon |
| Currency | dollars | USD, euro, EUR, GBP, JPY |
| Energy | joules | J, kJ, cal, kcal, kWh, BTU |
| Power | watts | W, kW, MW, hp |
| Speed (derived) | m/s | mph, kph |
| Counting | — | people, person, pianos, tuners, tunings |

---

#### `parse_unit`

Parses a unit expression string into a `Unit` plus an aggregate scale factor.

```python
from fermi_problems.units import parse_unit

# Simple
r = parse_unit("meters")
print(r.unit)  # Unit({"length": 1})
print(r.scale)  # 1.0

# Ratio
r = parse_unit("meters/second")
print(r.unit)  # Unit({"length": 1, "time": -1})
print(r.scale)  # 1.0

# With exponent
r = parse_unit("meters/second^2")
print(r.unit)  # Unit({"length": 1, "time": -2})

# Mixed — scale factor is the aggregate conversion
r = parse_unit("feet/year")
print(r.unit)  # Unit({"length": 1, "time": -1})
print(r.scale)  # 0.3048 / 31557600 ≈ 9.66e-9

# Compound numerator
r = parse_unit("km*kg")
print(r.unit)  # Unit({"length": 1, "mass": 1})
print(r.scale)  # 1000.0 (km → m) × 1.0 (kg) = 1000.0

# Dimensionless
r = parse_unit("")
r = parse_unit("1")
r = parse_unit("dimensionless")
# all give: Unit(), scale=1.0

# Whitespace is fine
r = parse_unit("meters / second ^ 2")
```

**Grammar:**
```
unit_expr = term ("/" term)*
term      = atom ("*" atom)*
atom      = NAME ("^" INTEGER)?
```

---

### `fermi_problems.core`

#### `Quantity`

A numeric value with a unit. Values are stored in SI base units internally.

```python
from fermi_problems import Quantity

# Create
q = Quantity(60, "miles/hour")  # internally stored as ~26.82 m/s
print(q.value)  # 26.82... (SI: meters/second)
print(q.unit)  # Unit({"length": 1, "time": -1})

# Convert to a different unit
print(q.in_unit("km/hour"))  # approximately... wait, kph is a named unit:
q2 = Quantity(100, "kph")
print(q2.in_unit("mph"))  # ~62.1

# .to() returns a new Quantity
q_km = Quantity(1000, "meters").to("km")
print(q_km.in_unit("km"))  # 1.0

# Arithmetic — units combine automatically
dist = Quantity(100, "meters")
time = Quantity(10, "seconds")
speed = dist / time
print(speed.value)  # 10.0 (m/s in SI)
print(speed.unit)  # Unit({"length": 1, "time": -1})

# Scalar multiplication
double = dist * 2
triple = 3 * dist

# Addition/subtraction — dimensions must match
q1 = Quantity(1, "meters")
q2 = Quantity(1, "feet")
result = q1 + q2  # adds SI values: 1.0 + 0.3048 = 1.3048 m

# Incompatible dimensions raise DimensionError
from fermi_problems import DimensionError

try:
    Quantity(1, "meters") + Quantity(1, "seconds")
except DimensionError:
    print("Can't add length and time")

# Division to dimensionless
ratio = Quantity(10, "meters") / Quantity(2, "meters")
print(ratio.unit.is_dimensionless)  # True
print(ratio.value)  # 5.0
```

---

#### `Estimate`

A quantity with associated uncertainty, modelled as a lognormal distribution.
This is the main type for Fermi estimation.

```python
from fermi_problems import Estimate

# From a point estimate — sig figs inferred from value
e = Estimate(1e6, "people")
print(e.value)  # ~1e6 (SI)
print(e.sig_figs)  # 1 (inferred: 1e6 has 1 sig fig)

# With explicit sig figs
e = Estimate(1.5e6, "people", sig_figs=2)
print(e.sig_figs)  # 2

# From a range — value becomes the geometric mean
e = Estimate(1e6, "people", low=8e5, high=1.2e6)
print(e.value)  # geometric mean of 8e5 and 1.2e6 ≈ 9.8e5
print(e.low)  # 8e5
print(e.high)  # 1.2e6

# Confidence interval (lognormal model)
lo, hi = e.confidence_interval(0.90)  # 90% CI
lo, hi = e.confidence_interval(0.50)  # 50% CI (tighter)

# Arithmetic — uncertainty propagates in quadrature
population = Estimate(2.7e6, "people", low=2.5e6, high=3e6)
piano_frac = Estimate(0.02, "pianos/person", low=0.01, high=0.05)
pianos = population * piano_frac
print(pianos.unit)  # Unit({"pianos": 1})
print(pianos.sig_figs)  # min(sig figs of inputs)
print(pianos.log_std)  # sqrt(pop.log_std² + piano.log_std²)

# Divide estimates
speed = Estimate(60, "mph")
time = Estimate(2, "hours")
dist = speed * time
print(dist.unit)  # Unit({"length": 1})
print(dist.in_unit("miles"))  # ~120

# Scalar multiply/divide — treated as exact (log_std = 0)
bigger = Estimate(100, "people") * 3
smaller = Estimate(100, "people") / 10

# Convert value to another unit
e = Estimate(1, "miles")
print(e.in_unit("feet"))  # ~5280

# String representation
print(Estimate(1e6, "people", low=5e5, high=2e6))
# ~1.0e+06 people [5.0e+05, 2.0e+06]
```

**Uncertainty propagation rules:**

| Operation | log_mean | log_std |
|---|---|---|
| `a * b` | `a.log_mean + b.log_mean` | `sqrt(a² + b²)` |
| `a / b` | `a.log_mean - b.log_mean` | `sqrt(a² + b²)` |
| `a * scalar` | `a.log_mean + log(scalar)` | `a.log_std` (unchanged) |

---

#### `EstimateChain` and `ChainResult`

A Fermi decomposition: a named sequence of estimates that multiply together.

```python
from fermi_problems import EstimateChain

# Create a chain with an optional target unit for checking
chain = EstimateChain(target_unit="tuners")

# Add factors
chain.add_factor(
    name="population",
    value=2.7e6,
    unit="people",
    low=2.5e6,  # optional lower bound for uncertainty
    high=3e6,  # optional upper bound
)

# Divisor factors (divide=True)
chain.add_factor(
    name="tuner_capacity",
    value=4,
    unit="tunings/tuner/day",
    low=3,
    high=5,
    divide=True,  # this factor divides rather than multiplies
)

# Or add a pre-built Estimate
from fermi_problems import Estimate

e = Estimate(250, "days/year", low=240, high=260)
chain.add(name="work_days", estimate=e, divide=True)

# Inspect factors
for name, est, is_divisor in chain.factors:
    print(
        f"{'/' if is_divisor else '*'} {name}: {est.value:.2g} {est._display_unit_str}"
    )

# Compute
result = chain.compute(confidence=0.90)

# ChainResult fields:
print(result.estimate.value)  # combined point estimate (SI)
print(result.best_case)  # (low, high) — lognormal 90% CI
print(result.worst_case)  # (low, high) — interval arithmetic
print(result.unit_check)  # True/False — do units cancel?
print(result.unit_mismatch_detail)  # error message if unit_check is False
print(result.sig_figs)  # significant figures in result

# Validate units without computing
ok, result_unit, msg = chain.validate_units()
print(ok)  # True/False
print(result_unit)  # the resulting Unit after all multiplications/divisions
print(msg)  # None if ok, else explanation
```

**Unit checking example:**

```python
# This chain's units should cancel to "tuners":
# people × (pianos/person) × (tunings/piano/year)
#         / (tunings/tuner/day) / (days/year)
# = people × pianos/person × tunings/piano/year × tuner/tunings/day × year/days
# = tuners  ✓

chain = EstimateChain(target_unit="tuners")
chain.add_factor("population", 2.7e6, "people")
chain.add_factor("pianos_per_person", 0.02, "pianos/person")
chain.add_factor("tunings_per_year", 1.5, "tunings/piano/year")
chain.add_factor("tuner_capacity", 4, "tunings/tuner/day", divide=True)
chain.add_factor("work_days", 250, "days/year", divide=True)
result = chain.compute()
assert result.unit_check  # passes
```

---

### `fermi_problems.uncertainty`

These are the building blocks used internally by `Estimate` and `EstimateChain`.
You can use them directly for custom calculations.

#### `lognormal.py`

```python
from fermi_problems.uncertainty.lognormal import (
    normal_ppf,
    lognormal_from_range,
    lognormal_point_estimate,
    lognormal_confidence_interval,
    combine_lognormals_product,
    lognormal_from_point_estimate,
)

# Inverse normal CDF — no scipy needed
normal_ppf(0.95)  # ≈ 1.645
normal_ppf(0.975)  # ≈ 1.960
normal_ppf(0.5)  # 0.0

# Fit lognormal to a confidence interval
# Interprets [low, high] as a 90% CI (P5, P95)
log_mean, log_std = lognormal_from_range(100, 10000, confidence=0.90)
# geometric mean is sqrt(100 * 10000) = 1000
import math

assert math.isclose(math.exp(log_mean), 1000, rel_tol=0.01)

# Round-trip: fit then recover interval
lo, hi = lognormal_confidence_interval(log_mean, log_std, confidence=0.90)
# lo ≈ 100, hi ≈ 10000

# Combine independent lognormals via multiplication
# (product of lognormals is lognormal)
params = [
    (math.log(100), 0.5),  # mean=100, spread=0.5 in ln space
    (math.log(1000), 0.3),  # mean=1000
]
combined_mean, combined_std = combine_lognormals_product(params)
# combined_mean = log(100) + log(1000) = log(100000)
# combined_std  = sqrt(0.5² + 0.3²) ≈ 0.583

# Infer lognormal params from a point estimate
# (uncertainty reflects the precision implied by the value's sig figs)
log_mean, log_std = lognormal_from_point_estimate(1_000_000, sig_figs=1)
# sig_figs=1 → large spread (~half OOM)
log_mean, log_std = lognormal_from_point_estimate(1_200_000, sig_figs=2)
# sig_figs=2 → ~30% spread
log_mean, log_std = lognormal_from_point_estimate(1_230_000, sig_figs=3)
# sig_figs=3 → ~10% spread
```

#### `interval.py`

Worst-case bound computation — does not assume any distribution shape.

```python
from fermi_problems.uncertainty.interval import interval_product, interval_quotient

# Multiply intervals: considers all combinations of extremes
low, high = interval_product([(2, 5), (10, 20), (1, 2)])
# low = 2*10*1 = 20
# high = 5*20*2 = 200

# Single interval
interval_product([(3, 7)])  # (3, 7)

# Handles negatives correctly
interval_product([(-2, -1), (-2, -1)])  # (1, 4)

# Divide intervals
low, high = interval_quotient((10, 20), (2, 5))
# = interval_product([(10,20), (1/5, 1/2)])
# low = 10/5 = 2, high = 20/2 = 10

# Zero in denominator raises
interval_quotient((1, 10), (-1, 1))  # ZeroDivisionError
```

#### `bounds.py`

Heuristic error bounds based on number of estimation steps.

```python
from fermi_problems.uncertainty.bounds import fermi_error_bounds

# 9 multiplicative steps, each off by factor of 2 at most
lower, upper = fermi_error_bounds(num_steps=9, accuracy_factor=2.0)
# lower = 0.125  (1/8)
# upper = 8.0

# Interpretation: with 9 steps, the true answer is likely within
# [estimate * 0.125, estimate * 8] — a factor of 8 in either direction

# 1 step: just the accuracy_factor itself
fermi_error_bounds(1)  # (0.5, 2.0)

# The bounds are always symmetric in log space: lower * upper = 1
```

---

### `fermi_problems.core.magnitude`

Order-of-magnitude utilities.

```python
from fermi_problems.core.magnitude import (
    order_of_magnitude,
    nearest_order_of_magnitude,
    order_of_magnitude_range,
    log10_distance,
)

# Which power of 10 a number is closest to (geometric midpoint rounding)
order_of_magnitude(4e6)  # 7   (closer to 10^7 than 10^6 geometrically)
order_of_magnitude(1.7e8)  # 8
order_of_magnitude(3.7e8)  # 9
order_of_magnitude(0.2)  # -1
order_of_magnitude(5)  # 1   (5 > sqrt(10) ≈ 3.16, so rounds up)

# Nearest: just round(log10(x))
nearest_order_of_magnitude(4e6)  # 7
nearest_order_of_magnitude(999)  # 3

# Range of numbers that share the same order of magnitude
order_of_magnitude_range(5)  # (1, 10)
order_of_magnitude_range(50)  # (10, 100)

# Distance in log10 space — the fundamental Fermi "closeness" metric
log10_distance(10, 100)  # 1.0  (one order of magnitude apart)
log10_distance(100, 10)  # 1.0  (absolute value)
log10_distance(1000, 2000)  # ≈ 0.301
log10_distance(x, x)  # 0.0
```

---

### `fermi_problems.core.sigfigs`

Significant figures utilities.

```python
from fermi_problems.core.sigfigs import (
    infer_sig_figs,
    round_to_sig_figs,
    format_sig_figs,
)

# Infer sig figs from float representation
infer_sig_figs(1e6)  # 1
infer_sig_figs(1.5e6)  # 2
infer_sig_figs(1.23e6)  # 3
infer_sig_figs(0.01)  # 1
infer_sig_figs(250.0)  # 2

# Round to sig figs
round_to_sig_figs(12345, 3)  # 12300.0
round_to_sig_figs(0.00456, 2)  # 0.0046
round_to_sig_figs(1.567e6, 3)  # 1570000.0

# Format as string with exactly N sig figs
format_sig_figs(12345, 3)  # "1.23e+04"
format_sig_figs(0.00456, 2)  # "4.6e-03"
format_sig_figs(42.0, 2)  # "42"
format_sig_figs(1500, 2)  # "1500"
```

---

### `fermi_problems.formatting`

Human-readable number and result formatting.

```python
from fermi_problems.formatting.notation import (
    to_scientific,
    to_engineering,
    to_human,
    to_order_of_magnitude,
)

# Scientific notation
to_scientific(1234567, 3)  # "1.23e+06"
to_scientific(0.001234, 3)  # "1.23e-03"

# Engineering notation (exponent multiple of 3, with suffix)
to_engineering(1234567, 3)  # "1.23M"
to_engineering(1234, 3)  # "1.23k"
to_engineering(1.5e9, 2)  # "1.5B"

# Human-friendly (picks best format automatically)
to_human(42)  # "42"
to_human(1500)  # "1.5k"
to_human(1.5e6)  # "1.5M"
to_human(3e23)  # "3.0e+23"

# Order of magnitude label
to_order_of_magnitude(1.5e6)  # "~10^6"
to_order_of_magnitude(1e3)  # "~10^3"
```

```python
from fermi_problems.formatting.display import format_chain_result, format_estimate
from fermi_problems import Estimate

# Format a single estimate
e = Estimate(1e6, "people", low=5e5, high=2e6)
print(format_estimate(e, style="human"))  # ~1.0M people [5.0e+05, 2.0e+06]
print(format_estimate(e, style="scientific"))  # ~1.00e+06 people [5.0e+05, 2.0e+06]
print(format_estimate(e, style="engineering"))  # ~1.0M people [5.0e+05, 2.0e+06]

# Format a full chain result
from fermi_problems import EstimateChain

chain = EstimateChain(target_unit="tuners")
chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
chain.add_factor("pianos_per_person", 0.02, "pianos/person", low=0.01, high=0.05)
result = chain.compute()

print(format_chain_result(result, show_factors=False))
# Estimate: ~54k pianos
# 90% CI: [5.7k, 510k] pianos (best case, lognormal)
# Worst case: [12.5k, 150k] pianos (interval arithmetic)
# Significant figures: 1
# Unit check: PASS
```

---

## Worked Examples

### Example 1 — How many piano tuners in Chicago?

The classic Fermi problem. Chicago has ~2.7M people; roughly 1 in 50 households
has a piano; each piano is tuned ~1.5 times/year; a tuner does ~4 tunings/day;
there are ~250 working days/year.

```python
from fermi_problems import EstimateChain
from fermi_problems.formatting.display import format_chain_result

chain = EstimateChain(target_unit="tuners")
chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
chain.add_factor("pianos_per_person", 0.02, "pianos/person", low=0.01, high=0.05)
chain.add_factor("tunings_per_year", 1.5, "tunings/piano/year", low=1, high=2)
chain.add_factor("tuner_capacity", 4, "tunings/tuner/day", low=3, high=5, divide=True)
chain.add_factor("work_days", 250, "days/year", low=240, high=260, divide=True)

result = chain.compute()
print(format_chain_result(result))
```

Output:
```
Estimate: ~90 tuners
90% CI: [36, 224] tuners (best case, lognormal)
Worst case: [19, 417] tuners (interval arithmetic)
Significant figures: 1
Unit check: PASS
```

---

### Example 2 — Distance from speed and time

```python
from fermi_problems import Estimate

speed = Estimate(60, "mph")
duration = Estimate(2.5, "hours")
distance = speed * duration

print(distance.unit)  # Unit({"length": 1})
print(distance.in_unit("miles"))  # ~150.0
print(distance.in_unit("km"))  # ~241.4
```

---

### Example 3 — Unit conversion with `Quantity`

```python
from fermi_problems import Quantity

# 1 mile in various units
one_mile = Quantity(1, "miles")
print(one_mile.in_unit("feet"))  # 5280.0
print(one_mile.in_unit("km"))  # ~1.609
print(one_mile.in_unit("meters"))  # ~1609.3

# Arithmetic
d1 = Quantity(5, "km")
d2 = Quantity(3, "miles")
total = d1 + d2  # adds SI values: 5000 + 4828 = 9828 m
print(total.in_unit("km"))  # ~9.83
```

---

### Example 4 — Custom counting units

When you use a unit name that's not in the built-in registry, register it first:

```python
from fermi_problems.units import default_registry, UnitDef
from fermi_problems import Estimate, EstimateChain

reg = default_registry()
reg.auto_register_counting_unit("widgets")
reg.auto_register_counting_unit("factories")

chain = EstimateChain(target_unit="widgets")
chain.add_factor("factories", 1000, "factories")
chain.add_factor(
    "widgets_per_day", 500, "widgets/factories"
)  # note: already registered
result = chain.compute()
```

Or pass a custom registry:

```python
from fermi_problems.units import UnitRegistry, UnitDef
from fermi_problems import Estimate

reg = UnitRegistry()
reg.auto_register_counting_unit("sprockets")
reg.auto_register_counting_unit("machines")

e = Estimate(50, "sprockets", registry=reg)
```

---

### Example 5 — Using uncertainty functions directly

```python
import math
from fermi_problems.uncertainty.lognormal import (
    lognormal_from_range,
    lognormal_confidence_interval,
    combine_lognormals_product,
)
from fermi_problems.uncertainty.interval import interval_product

# You estimate a quantity is between 100 and 10,000 (90% confident)
log_mean, log_std = lognormal_from_range(100, 10_000, confidence=0.90)
point = math.exp(log_mean)  # geometric mean: 1000
lo, hi = lognormal_confidence_interval(log_mean, log_std, 0.50)  # tighter 50% CI

# Combine two uncertain estimates multiplicatively
a_params = lognormal_from_range(10, 100)
b_params = lognormal_from_range(5, 50)
combined_mean, combined_std = combine_lognormals_product([a_params, b_params])
# result is lognormal with these params

# Worst-case bounds (no distributional assumption)
lo, hi = interval_product([(10, 100), (5, 50)])
# lo = 50, hi = 5000 — widest possible range
```

---

## API Quick Reference

```python
# Top-level imports
from fermi_problems import (
    Unit,
    UnitRegistry,
    parse_unit,
    default_registry,
    Quantity,
    Estimate,
    EstimateChain,
    ChainResult,
    DimensionError,
    nearest_order_of_magnitude,
    order_of_magnitude,
    log10_distance,
    to_scientific,
    to_engineering,
    to_human,
    format_chain_result,
    format_estimate,
)
```

| Class/Function | Module | Purpose |
|---|---|---|
| `Unit` | `units.dimension` | Immutable compound unit |
| `UnitDef` | `units.registry` | Named unit definition (dims + scale) |
| `UnitRegistry` | `units.registry` | Registry of unit names |
| `UnknownUnitError` | `units.registry` | Raised on unknown unit name |
| `parse_unit` | `units.parser` | Parse unit expression string |
| `default_registry` | `units.registry` | Module-level singleton registry |
| `Quantity` | `core.quantity` | Value with unit, SI-internal |
| `DimensionError` | `core.quantity` | Raised on incompatible unit ops |
| `Estimate` | `core.estimate` | Value + lognormal uncertainty |
| `EstimateChain` | `core.chain` | Fermi decomposition |
| `ChainResult` | `core.chain` | Output of `chain.compute()` |
| `order_of_magnitude` | `core.magnitude` | Geometric OOM of a number |
| `log10_distance` | `core.magnitude` | Distance in log10 space |
| `infer_sig_figs` | `core.sigfigs` | Sig figs from float repr |
| `format_sig_figs` | `core.sigfigs` | Format with N sig figs |
| `normal_ppf` | `uncertainty.lognormal` | Inverse normal CDF |
| `lognormal_from_range` | `uncertainty.lognormal` | Fit lognormal to CI |
| `combine_lognormals_product` | `uncertainty.lognormal` | Multiply lognormals |
| `interval_product` | `uncertainty.interval` | Worst-case product bounds |
| `fermi_error_bounds` | `uncertainty.bounds` | Heuristic N-step bounds |
| `to_scientific` | `formatting.notation` | Format as `1.23e+06` |
| `to_engineering` | `formatting.notation` | Format as `1.23M` |
| `to_human` | `formatting.notation` | Format for human reading |
| `format_chain_result` | `formatting.display` | Multi-line result summary |
