from decimal import Decimal, ROUND_HALF_UP
from typing import List

class SigFig:
    EXACT_DIGITS = float('inf')  # Represents an infinite number of significant digits

    def __init__(self, number: float, digits: int):
        self.number = number
        self.digits = digits
        self.value = self.round_to_sigfigs(Decimal(number), self.digits)

    def round_to_sigfigs(self, num: Decimal, sig_figs: int) -> Decimal:
        if sig_figs is SigFig.EXACT_DIGITS:
            return num  # No rounding for exact numbers
        if num != 0:
            return round(num, -int(num.log10()) + (sig_figs - 1))
        return Decimal(0)  # Can't take log(0)

    def __add__(self, other: 'SigFig') -> 'SigFig':
        result = self.value + other.value
        min_digits = min(self.digits, other.digits)
        return SigFig(float(result), min_digits)

    def __sub__(self, other: 'SigFig') -> 'SigFig':
        result = self.value - other.value
        min_digits = min(self.digits, other.digits)
        return SigFig(float(result), min_digits)

    def __mul__(self, other: 'SigFig') -> 'SigFig':
        result = self.value * other.value
        min_digits = min(self.digits, other.digits)
        return SigFig(float(result), min_digits)

    def __truediv__(self, other: 'SigFig') -> 'SigFig':
        result = self.value / other.value
        min_digits = min(self.digits, other.digits)
        return SigFig(float(result), min_digits)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SigFig):
            return NotImplemented
        return (self.value == other.value) and (self.digits == other.digits)

    def __repr__(self) -> str:
        return f"SigFig({self.value}, {self.digits})"



def sum_sigfigs(numbers: List[SigFig]) -> SigFig:
    if not numbers:
        return SigFig(0.0, 0)

    # Sum the values without rounding
    total_value = sum(number.value for number in numbers)

    # Find the minimum digits among all instances
    min_digits = min(number.digits for number in numbers)

    # Create a new SigFig instance with the total value and the minimum digits
    return SigFig(float(total_value), min_digits)

def product_sigfigs(numbers: List[SigFig]) -> SigFig:
    if not numbers:
        return SigFig(1.0, 0)

    # Multiply the values without rounding
    total_value = 1
    for number in numbers:
        total_value *= number.value

    # Find the minimum digits among all instances
    min_digits = min(number.digits for number in numbers)

    # Create a new SigFig instance with the total value and the minimum digits
    return SigFig(float(total_value), min_digits)

class DeferredExpression:
    def __init__(self):
        self.stack = []

    def add_operand(self, operand: SigFig):
        self.stack.append(operand)

    def add_operation(self, operation: str):
        self.stack.append(operation)

    def evaluate(self):
        # Evaluate the expression respecting the order of operations
        # This is a simplified version; a full implementation would need to handle parentheses and the full set of arithmetic rules
        while len(self.stack) > 1:
            left_operand = self.stack.pop(0)
            operation = self.stack.pop(0)
            right_operand = self.stack.pop(0)

            if operation in ('*', '/'):
                result = left_operand * right_operand if operation == '*' else left_operand / right_operand
            elif operation in ('+', '-'):
                # Defer rounding for addition/subtraction
                result = left_operand + right_operand if operation == '+' else left_operand - right_operand
                # Keep track of the operands' significant digits for final rounding

            self.stack.insert(0, result)

        # Final result is on the stack
        final_result = self.stack[0]

        # Apply final rounding to the result based on the collected significant digits information
        # ...

        return final_result

if __name__ == '__main__':

    # Usage
    expr = DeferredExpression()
    expr.add_operand(SigFig(1.234, 3))
    expr.add_operation('*')
    expr.add_operand(SigFig(2.345, 3))
    expr.add_operation('+')
    expr.add_operand(SigFig(3.456, 3))
    result = expr.evaluate()
    print(result)

if __name__ == '__main__':
    # So if the measured values of 22.35 and 47.773 are added, the limiting value of 22.35
    # has two decimal places, which means that the result of the addition will have only two decimal places
    # https://www.britannica.com/science/significant-figures
    a = SigFig(22.35, 4)
    b = SigFig(47.773, 5)
    print(a + b)
    assert a + b == SigFig(70.12, 4)

    # So if the measured values of 2.445 and 31.7 are being multiplied, the resulting value will have three
    # significant figures, since 2.445 has four significant figures, but 31.7 has only three significant figures.
    a = SigFig(2.445, 4)
    b = SigFig(31.7, 3)
    print(a * b)
    assert a * b == SigFig(77.5, 3)

    numbers = [SigFig(1.234, 3), SigFig(2.345, 3), SigFig(3.456, 3)]
    result = product_sigfigs(numbers)
    print(result)