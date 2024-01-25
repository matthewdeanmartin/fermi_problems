"""

If min/max estimate are the 5% and 95% bounds, then what was the mean, std dev, and variance?

Best case, errors cancel out.
"""

from scipy.stats import norm


def calculate_statistics(P5, P95):
    # Calculate the mean
    mean = (P5 + P95) / 2

    # Z-score for the 95th percentile
    Z_95th = norm.ppf(0.95)

    # Calculate standard deviation using the Z-score
    std_dev = (P95 - mean) / Z_95th

    # Calculate variance
    variance = std_dev**2

    return mean, std_dev, variance


# TODO: take range of each product, calculate the meant/std dev of each (as implied)
# then https://math.stackexchange.com/a/4382059/408
# which gives us the range of the final answer.

if __name__ == "__main__":
    print(calculate_statistics(5000, 25000))
