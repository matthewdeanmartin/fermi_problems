# Fermi Problems Core Library: Analysis & Redesign

## 1. Assessment of Current State

### What Exists

The current codebase is a collection of independent modules that each solve a piece of the
Fermi estimation puzzle, but they don't talk to each other. There's no spine connecting them.

| Module                   | What It Does                                 | Quality                                   |
|--------------------------|----------------------------------------------|-------------------------------------------|
| `bounds.py`              | Error bound compounding, interval arithmetic | Sound math, usable                        |
| `means.py`               | Approximate geometric mean from ranges       | Two versions, neither is just `sqrt(a*b)` |
| `rounding.py`            | Order of magnitude classification            | Solid, well-tested                        |
| `score.py`               | Olympiad-style scoring (0/1/3/5 points)      | Works, simple                             |
| `significant_numbers.py` | SigFig class with operator overloading       | Decent, incomplete DeferredExpression     |
| `significant.py`         | Count sig digits from string                 | Bugs with scientific notation             |
| `simple_dimensional.py`  | Cancel matching unit strings                 | Toy implementation                        |
| `inferred_moments.py`    | Infer normal distribution from P5/P95        | One function, scipy dependency            |
| `files.py`               | Parse `.txt` problem files                   | Fragile, duplicated branches, dead code   |
| `game.py`                | Console factor entry                         | No scoring, no problem data, no units     |
| `use_file.py`            | Engineering notation wrapper                 | Sketch only                               |

### What's Wrong

**No integration layer.** Each module is an island. There's no type that represents "a
quantity with a value, uncertainty, and unit" that flows through the system. You can't take
a problem file, parse it, compute the estimate, propagate uncertainty, track units, and
score the result in one pipeline.

**Units are strings, not algebra.** `simple_dimensional.py` cancels matching strings like
`"year"` in numerator and denominator. It can't convert feet to meters, can't handle
`meters/second^2`, can't detect dimensional incompatibility. It's a party trick, not
dimensional analysis.

**No DSL.** The game expects users to enter raw floats via `input()`. The file format in
`piano.txt` is a reasonable start for a problem definition format, but there's no way for a
user to express "10 million people * 1 piano per 100 people * 2 tunings per year" in a
natural way and get back a computed result with units and uncertainty.

**Uncertainty is scattered.** Interval arithmetic is in `bounds.py`. Distribution inference
is in `inferred_moments.py`. The SigFig class tracks precision. But none of these compose.
You can't say "this factor is 10 million ± a factor of 2, lognormally distributed" and have
that propagate through a product of five factors.

**`__init__.py` is empty, `__main__.py` doesn't exist.** The package has no public API and
the declared CLI entry point is broken.

---

## 2. Design Goals

### Primary Use Case: The Fermi Game

A player is presented with a question like "How many piano tuners are in Chicago?" They
decompose it into factors, enter estimates for each factor (with units and uncertainty),
and the system:

1. Checks that the units are dimensionally consistent and cancel to the right answer unit
2. Computes the point estimate (product of geometric means)
3. Propagates uncertainty to give confidence bounds
4. Compares to a known answer and scores the result

### Secondary Use Case: The Core Library

Developers and educators can use the library programmatically to:

- Build quantities with values, units, and uncertainty
- Multiply/divide quantities with automatic unit tracking and conversion
- Propagate uncertainty through chains of estimates
- Round and present results respecting significant figures

### Tertiary Use Case: The DSL

A lightweight expression language lets users write estimates without being programmers:

```
population = 10M people
pianos_per_person = 1/100 pianos/person
tunings = 2 tunings/piano/year
tuner_capacity = 4 tunings/tuner/day * 250 days/year
answer = population * pianos_per_person * tunings / tuner_capacity -> tuners
```

---

## 3. Core Library Design

### 3.1 Unit System

Units are the hardest part and must be designed first. Everything else builds on them.

#### Representation

A unit is a sorted mapping from base dimension strings to integer exponents:

```python
@dataclass(frozen=True)
class Unit:
    """Immutable unit represented as dimension -> exponent mapping."""
    dimensions: tuple[tuple[str, int], ...]  # sorted for equality

    # Examples:
    # meters/second  -> (("length", 1), ("time", -1))
    # dollars        -> (("currency", 1),)
    # dimensionless  -> ()
```

We do NOT try to enumerate all possible units upfront. Instead, we define a registry of
**known units** that maps surface names to their canonical dimension + scale factor:

