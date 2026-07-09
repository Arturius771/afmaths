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
    newtons_raphson_method,
    power_rule_string,
    ratio,
    reduce,
    square,
    square_root,
    subtract,
    termial,
)


class OperatioTestMethods(unittest.TestCase):
    def test_add(self):
        result = add(5)(6)

        self.assertEqual(result, 11)

    def test_subtract(self):
        result = subtract(10)(21)

        self.assertEqual(result, 11)

    def test_multiply(self):
        result = multiply(556)(2)

        self.assertEqual(result, 1112)

        result = multiply(10)(2)

        self.assertEqual(result, 20)

    def test_multiply_by_repeated_addition(self):
        result = multiply_by_repeated_addition(556)(2)

        self.assertEqual(result, 1112)

        result = multiply_by_repeated_addition(10)(2)

        self.assertEqual(result, 20)

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

    def test_ratio(self):
        result = ratio(5)(10)

        self.assertEqual(result, 0.5)

    def test_newtons_raphson_method(self):
        result = newtons_raphson_method(60, subtract(5)(4), 3)

        self.assertEqual(result, 60.333333333333336)

    def test_reduce(self):
        result = reduce(lambda a, b: subtract(b)(a))([1, 2, 3, 5, 6])

        self.assertEqual(result, -15)

    def test_power_rule_string(self):
        self.assertEqual(power_rule_string(55, 5), "f'(55^{5}) = 5 * 55^{4}")


if __name__ == "__main__":
    unittest.main()
