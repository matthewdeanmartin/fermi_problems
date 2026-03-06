import math


def calculate_olympiad_score(user_estimate: float, actual_answer: float):
    """
    Calculate the Olympiad score for a user's estimate of a quantity.
    Args:
        user_estimate: The user's estimate of the quantity.
        actual_answer: The actual answer to the quantity.

    Returns:
        The Olympiad score for the user's estimate.

    Examples:
        >>> calculate_olympiad_score(50000, 200000)
        3
    """
    # Calculate the order of magnitude for the user's estimate and the actual answer
    user_order = math.floor(math.log10(user_estimate))
    actual_order = math.floor(math.log10(actual_answer))

    # Calculate the difference in the order of magnitude
    order_difference = abs(user_order - actual_order)

    # Assign points based on the difference in the order of magnitude
    if order_difference == 0:
        return 5  # Correct power of ten
    if order_difference == 1:
        return 3  # One away from the correct power of ten
    if order_difference == 2:
        return 1  # Two away from the correct power of ten
    return 0  # More than two away from the correct power of ten


if __name__ == "__main__":

    def run() -> None:
        # Example usage:
        user_estimate = 50000
        actual_answer = 200000
        score = calculate_olympiad_score(user_estimate, actual_answer)
        print(f"Your Olympiad score is: {score}")

    run()
