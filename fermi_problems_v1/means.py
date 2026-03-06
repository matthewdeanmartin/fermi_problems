"""
But why? We got computers so we can do the actual geometric mean.
"""

import math


def scientific_notation(number):
    if number > 0:
        exponent = math.floor(math.log10(number))
        coefficient = number / (10**exponent)
        return coefficient, exponent
    raise ValueError("Number must be positive.")


def approximate_geometric_mean(lower_bound, upper_bound):
    # Convert numbers to scientific notation
    coeff1, exp1 = scientific_notation(lower_bound)
    coeff2, exp2 = scientific_notation(upper_bound)

    # Average the coefficients and exponents
    avg_coefficient = (coeff1 + coeff2) / 2
    avg_exponent = (exp1 + exp2) / 2

    # Check if the average exponent is not an integer
    if avg_exponent % 1 != 0:
        # Round the exponent down and multiply the final result by three
        avg_exponent = math.floor(avg_exponent)
        final_multiplier = 3
    else:
        final_multiplier = 1

    # Construct the AGM using the averaged coefficient and exponent
    agm = final_multiplier * avg_coefficient * (10**avg_exponent)
    return agm


def approximate_geometric_mean_v2(lower_bound, upper_bound):
    # Convert numbers to scientific notation
    coeff1, exp1 = scientific_notation(lower_bound)
    coeff2, exp2 = scientific_notation(upper_bound)

    # Average the coefficients and exponents
    avg_coefficient = (coeff1 + coeff2) / 2
    avg_exponent = (exp1 + exp2) / 2

    # Construct the AGM using the averaged coefficient and exponent
    agm = avg_coefficient * (10**avg_exponent)
    return agm


if __name__ == "__main__":

    def run() -> None:
        # Example usage:
        lower_bound = 20
        upper_bound = 400
        agm = approximate_geometric_mean(lower_bound, upper_bound)
        print(f"The approximate geometric mean of {lower_bound} and {upper_bound} is {agm:.2f}.")

        # Example usage:
        lower_bound = 2
        upper_bound = 400
        agm = approximate_geometric_mean_v2(lower_bound, upper_bound)
        print(f"The approximate geometric mean of {lower_bound} and {upper_bound} is {agm:.2f}.")

    run()
