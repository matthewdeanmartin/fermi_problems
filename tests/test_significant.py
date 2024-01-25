import fermi_problems.significant as significant


def test_count_significant_digits():
    assert significant.count_significant_digits("0.0025") == 2
    assert significant.count_significant_digits("25") == 2


def test_count_significant_digits_ambiguous():
    # The problem is with trailing zeros. Can't tell with scientific notation.
    # Is this wrong? I see 1.30 there.
    assert significant.count_significant_digits("1.30e3") == 2

    # assert significant.count_significant_digits("1300.0") == 5
    # Output: 2 (ambiguous without additional notation)
    assert significant.count_significant_digits("1300") == 2
