import math
from afmaths.operation import (
    SQUARE,
    add,
    divide,
    exponentiate,
    multiply,
    factorial,
    reduce,
    summation,
)

from astronomy_types import Coordinate2D


def sigmoid(input: float, bias: float = 0) -> float:
    """Calculates the sigmoid of a value"""
    # TM358 Section Block 1 section 5
    return divide(add(1)(exponentiate(add(bias)(-input))(math.e)))(1)


def inverse_square_law(source_strength: float, distance_metres: float) -> float:
    """Calculates the inverse square law"""
    ##TM255 block 1
    four_times_pi = multiply(4)(math.pi)
    denominator = multiply(SQUARE(distance_metres))(four_times_pi)
    return divide(denominator)(source_strength)


def taylor_series(value):
    """Calculates the Taylor series of a value"""

    # Written for sin and cos functions so may not be generic for pure Taylor Series functions.
    def steps(
        initial_value_in_series, increment=1, initial_denmoninator=1, steps=3, sign=-1
    ):
        taylor = [initial_value_in_series]
        for _ in range(steps):
            exponent = exponentiate(initial_denmoninator)
            division = divide(factorial(initial_denmoninator))
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


# def trapezoidal_rule(start: Coordinate2D, end: Coordinate2D) -> float:
#     """
#     Area under a straight-line velocity-time segment.
#     """

#     return Displacement(
#         Scalar(multiply((start.y + end.y) / 2)(subtract(start.x)(end.x)))
#     )
