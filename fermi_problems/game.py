import math


# Step 1: Game Introduction and Instructions
def display_intro():
    print("Welcome to the Fermi Estimation Game!")
    print("You will be asked to enter factors in scientific notation (e.g., 3.2e5 for 3.2 x 10^5).")
    print("After entering a factor, you will be prompted to enter its units.")
    print("Enter nothing and press 'Enter' when you are done entering factors.")
    print("Let's start!\n")


# Step 2: User Input for Factors and Units
def get_factors_and_units():
    factors = []
    units = []
    i = 1
    while True:
        factor_input = input(f"Enter {ordinal(i)} factor (or enter to stop entering factors): ")
        if factor_input == "":
            break
        try:
            factor = float(factor_input)
            factors.append(factor)
            unit = input(f"Enter {ordinal(i)} factor units: ")
            units.append(unit)
            i += 1
        except ValueError:
            print("Invalid input. Please enter the factor in scientific notation (e.g., 3.2e5).")
    return factors, units


# Helper function to get ordinal representation (1st, 2nd, 3rd, etc.)
def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(math.floor(n / 10) % 10 != 1) * (n % 10 < 4) * n % 10 :: 4])


# Step 3: Calculation of Product
def calculate_product(factors):
    product = math.prod(factors)
    return product


# Step 4: Displaying Results
def display_results(product, units):
    unit_str = " * ".join(units) if units else ""
    print(f"\nOkay, that works out to: {product:.2e} {unit_str}")


# Main game loop
def main():
    display_intro()
    factors, units = get_factors_and_units()
    if factors:  # Proceed only if there's at least one factor
        product = calculate_product(factors)
        display_results(product, units)
    else:
        print("No factors entered. Exiting the game.")


if __name__ == "__main__":
    main()
