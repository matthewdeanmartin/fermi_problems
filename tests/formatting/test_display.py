"""Tests for fermi_problems.formatting.display"""

import pytest
from fermi_problems.core.chain import EstimateChain
from fermi_problems.core.estimate import Estimate
from fermi_problems.formatting.display import format_chain_result, format_estimate


def test_format_chain_result_basic():
    chain = EstimateChain()
    chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
    result = chain.compute()
    s = format_chain_result(result, show_factors=False)
    assert "Estimate" in s
    assert "CI" in s or "ci" in s.lower() or "90%" in s
    assert "Unit check" in s


def test_format_chain_result_with_factors():
    chain = EstimateChain()
    chain.add_factor("population", 2.7e6, "people", low=2.5e6, high=3e6)
    result = chain.compute()
    s = format_chain_result(result, show_factors=True)
    assert "Estimate" in s


def test_format_estimate_styles():
    e = Estimate(1e6, "people")
    s_human = format_estimate(e, style="human")
    s_sci = format_estimate(e, style="scientific")
    s_eng = format_estimate(e, style="engineering")
    assert "people" in s_human
    assert "people" in s_sci
    assert "people" in s_eng