```python
UNIT_REGISTRY = {
    # Length
    "m":       UnitDef(dimensions={"length": 1}, scale=1.0),
    "meter":   UnitDef(dimensions={"length": 1}, scale=1.0),
    "meters":  UnitDef(dimensions={"length": 1}, scale=1.0),
    "km":      UnitDef(dimensions={"length": 1}, scale=1000.0),
    "ft":      UnitDef(dimensions={"length": 1}, scale=0.3048),
    "feet":    UnitDef(dimensions={"length": 1}, scale=0.3048),
    "mi":      UnitDef(dimensions={"length": 1}, scale=1609.34),
    "mile":    UnitDef(dimensions={"length": 1}, scale=1609.34),
    "miles":   UnitDef(dimensions={"length": 1}, scale=1609.34),

    # Time
    "s":       UnitDef(dimensions={"time": 1}, scale=1.0),
    "second":  UnitDef(dimensions={"time": 1}, scale=1.0),
    "min":     UnitDef(dimensions={"time": 1}, scale=60.0),
    "minute":  UnitDef(dimensions={"time": 1}, scale=60.0),
    "hr":      UnitDef(dimensions={"time": 1}, scale=3600.0),
    "hour":    UnitDef(dimensions={"time": 1}, scale=3600.0),
    "day":     UnitDef(dimensions={"time": 1}, scale=86400.0),
    "days":    UnitDef(dimensions={"time": 1}, scale=86400.0),
    "year":    UnitDef(dimensions={"time": 1}, scale=31557600.0),
    "years":   UnitDef(dimensions={"time": 1}, scale=31557600.0),

    # Mass
    "kg":      UnitDef(dimensions={"mass": 1}, scale=1.0),
    "lb":      UnitDef(dimensions={"mass": 1}, scale=0.453592),
    "lbs":     UnitDef(dimensions={"mass": 1}, scale=0.453592),

    # "Counting" units (people, pianos, tuners, etc.)
    # These are user-defined and contextual. See below.
}
```

**Key design decision: counting units.** Fermi problems are full of units like "people",
"pianos", "tuners", "tunings" that aren't physical dimensions. We handle these as
**opaque counting dimensions** — each distinct counting noun becomes its own dimension:

```python
"people":   UnitDef(dimensions={"people": 1}, scale=1.0),
"person":   UnitDef(dimensions={"people": 1}, scale=1.0),
"pianos":   UnitDef(dimensions={"pianos": 1}, scale=1.0),
"piano":    UnitDef(dimensions={"pianos": 1}, scale=1.0),
"tuners":   UnitDef(dimensions={"tuners": 1}, scale=1.0),
"tuner":    UnitDef(dimensions={"tuners": 1}, scale=1.0),
"tunings":  UnitDef(dimensions={"tunings": 1}, scale=1.0),
"tuning":   UnitDef(dimensions={"tunings": 1}, scale=1.0),
```

The registry is extensible at runtime. Unknown unit tokens encountered in parsing are
auto-registered as new counting dimensions (with a warning).

#### Operations

```python
Unit.__mul__(other: Unit) -> Unit     # meters * seconds = meter·seconds
Unit.__truediv__(other: Unit) -> Unit # meters / seconds = meters/second
Unit.__pow__(n: int) -> Unit          # meters ** 2 = square meters
Unit.is_compatible(other: Unit) -> bool
Unit.conversion_factor(other: Unit) -> float  # raises if incompatible
Unit.is_dimensionless() -> bool
```

#### Unit Parsing

Parse compound unit expressions from strings:

```
"meters/second"          -> length¹ · time⁻¹
"pianos/person"          -> pianos¹ · people⁻¹
"tunings/piano/year"     -> tunings¹ · pianos⁻¹ · time⁻¹
"dollars/year"           -> currency¹ · time⁻¹
"meters/second^2"        -> length¹ · time⁻²
```

Grammar:

```
unit_expr  = term ("/" term)*
term       = atom ("*" atom)*
atom       = NAME ("^" INTEGER)?
```

### 3.2 Quantity — The Central Type

A `Quantity` bundles a numeric value with a unit:

```python
@dataclass
class Quantity:
    value: float
    unit: Unit

    def __mul__(self, other: Quantity) -> Quantity: ...
    def __truediv__(self, other: Quantity) -> Quantity: ...
    def to(self, target_unit: Unit) -> Quantity: ...  # unit conversion
    def __repr__(self) -> str: ...  # "1.5e6 meters/second"
```

