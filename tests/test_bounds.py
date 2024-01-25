import fermi_problems.bounds as bounds


def test_fermi_error_bounds():
    steps = 9
    lower_bound, upper_bound = bounds.fermi_error_bounds(steps, accuracy=2, std_dev=2)
    assert lower_bound == 0.125
    assert upper_bound == 8


def test_interval_bounds_worst_case():
    # Example usage:
    range_estimates = [(2, 5), (10, 20), (1, 2)]
    lowest, highest = bounds.calculate_interval_product(range_estimates)
    print(f"The lowest possible product is {lowest}, and the highest possible product is {highest}.")
    assert lowest == 20
    assert highest == 200
