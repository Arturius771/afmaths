import math


def add(num1: float):
    return lambda num2: num1 + num2


def subtract(num2: float):
    return lambda num1: num1 - num2


def multiply(num1: float):
    return lambda num2: num1 * num2


def divide(denominator: float):
    return lambda numerator: numerator / denominator


def exponentiate(exponent: float):
    return lambda num: num**exponent


def square_root(num: float):
    return math.sqrt(num)  # TODO: use herons_method()


def square():
    """Squares a number"""
    return exponentiate(2)


# def ratio(num1): return  lambda num2: divide(num1)(num2) # TODO: provide as {numerator and denominator object?}


def half():
    return divide(2)


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


def dot_product_3d(vector_a: list[float], vector_b: list[float]) -> float:
    """Returns the dot product of two vectors"""
    a = multiply(vector_a[0])(vector_b[0])
    b = multiply(vector_a[1])(vector_b[1])
    c = multiply(vector_a[2])(vector_b[2])

    return add(a)(add(b)(c))


# TODO: check naming
def vector_magnitude_3d(vector: list[float]) -> float:
    """Returns the magnitude of a vector"""
    return square_root(
        add(SQUARE(vector[0]))(add(SQUARE(vector[1]))(SQUARE(vector[2])))
    )


def vector_multiplication_3d(vector: list[float], scalar: float) -> list[float]:
    scalar_multiply = multiply(scalar)
    i = scalar_multiply(vector[0])
    j = scalar_multiply(vector[1])
    k = scalar_multiply(vector[2])

    return [i, j, k]


def vector_cross_multiplication_3d(
    vector_a: list[float], vector_b: list[float]
) -> list[float]:
    """Returns the cross product of two 3D vectors"""
    # i = subtract(multiply(vector_a[1])(vector_b[2]))(multiply(vector_a[2])(vector_b[1]))
    # j = subtract(multiply(vector_a[2])(vector_b[0]))(multiply(vector_a[0])(vector_b[2]))
    # k = subtract(multiply(vector_a[0])(vector_b[1]))(multiply(vector_a[1])(vector_b[0]))

    # (a_{2}b_{3}-a_{3}b_{2}),(a_{3}b_{1}-a_{1}b_{3}),(a_{1}b_{2}-a_{2}b_{1})
    a = multiply(vector_a[1])(vector_b[2])
    b = multiply(vector_a[2])(vector_b[1])
    c = multiply(vector_a[2])(vector_b[0])
    d = multiply(vector_a[0])(vector_b[2])
    e = multiply(vector_a[0])(vector_b[1])
    f = multiply(vector_a[1])(vector_b[0])

    i = subtract(b)(a)
    j = subtract(d)(c)
    k = subtract(f)(e)

    return [i, j, k]
