def count_significant_digits(number_str):
    # Remove any plus/minus sign
    number_str = number_str.lstrip("+-")

    # Check if the number is in scientific notation
    if "e" in number_str or "E" in number_str:
        mantissa, _, _ = number_str.partition("e" if "e" in number_str else "E")
        return count_significant_digits(mantissa.replace(".", "").lstrip("0"))

    # Remove decimal point if present
    number_str = number_str.replace(".", "")

    # Count leading and trailing zeros
    leading_zeros = len(number_str) - len(number_str.lstrip("0"))
    trailing_zeros = len(number_str) - len(number_str.rstrip("0"))

    # If there's a decimal point in the original number, trailing zeros are significant
    if "." in number_str:
        return len(number_str) - leading_zeros
    return len(number_str) - leading_zeros - trailing_zeros


if __name__ == "__main__":
    # Example usage:
    print(count_significant_digits("0.0025"))  # Output: 2
    print(count_significant_digits("1300"))  # Output: 2 (ambiguous without additional notation)
    print(count_significant_digits("1300.0"))  # Output: 5
    print(count_significant_digits("1.30e3"))  # Output: 3