Multiplication/division multiplies values and combines units. Addition/subtraction requires
compatible units (same dimensions) and converts to a common scale.

### 3.3 Estimate — Quantity + Uncertainty

An `Estimate` is what users actually work with. It wraps a `Quantity` with uncertainty
information:

```python
class Estimate:
    """A quantity with associated uncertainty."""

    def __init__(
        self,
        value: float,
        unit: Unit | str,          # parsed if string
        *,
        low: float | None = None,  # lower bound (e.g. P5)
        high: float | None = None, # upper bound (e.g. P95)
        sig_figs: int | None = None,
    ): ...
```

There are multiple ways to express uncertainty, all normalized internally:

| Input Style        | Example                                                | Internal Representation                 |
|--------------------|--------------------------------------------------------|-----------------------------------------|
| Point estimate     | `Estimate(1e6, "people")`                              | value=1e6, sig_figs inferred from input |
| Range              | `Estimate(1e6, "people", low=800_000, high=1_200_000)` | lognormal fit to range                  |
| Order of magnitude | `Estimate(1e6, "people", sig_figs=1)`                  | ±half an order of magnitude             |

Internally, every Estimate stores:

- `value`: the point estimate (geometric mean if range given)
- `unit`: the Unit
- `log_mean`: mean of ln(value), for lognormal propagation
- `log_std`: std dev of ln(value), for lognormal propagation
- `sig_figs`: significant figures

#### Why Lognormal?

Fermi estimates are products of positive quantities. The Central Limit Theorem applied to
log-space says the product of many independent positive random variables tends toward
lognormal. This is the standard statistical model for Fermi estimation (see Mahajan,
"Street-Fighting Mathematics"; Weinstein & Adam, "Guesstimation").

When a user gives a range `[low, high]` interpreted as a 90% confidence interval:

```python
log_mean = (ln(low) + ln(high)) / 2
log_std = (ln(high) - ln(low)) / (2 * 1.645)  # 1.645 = z for 95th percentile
```

The point estimate is `exp(log_mean)` = geometric mean of the bounds.

#### Propagation Through Products

When multiplying Estimates:

```python
result.log_mean = sum(e.log_mean for e in factors)
result.log_std = sqrt(sum(e.log_std**2 for e in factors))  # quadrature
result.value = exp(result.log_mean)
result.unit = product of all units
result.sig_figs = min of all sig_figs
```

This gives us the "best case" bounds from the README — errors partially cancel in
quadrature rather than compounding multiplicatively. The interval arithmetic in `bounds.py`
gives the worst case (all errors in same direction).

#### Deriving Bounds from Propagated Uncertainty

```python
Estimate.confidence_interval(level=0.90) -> tuple[float, float]
    # Returns (low, high) from the lognormal distribution
    z = norm.ppf((1 + level) / 2)
    low = exp(self.log_mean - z * self.log_std)
    high = exp(self.log_mean + z * self.log_std)
```

#### Interval Arithmetic (Worst Case)

Keep the existing `calculate_interval_product` logic from `bounds.py`, but integrate it
into Estimate:

```python
Estimate.worst_case_interval() -> tuple[float, float]
    # From the stored low/high of each factor
```

### 3.4 EstimateChain — Composing a Full Fermi Estimate

```python
class EstimateChain:
    """A sequence of Estimates that multiply together to produce an answer."""

    factors: list[Estimate]
    target_unit: Unit | None  # what we expect the answer to be in

    def compute(self) -> Estimate:
        """Multiply all factors, propagate uncertainty, check units."""

    def validate_units(self) -> bool:
        """Check that factor units cancel to target_unit."""

    def worst_case_bounds(self) -> tuple[float, float]:
        """Interval arithmetic across all factors."""

    def best_case_bounds(self, confidence: float = 0.90) -> tuple[float, float]:
        """Lognormal propagation confidence interval."""
```

### 3.5 Module Map

