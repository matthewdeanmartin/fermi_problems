"""Tests for fermi_problems.uncertainty.bounds"""

import pytest
from fermi_problems.uncertainty.bounds import fermi_error_bounds


def test_fermi_error_bounds_9_steps():
    lower, upper = fermi_error_bounds(9, accuracy_factor=2.0)
    assert lower == pytest.approx(0.125, rel=1e-4)
    assert upper == pytest.approx(8.0, rel=1e-4)


def test_fermi_error_bounds_1_step():
    lower, upper = fermi_error_bounds(1, accuracy_factor=2.0)
    assert lower == pytest.approx(0.5, rel=1e-4)
    assert upper == pytest.approx(2.0, rel=1e-4)


def test_fermi_error_bounds_symmetry():
    lower, upper = fermi_error_bounds(5)
    assert lower * upper == pytest.approx(1.0, rel=1e-6)


def test_fermi_error_bounds_increases_with_steps():
    _, upper_1 = fermi_error_bounds(1)
    _, upper_4 = fermi_error_bounds(4)
    _, upper_9 = fermi_error_bounds(9)
    assert upper_1 < upper_4 < upper_9
