from math import factorial
import unittest

from afmaths.operation import (
    absolute,
    add,
    divide_by,
    exponentiate,
    exponentiate_by_repeated_multiplication,
    interval,
    multiply,
    multiply_by_repeated_addition,
    negate,
    square,
    square_root,
    subtract,
    termial,
)


class CoordinateTestMethods(unittest.TestCase):
    def test_add(self):
        result = add(5)(6)

        self.assertEqual(result, 11)

    def test_subtract(self):
        result = subtract(10)(21)

        self.assertEqual(result, 11)

    def test_multiply(self):
        result = multiply(556)(2)

        self.assertEqual(result, 1112)

    def test_multiply_by_repeated_addition(self):
        result = multiply_by_repeated_addition(556)(2)

        self.assertEqual(result, 1112)

    def test_divide(self):
        result = divide_by(7)(41)

        self.assertEqual(result, 5.857142857142857)

    def test_exponentiate(self):
        result = exponentiate(8)(10)

        self.assertEqual(result, 100_000_000)

    def test_exponentiate_by_repeated_multiplication(self):
        result = exponentiate_by_repeated_multiplication(7)(10)

        self.assertEqual(result, 10000000)

    def test_square_root(self):
        result = square_root(8)

        self.assertEqual(result, 2.8284271247461903)

    def test_square(self):
        result = square()(8)

        self.assertEqual(result, 64)

    def test_negate(self):
        result = negate(12)

        self.assertEqual(result, -12)

    def test_absolute(self):
        result = absolute(-5.4)

        self.assertEqual(result, 5.4)

    def test_factorial(self):
        result = factorial(8)

        self.assertEqual(result, 40320)

    def test_termial(self):
        result = termial(100)

        self.assertEqual(result, 5050.0)

    def test_interval(self):
        result = interval(0, 10, 5)

        self.assertEqual(result, [0.0, 2.5, 5.0, 7.5, 10.0])


if __name__ == "__main__":
    unittest.main()
