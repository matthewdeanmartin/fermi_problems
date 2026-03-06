# fermi_problems project memory

## Project structure
- `fermi_problems/` — new package (v2), being implemented per IMPLEMENT_CORE_LIBRARY.md
- `fermi_problems_v1/` — old package (renamed via git), kept for reference
- `tests/` — old tests (test_bounds.py etc) reference `fermi_problems.X` which no longer
  has those modules; new tests are in subdirectories tests/units/, tests/core/ etc.

## Key files
- `IMPLEMENT_CORE_LIBRARY.md` — full work order for the rebuild
- `DESIGN.md` — architectural design doc
- `pyproject.toml` — project config, Python 3.14+, uv for package management

## Architecture (v2)
- `fermi_problems/units/` — Unit, UnitDef, UnitRegistry, parse_unit
- `fermi_problems/core/` — Quantity, Estimate, EstimateChain, sigfigs, magnitude
- `fermi_problems/uncertainty/` — lognormal, interval arithmetic, error bounds
- `fermi_problems/formatting/` — notation, display

## Implementation status (as of 2026-03-02)
All tasks P1 through 7.2 complete. 118 tests pass.
Tasks 8.1 (remove old modules), 8.2 (update pyproject.toml), 8.3 (verify) pending.

## Key design decisions
- Estimates store SI-base values internally; display scale separate
- Lognormal uncertainty: log_mean + log_std in ln-space
- No scipy: uses Abramowitz & Stegun rational approx for normal_ppf
- Unit system: immutable Unit class with sorted tuple of (dim, exp) pairs

## Workflow
- Use `uv run pytest` to run tests
- GitBash on Windows; use forward slashes
