"""UnitRegistry — maps unit name strings to their canonical dimensions and scale factors."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UnitDef:
    """Definition of a named unit."""

    dimensions: dict[str, int]
    scale: float  # relative to SI base unit for that dimension
    canonical_name: str  # for display


class UnknownUnitError(Exception):
    """Raised when a unit name is not found in the registry."""


class UnitRegistry:
    """Mutable registry of known unit names."""

    def __init__(self):
        """Initialize with built-in units."""
        self._registry: dict[str, UnitDef] = {}
        self._canonical_to_names: dict[str, list[str]] = {}
        self._register_builtins()

    def _add(self, name: str, unit_def: UnitDef) -> None:
        self._registry[name.lower()] = unit_def
        canonical = unit_def.canonical_name
        if canonical not in self._canonical_to_names:
            self._canonical_to_names[canonical] = []
        if name not in self._canonical_to_names[canonical]:
            self._canonical_to_names[canonical].append(name)

    def _register_builtins(self) -> None:
        # ── Length (base: meters = 1.0) ──────────────────────────────────────
        _L = {"length": 1}
        for name in ("m", "meter", "meters"):
            self._add(name, UnitDef(_L, 1.0, "meters"))
        for name in ("km", "kilometer", "kilometers"):
            self._add(name, UnitDef(_L, 1000.0, "kilometers"))
        for name in ("cm", "centimeter", "centimeters"):
            self._add(name, UnitDef(_L, 0.01, "centimeters"))
        for name in ("mm", "millimeter", "millimeters"):
            self._add(name, UnitDef(_L, 0.001, "millimeters"))
        for name in ("ft", "foot", "feet"):
            self._add(name, UnitDef(_L, 0.3048, "feet"))
        for name in ("in", "inch", "inches"):
            self._add(name, UnitDef(_L, 0.0254, "inches"))
        for name in ("mi", "mile", "miles"):
            self._add(name, UnitDef(_L, 1609.344, "miles"))
        for name in ("yd", "yard", "yards"):
            self._add(name, UnitDef(_L, 0.9144, "yards"))

        # ── Time (base: seconds = 1.0) ────────────────────────────────────────
        _T = {"time": 1}
        for name in ("s", "sec", "second", "seconds"):
            self._add(name, UnitDef(_T, 1.0, "seconds"))
        for name in ("ms", "millisecond", "milliseconds"):
            self._add(name, UnitDef(_T, 0.001, "milliseconds"))
        for name in ("min", "minute", "minutes"):
            self._add(name, UnitDef(_T, 60.0, "minutes"))
        for name in ("hr", "hour", "hours"):
            self._add(name, UnitDef(_T, 3600.0, "hours"))
        for name in ("day", "days"):
            self._add(name, UnitDef(_T, 86400.0, "days"))
        for name in ("week", "weeks"):
            self._add(name, UnitDef(_T, 604800.0, "weeks"))
        for name in ("month", "months"):
            self._add(name, UnitDef(_T, 2628000.0, "months"))  # ~30.4375 days
        for name in ("year", "years", "yr", "yrs"):
            self._add(name, UnitDef(_T, 31557600.0, "years"))  # Julian year

        # ── Mass (base: kilograms = 1.0) ──────────────────────────────────────
        _M = {"mass": 1}
        for name in ("kg", "kilogram", "kilograms"):
            self._add(name, UnitDef(_M, 1.0, "kilograms"))
        for name in ("g", "gram", "grams"):
            self._add(name, UnitDef(_M, 0.001, "grams"))
        for name in ("mg", "milligram", "milligrams"):
            self._add(name, UnitDef(_M, 1e-6, "milligrams"))
        for name in ("lb", "lbs", "pound", "pounds"):
            self._add(name, UnitDef(_M, 0.453592, "pounds"))
        for name in ("oz", "ounce", "ounces"):
            self._add(name, UnitDef(_M, 0.0283495, "ounces"))
        for name in ("ton", "tons"):
            self._add(name, UnitDef(_M, 907.185, "tons"))  # US short ton
        for name in ("tonne", "tonnes"):
            self._add(name, UnitDef(_M, 1000.0, "tonnes"))  # metric tonne

        # ── Area (base: square meters = 1.0) ─────────────────────────────────
        _A = {"length": 2}
        for name in ("acre", "acres"):
            self._add(name, UnitDef(_A, 4046.86, "acres"))
        for name in ("hectare", "hectares"):
            self._add(name, UnitDef(_A, 10000.0, "hectares"))

        # ── Volume (base: cubic meters = 1.0) ────────────────────────────────
        _V = {"length": 3}
        for name in ("liter", "liters"):
            self._add(name, UnitDef(_V, 0.001, "liters"))
        for name in ("l",):
            self._add(name, UnitDef(_V, 0.001, "liters"))
        for name in ("ml", "milliliter", "milliliters"):
            self._add(name, UnitDef(_V, 1e-6, "milliliters"))
        for name in ("gallon", "gallons", "gal"):
            self._add(name, UnitDef(_V, 0.00378541, "gallons"))

        # ── Currency (base: dollars = 1.0) ───────────────────────────────────
        _C = {"currency": 1}
        for name in ("dollar", "dollars", "usd"):
            self._add(name, UnitDef(_C, 1.0, "dollars"))
        for name in ("euro", "euros", "eur"):
            self._add(name, UnitDef(_C, 1.08, "euros"))  # approx
        for name in ("pound_sterling", "gbp"):
            self._add(name, UnitDef(_C, 1.27, "pound_sterling"))  # approx
        for name in ("yen", "jpy"):
            self._add(name, UnitDef(_C, 0.0067, "yen"))  # approx

        # ── Energy (base: joules = 1.0) ───────────────────────────────────────
        _E = {"energy": 1}
        for name in ("joule", "joules", "j"):
            self._add(name, UnitDef(_E, 1.0, "joules"))
        for name in ("kj", "kilojoule", "kilojoules"):
            self._add(name, UnitDef(_E, 1000.0, "kilojoules"))
        for name in ("calorie", "calories", "cal"):
            self._add(name, UnitDef(_E, 4.184, "calories"))
        for name in ("kcal",):
            self._add(name, UnitDef(_E, 4184.0, "kcal"))
        for name in ("kwh", "kilowatt_hour"):
            self._add(name, UnitDef(_E, 3600000.0, "kWh"))
        for name in ("btu",):
            self._add(name, UnitDef(_E, 1055.06, "BTU"))

        # ── Power (base: watts = 1.0) ─────────────────────────────────────────
        _P = {"power": 1}
        for name in ("watt", "watts", "w"):
            self._add(name, UnitDef(_P, 1.0, "watts"))
        for name in ("kw", "kilowatt", "kilowatts"):
            self._add(name, UnitDef(_P, 1000.0, "kilowatts"))
        for name in ("mw", "megawatt", "megawatts"):
            self._add(name, UnitDef(_P, 1e6, "megawatts"))
        for name in ("hp", "horsepower"):
            self._add(name, UnitDef(_P, 745.7, "horsepower"))

        # ── Speed: mph, kph (derived: length/time) ────────────────────────────
        _S = {"length": 1, "time": -1}
        self._add("mph", UnitDef(_S, 1609.344 / 3600.0, "mph"))
        self._add("kph", UnitDef(_S, 1000.0 / 3600.0, "kph"))

        # ── Counting units ─────────────────────────────────────────────────────
        for name in ("person", "people"):
            self._add(name, UnitDef({"people": 1}, 1.0, "people"))
        for name in ("piano", "pianos"):
            self._add(name, UnitDef({"pianos": 1}, 1.0, "pianos"))
        for name in ("tuner", "tuners"):
            self._add(name, UnitDef({"tuners": 1}, 1.0, "tuners"))
        for name in ("tuning", "tunings"):
            self._add(name, UnitDef({"tunings": 1}, 1.0, "tunings"))

    def lookup(self, name: str) -> UnitDef:
        """Look up a unit name. Raises UnknownUnitError if not found."""
        key = name.strip().lower()
        if key not in self._registry:
            raise UnknownUnitError(f"Unknown unit: {name!r}")
        return self._registry[key]

    def register(self, name: str, unit_def: UnitDef) -> None:
        """Register a new unit name."""
        self._add(name, unit_def)

    def auto_register_counting_unit(self, name: str) -> UnitDef:
        """Register an unknown name as a new counting dimension.

        'widgets' -> UnitDef(dimensions={'widgets': 1}, scale=1.0)
        Returns the new UnitDef.
        """
        unit_def = UnitDef({name: 1}, 1.0, name)
        self._add(name, unit_def)
        return unit_def

    def aliases(self, canonical_name: str) -> list[str]:
        """Return all registered names for a given canonical name."""
        return list(self._canonical_to_names.get(canonical_name, []))


_default_registry: UnitRegistry | None = None


def default_registry() -> UnitRegistry:
    """Return the module-level default registry (singleton)."""
    global _default_registry
    if _default_registry is None:
        _default_registry = UnitRegistry()
    return _default_registry