```
fermi_problems/
├── __init__.py              # Public API exports
├── __main__.py              # CLI entry point
├── units/
│   ├── __init__.py
│   ├── dimension.py         # Unit class, dimension algebra
│   ├── registry.py          # Known units, conversions, aliases
│   └── parser.py            # Parse "meters/second^2" -> Unit
├── core/
│   ├── __init__.py
│   ├── quantity.py           # Quantity = value + unit
│   ├── estimate.py           # Estimate = quantity + uncertainty
│   ├── chain.py              # EstimateChain = list of estimates -> answer
│   └── sigfigs.py            # Significant figures tracking
├── uncertainty/
│   ├── __init__.py
│   ├── lognormal.py          # Lognormal propagation
│   ├── interval.py           # Interval arithmetic (worst case)
│   └── bounds.py             # Error bound heuristics
├── dsl/
│   ├── __init__.py
│   ├── lexer.py              # Tokenize DSL input
│   ├── parser.py             # Parse tokens into AST
│   └── evaluator.py          # Evaluate AST using core types
├── game/
│   ├── __init__.py
│   ├── problems.py           # Problem database / file loading
│   ├── scoring.py            # Scoring systems (Olympiad, continuous, etc.)
│   └── session.py            # Game session management
├── formatting/
│   ├── __init__.py
│   ├── notation.py           # Scientific/engineering notation display
│   └── display.py            # Pretty-print results
└── compat/
    └── legacy.py             # Thin wrappers around old module functions
```

---

## 4. The DSL

### 4.1 Design Principles

- Looks like math, not code
- Units are first-class — you write them inline
- Ranges and magnitudes have concise syntax
- Errors are helpful — "these units don't cancel" not "TypeError"

### 4.2 Syntax

```
# Comments start with #

# Simple assignment
population = 10M people

# With range (brackets = 90% confidence interval)
population = 10M people [8M, 12M]

# Fractional/ratio values
pianos_per_person = 1/100 pianos/person

# Explicit scientific notation
speed = 3e8 meters/second

# Suffixes: k (1e3), M (1e6), B (1e9), T (1e12)
gdp = 25T dollars/year

# Order-of-magnitude only (tilde prefix)
stars = ~1e11 stars

# Multiplication chain
answer = population * pianos_per_person * tunings_per_year / tuner_capacity

# Unit target (arrow asserts final unit)
answer -> tuners

# Inline computation
answer = 10M people * 0.01 pianos/person * 2 tunings/piano/year
         / (4 tunings/tuner/day * 250 days/year) -> tuners
```

### 4.3 Grammar (EBNF)

```ebnf
program     = { statement } ;
statement   = assignment | assertion | comment ;
assignment  = IDENT "=" expression ;
assertion   = expression "->" unit_expr ;
expression  = term { ("*" | "/") term } ;
term        = number unit_expr? range?
            | IDENT
            | "(" expression ")" ;
number      = FLOAT | INT | sci_notation | suffix_notation ;
sci_notation = FLOAT "e" INT ;
suffix_notation = FLOAT ("k" | "M" | "B" | "T") ;
range       = "[" number "," number "]" ;
unit_expr   = unit_atom { ("/" | "*") unit_atom } ;
unit_atom   = IDENT ( "^" INT )? ;
comment     = "#" .* ;
```

### 4.4 Semantics

1. **Number parsing**: `10M` -> `10_000_000`, `3e8` -> `300_000_000`, `1/100` -> `0.01`
2. **Unit attachment**: `10M people` creates `Estimate(1e7, "people")`
3. **Range attachment**: `10M people [8M, 12M]` sets low=8e6, high=1.2e7
4. **Multiplication**: `a * b` multiplies values, combines units, propagates uncertainty
5. **Division**: `a / b` divides values, divides units
6. **Parentheses**: group sub-expressions (useful for `tuner_capacity` above)
7. **Arrow assertion**: `expr -> unit` checks that the result has the stated unit dimensions

### 4.5 Error Messages

```
Line 5: Unit mismatch in multiplication
  population * speed
  ~~~~~~~~~   ~~~~~
  people      meters/second

  Result has unit: people·meters/second
  This doesn't simplify to a meaningful single unit.
  Did you mean to divide instead?

Line 8: Dimensional inconsistency
  answer -> tuners
  Result has unit: tunings/day
  Expected: tuners
  These are different counting dimensions.
  Check that your factors include a "tunings/tuner" conversion.
```

---

## 5. Scoring System

### 5.1 Existing: Olympiad Scoring

Keep the current `calculate_olympiad_score` — it's clean and well-tested. Scores 0/1/3/5
based on order-of-magnitude distance.

### 5.2 New: Continuous Log-Distance Score

