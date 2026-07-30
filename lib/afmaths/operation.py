import math
from typing import Callable
from astronomy_types import Coordinate2D, Ratio

from afmaths.afmath_types import Percentage

# region Basic Operations


def add(num1: float) -> Callable:
    return lambda num2: num1 + num2


def subtract(value: float) -> Callable:
    return lambda from_value: from_value - value


def multiply(num1: float) -> Callable:
    return lambda num2: num1 * num2


def multiply_by_repeated_addition(num1: float) -> Callable:
    return lambda num2: summation(lambda _: num1, 1, num2)


def divide_by(denominator: float) -> Callable:
    return lambda numerator: numerator / denominator


def exponentiate(exponent: float) -> Callable:
    return lambda num: num**exponent


def exponentiate_by_repeated_multiplication(exponent: int) -> Callable:
    return lambda num: product(lambda _: num, 1, exponent)


def square_root(num: float) -> float:
    return math.sqrt(num)  # TODO: use herons_method()


def square() -> Callable:
    """Squares a number"""
    return exponentiate(2)


def negate(value: float) -> float:
    return -value


def absolute(value: float) -> float:
    return abs(value)


# def ratio(num1): return  lambda num2: divide(num1)(num2) # TODO: provide as {numerator and denominator object?}

# region Helpers


def half():
    return divide_by(2)


SQUARE = square()
CUBE = exponentiate(3)
HALF = half()
DOUBLE = multiply(2)


def factorial(number: int):
    """
    Calculates the factorial of a number.
    """
    working_string = ""
    result = 1

    for i in range(number, 0, -1):
        result = multiply(result)(i)
        working_string = f"{working_string} {i} x"

    working_string = f"{number}! = {working_string[:-1]} = {result}"

    return result


def termial(number: int) -> int:
    """
    Calculates the termial of a number (sum of all positive integers up to that number).
    """

    return HALF(multiply(number)(add(number)(1)))


def interval_points(
    start: float, end: float, number_of_intervals: int, step: float | None = None
) -> list[float]:
    """
    Creates a fixed number of points starting at ``start``.

    When ``step`` is not provided, ``number_of_intervals`` points are distributed
    evenly between ``start`` and ``end``, including both endpoints.

    When ``step`` is provided, exactly ``number_of_intervals`` points are created
    using that spacing. In this case, ``end`` does not limit the generated range;
    the final point is:

        start + (number_of_intervals - 1) * step

    Therefore, callers using ``step`` must calculate an appropriate
    ``number_of_intervals`` if the points should cover a specific duration.
    """

    if number_of_intervals < 2:
        return [start]
    if step is None:
        used_step = (subtract(start)(end)) / (subtract(1)(number_of_intervals))
    else:
        used_step = step

    return [start + i * used_step for i in range(number_of_intervals)]


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


def ratio(num1: float) -> Callable:
    """Returns a function that calculates the ratio of num1 to num2."""
    return lambda num2: Ratio(divide_by(num2)(num1))


def summation(
    sum_rule: Callable[[int], float],
    start_index: int,
    stop_index: int,
) -> float:
    """Function that takes a rule, and then iteratively adds according to that rule."""
    total = 0.0

    for val in range(round(start_index), round(stop_index + 1)):
        total = add(sum_rule(val))(total)

    return total


def product(
    product_function: Callable[[int], float],
    start_index: int,
    stop_index: int,
) -> float:
    """Function that takes a rule, and then iteratively multiplies according to that rule."""
    total = 1.0

    for val in range(round(start_index), round(stop_index + 1)):
        total = multiply_by_repeated_addition(product_function(val))(total)

    return total


def percentage_from_ratio(ratio: Ratio) -> Percentage:
    """Converts a ratio to a percentage."""
    return multiply(100)(ratio)


def sigmoid(input: float, bias: float = 0) -> float:
    """Calculates the sigmoid of a value"""
    # TM358 Section Block 1 section 5
    return divide_by(add(1)(exponentiate(add(bias)(-input))(math.e)))(1)


# region Formula


def taylor_series(value):
    """Calculates the Taylor series of a value"""

    # Written for sin and cos functions so may not be generic for pure Taylor Series functions.
    def steps(
        initial_value_in_series, increment=1, initial_denmoninator=1, steps=3, sign=-1
    ):
        taylor = [initial_value_in_series]
        for _ in range(steps):
            exponent = exponentiate(initial_denmoninator)
            division = divide_by(factorial(initial_denmoninator))
            taylor.append(division(exponent(value)))
            initial_denmoninator += increment

        for index in range(len(taylor)):
            sign = -1 if sign == +1 else +1
            taylor[index] = taylor[index] * sign

        # from functools import reduce
        return reduce(lambda a, b: a + b)(taylor)

    return steps


def herons_method(value: float):
    """
    O(log precision) method for calculating square roots. The square roots of two values (eg. 25, 2982186) will be calculated in the same number of cycles to the same precision
    """
    # www.youtube.com/watch?v=l2TCgS_eLwA
    initial_estimate = value / 2
    current_step = initial_estimate
    epsilon = value * exponentiate(-9)(10)

    while True:
        next_step = 1 / 2 * (current_step + (value / current_step))
        if next_step < epsilon:
            break
        current_step = next_step

    return current_step


def trapezoidal_rule(curve: list[Coordinate2D]) -> float:
    """Calculates the area under a curve using the trapezoidal rule."""
    if len(curve) < 2:
        return 0.0

    curve = sorted(curve, key=lambda point: point.x)

    def trap(n: int) -> float:
        left = curve[n]  # x_k, f(x_k)
        right = curve[n + 1]  # x_{k+1}, f(x_{k+1})

        width = right.x - left.x  # x_{k+1} - x_k

        average_height = (left.y + right.y) / 2
        # (f(x_k) + f(x_{k+1})) / 2

        return multiply(width)(average_height)

    return summation(trap, 0, len(curve) - 2)


def power_rule_string(symbol: float, exponent: float) -> str:
    """Returns a string representation of the power rule for differentiation."""
    return f"f'({symbol}^{{{exponent}}}) = {exponent} * {symbol}^{{{exponent - 1}}}"


def is_divisible(num: int, factor: int) -> bool:

    if num == 0:
        raise ValueError("Cannot divide by zero")

    return num % factor == 0


def newtons_raphson_method(
    current_estimate: float,
    auxiliary_function: float,
    derivative_value: float,
) -> float:
    """x_1=x_0-(f(x_0)/f'(x_0))

    The function value either equals 0, in which case we have solved the equation, or it gives the vertical error.

    The provided derivative value, the tangent of the function value, tells us the horizontal error when it is used to divide the function value, as a correction.

    We subtract the division from the current estimate to get the next guess to iterate for. In other words, we apply the correction to our current guess.

    This is used in iterative methods to find roots of equations, such as finding the eccentric anomaly in orbital mechanics.

    This is named for Sir Isaac Newton and Joseph Raphson, who independently developed the method in the 17th century.
    """

    correction = divide_by(derivative_value)(auxiliary_function)

    return subtract(correction)(current_estimate)
