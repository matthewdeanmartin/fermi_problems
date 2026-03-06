import fermi_problems.means as means


def test_approximate_geometric_mean():
    lower_bound = 2
    upper_bound = 400
    agm = means.approximate_geometric_mean(lower_bound, upper_bound)
    assert agm == 30


def test_approximate_geometric_mean_v2():
    lower_bound = 2
    upper_bound = 400
    agm = means.approximate_geometric_mean_v2(lower_bound, upper_bound)
    assert agm == 30
