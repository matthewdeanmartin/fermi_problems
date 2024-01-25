import fermi_problems.score as score


def test_score():
    # Example usage:
    user_estimate = 50000
    actual_answer = 200000
    the_score = score.calculate_olympiad_score(user_estimate, actual_answer)
    assert the_score == 3