The Olympiad system is coarse. A continuous score rewards getting closer:

```python
def continuous_score(estimate: float, actual: float, max_points: float = 10.0) -> float:
    """Score based on log-distance. Perfect = max_points, decays with distance."""
    log_error = abs(math.log10(estimate) - math.log10(actual))
    # Gaussian decay: score = max_points * exp(-(log_error)^2 / 2)
    # Within same OOM: ~10 points
    # 1 OOM off: ~6 points
    # 2 OOM off: ~1.4 points
    # 3 OOM off: ~0.1 points
    return max_points * math.exp(-0.5 * log_error ** 2)
```

### 5.3 New: Decomposition Bonus

Award points not just for the final answer but for the quality of the decomposition:

- **Factor count bonus**: More factors generally means better decomposition
- **Unit consistency bonus**: Units cancel correctly to the target
- **Calibration bonus**: Confidence intervals that contain the true answer
- **Precision penalty**: Claiming too many significant figures

### 5.4 Scoring Pipeline

```python
@dataclass
class ScoreReport:
    final_answer_score: float        # Olympiad or continuous
    decomposition_score: float       # Quality of factor breakdown
    calibration_score: float         # Did confidence interval contain truth?
    precision_score: float           # Appropriate significant figures?
    total: float
    feedback: list[str]              # Explanatory messages
```

---

## 6. Game Flow

### 6.1 Problem Database

Problems are stored as structured files (evolving from the current `piano.txt` format):

```yaml
# problems/piano_tuners.yaml
question: "How many piano tuners are in Chicago?"
answer: 225
answer_unit: tuners
source: "Classic Fermi problem, various sources cite 200-300"
difficulty: beginner

hints:
  - "Start with the population of Chicago"
  - "How many households have pianos?"
  - "How often does a piano need tuning?"
  - "How many pianos can one tuner service per day?"

reference_decomposition:
  - name: population
    value: 2.7e6
    unit: people
    range: [2.5e6, 3e6]
  - name: pianos_per_person
    value: 0.02
    unit: pianos/person
    range: [0.01, 0.05]
  - name: tunings_per_year
    value: 1.5
    unit: tunings/piano/year
    range: [1, 2]
  - name: tuner_daily_capacity
    value: 4
    unit: tunings/tuner/day
    range: [3, 5]
  - name: work_days
    value: 250
    unit: days/year
    range: [240, 260]
```

### 6.2 Session Flow

```
1. Present question
2. Player enters factors using DSL syntax
3. System validates units, computes answer
4. System shows:
   - Point estimate
   - Confidence interval (best case / worst case)
   - Unit analysis (did everything cancel?)
5. Reveal actual answer
6. Score and explain
7. Show reference decomposition for comparison
```

### 6.3 Interactive Mode

Using the DSL in a REPL-like environment:

```
> Question: How many piano tuners are in Chicago?

> population = 2.7M people
  = 2,700,000 people

> pianos = 1/50 pianos/person
  = 0.02 pianos/person

> tunings = 2 tunings/piano/year
  = 2 tunings/(piano·year)

> capacity = 4 tunings/tuner/day * 250 days/year
  = 1,000 tunings/(tuner·year)

> answer = population * pianos * tunings / capacity -> tuners
  = 108 tuners
  90% CI: [25, 460] tuners (best case)
  Worst case: [11, 1080] tuners

> !score
  Actual answer: 225 tuners
  Your estimate: 108 tuners (0.32 OOM off)
  Olympiad score: 5/5 (same order of magnitude)
  Continuous score: 9.0/10
  Unit check: PASS (all units cancel correctly)
  Calibration: PASS (225 is within your 90% CI)
```

---

## 7. What to Salvage vs. Rewrite

### Keep (refactor into new structure)

- `rounding.py` — order of magnitude logic, well-tested, moves to `core/`
- `score.py` — Olympiad scoring, moves to `game/scoring.py`
- `bounds.py` `calculate_interval_product` — interval arithmetic, moves to `uncertainty/interval.py`
- `bounds.py` `fermi_error_bounds` — heuristic bounds, moves to `uncertainty/bounds.py`

### Rewrite

- `simple_dimensional.py` → full `units/` package with real dimensional analysis
- `significant_numbers.py` → cleaner `core/sigfigs.py`, fix the SigFig arithmetic rules
  (addition/subtraction should track decimal places, not sig figs)
