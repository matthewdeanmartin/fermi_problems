import math


def nearest_order_of_magnitude(number):
    if number > 0:
        log10_of_number = math.log10(number)
        nearest_order = round(log10_of_number)
        return nearest_order
    raise ValueError("Number must be positive.")


def order_of_magnitude_range(number):
    """
    Rounding can be viewed as a range. It is the range of all numbers that would round to that number.
    """
    nearest_order = nearest_order_of_magnitude(number)

    # Lower bound is 10^nearest_order
    lower_bound = 10**nearest_order

    # Upper bound is 10^(nearest_order + 1)
    upper_bound = 10 ** (nearest_order + 1)

    # If the number is closer to the lower bound, adjust the range
    if number < math.sqrt(lower_bound * upper_bound):
        upper_bound = lower_bound
        lower_bound = 10 ** (nearest_order - 1)

    return lower_bound, upper_bound


def order_of_magnitude(number):
    if number > 0:
        # Express the number in scientific notation: N = a * 10^b
        b = math.floor(math.log10(number))
        a = number / (10**b)

        # Adjust b if a is outside the range [1/sqrt(10), sqrt(10)]
        if a < 1 / math.sqrt(10):
            a *= 10
            b -= 1
        elif a >= math.sqrt(10):
            a /= 10
            b += 1

        # b is the order of magnitude
        return b
    raise ValueError("Number must be positive.")


if __name__ == "__main__":

    def run() -> None:
        """# Example usage:"""
        numbers = [4e6, 1.7e8, 3.7e8]
        for number in numbers:
            nearest_order = nearest_order_of_magnitude(number)
            print(f"The nearest order of magnitude for {number} is 10^{nearest_order}.")

        # Example usage:
        numbers = [4e6, 1.7e8, 3.7e8]
        for number in numbers:
            order = order_of_magnitude(number)
            print(f"The order of magnitude for {number} is {order}.")

        print("--------------")
        numbers = [0.2, 1, 5, 6, 31, 32, 999, 1000]
        for number in numbers:
            order = order_of_magnitude(number)
            print(f"The order of magnitude for {number} is {order}.")

    run()
