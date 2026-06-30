import unittest

from afmaths.statistics import probability_of_outcome_percentage
from astronomy_types import Ratio, Scalar


class StatsTestMethods(unittest.TestCase):
    def test_add(self):
        result = probability_of_outcome_percentage(2, Ratio(Scalar(0.50)))

        self.assertEqual(result, 0.25)

        result = probability_of_outcome_percentage(5, Ratio(Scalar(0.10)))

        self.assertEqual(result, 1e-05)


if __name__ == "__main__":
    unittest.main()
