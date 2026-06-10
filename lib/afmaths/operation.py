import math
from typing import Callable
from astronomy_types import Ratio


def add(num1: float):
    return lambda num2: num1 + num2


def subtract(value: float):
    return lambda from_value: from_value - value


def multiply(num1: float):
    return lambda num2: num1 * num2


def divide_by(denominator: float):
    return lambda numerator: numerator / denominator


def exponentiate(exponent: float):
    return lambda num: num**exponent


def square_root(num: float):
    return math.sqrt(num)  # TODO: use herons_method()


def square():
    """Squares a number"""
    return exponentiate(2)


def negate(value: float):
    return -value


# def ratio(num1): return  lambda num2: divide(num1)(num2) # TODO: provide as {numerator and denominator object?}


def half():
    return divide_by(2)


SQUARE = square()
CUBE = exponentiate(3)
HALF = half()


def factorial(number: int) -> int:
    """
    Calculates the factorial of a number.
    """
    working_string = ""
    result = 1

    for i in range(number, 0, -1):
        result: int = multiply(result)(i)
        working_string = f"{working_string} {i} x"

    working_string = f"{number}! = {working_string[:-1]} = {result}"

    return result


def termial(number: int) -> int:
    """
    Calculates the termial of a number (sum of all positive integers up to that number).
    """

    return HALF(multiply(number)(add(number)(1)))


def interval(start: float, end: float, n: int) -> list[float]:
    """Creates n evenly spaced points between a and b."""
    if n < 2:
        return [start]
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]


# Apply a function of two arguments cumulatively to the items of an iterable, from left to right.

# This effectively reduces the iterable to a single value. If initial is present,
# it is placed before the items of the iterable in the calculation, and serves as
# a default when the iterable is empty.


def reduce(
    reduce_function,
):
    """Returns a function that applies a reduction function to a list of values."""

    def reduction(sequence: list[float]) -> float:
        # For example, reduce(lambda x, y: x+y, [1, 2, 3, 4, 5])
        # calculates ((((1 + 2) + 3) + 4) + 5).
        final_value = sequence.pop(0)
        for item in sequence:
            final_value = reduce_function(final_value, item)
        return final_value

    return reduction


def ratio(num1: float):
    """Returns a function that calculates the ratio of num1 to num2."""
    return lambda num2: Ratio(divide_by(num2)(num1))


def summation(
    sum_rule: Callable[[int], float],
    start_index: int,
    stop_index: int,
) -> float:
    """Function that takes a rule, and then iteratively adds according to that rule."""
    total = 0.0

    for val in range(start_index, stop_index + 1):
        total += sum_rule(val)

    return total


def product(
    product_function: Callable[[int], float],
    start_index: int,
    stop_index: int,
) -> float:
    total = 1.0

    for val in range(start_index, stop_index + 1):
        total *= product_function(val)

    return total


def newtons_raphson_method(
    first_term: float, function: float, derivative: float
) -> float:
    # E_i - (E_i - e * np.sin(E_i) - M) / (1 - e * np.cos(E_i))
    # E_i - (E_i - eccentricity * math.sin(E_i) - mean_anomaly)
    # M = E - e * np.sin(E)
    return subtract(divide_by(derivative)(function))(first_term)


if __name__ == "__main__":
    print(reduce(lambda a, b: subtract(b)(a))([1, 2, 3, 5, 6]))