- `inferred_moments.py` → `uncertainty/lognormal.py` with proper lognormal model
- `means.py` → delete, just use `math.sqrt(a * b)` or `exp(mean(ln(a), ln(b)))`
- `files.py` → `game/problems.py` with YAML format and proper validation
- `game.py` → `game/session.py` with DSL integration and scoring

### Delete

- `use_file.py` — superseded by proper integration
- `significant.py` — string-based sig fig counting is fragile; derive from value precision
- Dead code in `files.py` (commented-out old parser)
- `means.py` approximate geometric mean hacks (use actual geometric mean)

---

## 8. Implementation Phases

### Phase 1: Units & Quantities

Build the foundation everything else depends on.

- `units/dimension.py` — Unit class with dimension algebra
- `units/registry.py` — Built-in units (SI, imperial, time, counting nouns)
- `units/parser.py` — Parse "meters/second^2" into Unit objects
- `core/quantity.py` — Quantity = value + unit, with arithmetic
- Tests for all of the above

### Phase 2: Estimates & Uncertainty

Add the statistical layer.

- `core/estimate.py` — Estimate = quantity + lognormal uncertainty
- `uncertainty/lognormal.py` — Propagation through products
- `uncertainty/interval.py` — Worst-case interval arithmetic
- `uncertainty/bounds.py` — Heuristic error bounds
- `core/chain.py` — EstimateChain that composes everything
- Tests

### Phase 3: The DSL

Make it usable by non-programmers.

- `dsl/lexer.py` — Tokenizer
- `dsl/parser.py` — Parser producing AST
- `dsl/evaluator.py` — Walk AST, produce Estimates
- Error messages with source locations
- Tests

### Phase 4: Scoring & Game

The fun part.

- `game/scoring.py` — Olympiad + continuous + decomposition scoring
- `game/problems.py` — YAML problem loader, problem database
- `game/session.py` — Interactive game session
- `__main__.py` — CLI entry point
- Problem files (start with 10-20 classic Fermi problems)

### Phase 5: Polish

- `formatting/` — Pretty display, engineering notation
- `__init__.py` — Clean public API
- Documentation
- Package metadata updates

---

## 9. Dependencies

### Remove

- `engineering_notation` — we'll handle notation formatting ourselves

### Keep

- `scipy` — but only for `scipy.stats.norm.ppf`. Consider vendoring just the ppf
  calculation (it's a well-known formula) to avoid the heavy scipy dependency.
  Alternatively, use a lightweight stats library.

### Add

- `pyyaml` — for problem file format (or use TOML via stdlib `tomllib` in 3.11+)
- No other new runtime dependencies. Keep it lean.

### Consider

- `pint` — established Python units library. Could use as the units backend instead of
  building our own. **Trade-off**: pint is powerful but heavy and its API is designed for
  physics, not Fermi counting-noun units. Our unit system is simpler and more
  Fermi-specific. **Recommendation**: build our own, but study pint's dimension algebra
  for inspiration.

---

## 10. Open Questions

1. **Normal vs. Lognormal for ranges?** The current `inferred_moments.py` assumes normal.
   For Fermi problems, lognormal is more appropriate (positive quantities, multiplicative
   composition). The redesign assumes lognormal throughout.
   **Decision needed**: Should we support both and let the user choose?

2. **Tolerance for unknown units?** When the DSL encounters "widgets" for the first time,
   should it auto-register a new counting dimension, warn, or error?
   **Recommendation**: Auto-register with an informational message.

3. **YAML vs. TOML for problem files?** TOML is in the stdlib (3.11+), YAML is more
   expressive and familiar. Given the target is Python 3.14, TOML is dependency-free.
   **Recommendation**: Use TOML.

4. **How much precision to track?** Sig figs rules for addition vs. multiplication are
   different and somewhat contentious. For Fermi estimation specifically, where everything
   is multiplicative, tracking sig figs through products (min of operand sig figs) may be
   sufficient. Do we need full addition/subtraction sig fig rules?
   **Recommendation**: Start with multiplication-only rules. Fermi estimates are products.

5. **Web/API interface?** Is the game console-only, or should we design for a web frontend
   from the start? This affects whether the core returns structured data or formatted
   strings.
   **Recommendation**: Core returns structured data (`ScoreReport`, `Estimate`). The CLI
   is one presentation layer. A web API can be added later without changing the core.
