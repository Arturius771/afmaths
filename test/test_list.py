import unittest

from afmaths.list import (
    list_length,
    list_max,
    list_mean,
    list_median,
    list_min,
    list_range,
    list_sort,
    list_sum,
    quartiles,
)
from afmaths.statistics import probability_of_outcome_percentage


class ListTestMethods(unittest.TestCase):

    def test_list(self):

        number_list = [53.0, 2, 3, 4.0, 6]

        result = list_sort(number_list)
        self.assertEqual(result, [2, 3, 4, 6, 53])
        result = list_length(number_list)
        self.assertEqual(result, 5)
        result = list_sum(number_list)
        self.assertEqual(result, 68.0)
        result = list_min(number_list)
        self.assertEqual(result, 2)
        result = list_max(number_list)
        self.assertEqual(result, 53)
        result = list_range(number_list)
        self.assertEqual(result, 51)
        result = list_mean(number_list)
        self.assertEqual(result, 13.6)
        result = list_median(number_list)
        self.assertEqual(result, 4)
        result = quartiles(number_list)
        self.assertEqual(result, (3, 4, 1))


if __name__ == "__main__":
    unittest.main()
