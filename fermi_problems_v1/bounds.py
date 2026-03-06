import math


def scientific_notation(number):
    if number > 0:
        exponent = math.floor(math.log10(number))
        coefficient = number / (10**exponent)
        return coefficient, exponent
    raise ValueError("Number must be positive.")


def fermi_error_bounds(steps, accuracy=2, std_dev=2):
    """
    Given number of products and some parameters of the distribution of errors,
    calculate bounds.
    """
    # Calculate the standard error growth factor
    # In logarithmic terms, the standard deviation would compound in quadrature (square root of sum of squares)
    std_error_growth_factor = math.sqrt(steps)

    # Calculate the multiplicative factor for the error bounds
    # This uses the fact that the errors compound exponentially
    error_factor = accuracy**std_error_growth_factor

    # The bounds are from 1/error_factor to error_factor times the correct value
    lower_bound = 1 / error_factor
    upper_bound = error_factor

    return lower_bound, upper_bound


def calculate_interval_product(ranges):
    # Initialize the product interval with the first range
    product_interval = ranges[0]

    # Iterate through the remaining ranges and update the product interval
    for lower, upper in ranges[1:]:
        # Calculate the extremes of the product
        product_min = min(
            product_interval[0] * lower,
            product_interval[0] * upper,
            product_interval[1] * lower,
            product_interval[1] * upper,
        )
        product_max = max(
            product_interval[0] * lower,
            product_interval[0] * upper,
            product_interval[1] * lower,
            product_interval[1] * upper,
        )

        # Update the product interval
        product_interval = (product_min, product_max)

    return product_interval


if __name__ == "__main__":

    def run() -> None:
        """# Example usage:"""
        steps = 9
        lower_bound, upper_bound = fermi_error_bounds(steps)
        print(
            f"After {steps} steps, expect to be within {lower_bound:.2f} to {upper_bound:.2f} times the correct value."
        )

        # Example usage:
        range_estimates = [(2, 5), (10, 20), (1, 2)]
        lowest, highest = calculate_interval_product(range_estimates)
        print(f"The lowest possible product is {lowest}, and the highest possible product is {highest}.")
