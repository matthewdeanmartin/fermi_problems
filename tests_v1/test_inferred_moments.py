import fermi_problems.inferred_moments as inferred_moments


def test_get_standard_dev_from_range():
    assert inferred_moments.calculate_statistics(5000, 25000) == (15000.0, 6079.568319117691, 36961150.946819514)
