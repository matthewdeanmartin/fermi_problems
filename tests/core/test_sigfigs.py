"""Tests for fermi_problems.core.sigfigs"""

import pytest
from fermi_problems.core.sigfigs import infer_sig_figs, round_to_sig_figs, format_sig_figs


def test_infer_sig_figs_scientific_notation():
    assert infer_sig_figs(1e6) == 1
    assert infer_sig_figs(1.5e6) == 2
    assert infer_sig_figs(1.23e6) == 3


def test_infer_sig_figs_integer():
    assert infer_sig_figs(100.0) == 1  # 1e2, trailing zeros not significant
    assert infer_sig_figs(250.0) == 2


def test_infer_sig_figs_decimal():
    assert infer_sig_figs(0.01) == 1
    assert infer_sig_figs(0.015) == 2


def test_round_to_sig_figs():
    assert round_to_sig_figs(12345, 3) == pytest.approx(12300)
    assert round_to_sig_figs(0.00456, 2) == pytest.approx(0.0046)
    assert round_to_sig_figs(1e6, 1) == pytest.approx(1e6)
    assert round_to_sig_figs(1.567e6, 3) == pytest.approx(1.57e6)


def test_format_sig_figs_large():
    s = format_sig_figs(12345, 3)
    assert s == "1.23e+04"


def test_format_sig_figs_small():
    s = format_sig_figs(0.00456, 2)
    assert s == "4.6e-03"


def test_format_sig_figs_normal():
    s = format_sig_figs(42.0, 2)
    assert s == "42"
