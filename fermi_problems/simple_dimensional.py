from typing import List, Tuple
from collections import Counter


def simplify_units(ratios: List[str]) -> str:
    """
    Simplify a sequence of unit ratios to a single ratio.

    Args:
        ratios: A list of strings representing unit ratios, e.g., ["feet/year", "year/month", "month/day"].

    Returns:
        A string representing the simplified unit ratio.
    """
    # Parse the ratios into numerators and denominators
    numerators, denominators = [], []
    for ratio in ratios:
        numerator, denominator = ratio.split('/')
        numerators.append(numerator)
        denominators.append(denominator)

    # Count the occurrences of each unit
    numerator_counter = Counter(numerators)
    denominator_counter = Counter(denominators)

    # Cancel out units that appear in both numerator and denominator
    for unit in set(numerators + denominators):
        count = min(numerator_counter[unit], denominator_counter[unit])
        numerator_counter[unit] -= count
        denominator_counter[unit] -= count

    # Construct the result
    final_numerator = '*'.join(unit for unit, count in numerator_counter.items() for _ in range(count))
    final_denominator = '*'.join(unit for unit, count in denominator_counter.items() for _ in range(count))

    return f"{final_numerator}/{final_denominator}" if final_denominator else final_numerator


# Usage example
def test_simplify_units():
    ratios = ["feet/year", "year/month", "month/day"]
    simplified_unit = simplify_units(ratios)
    assert simplified_unit == "feet/day", f"Expected 'feet/day', but got {simplified_unit}"


test_simplify_units()
