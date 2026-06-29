import unittest

from afmaths.geometry.geometry import calculate_distance, calculate_foci
from astronomy_types import (
    Coordinate2D,
    Distance,
    Eccentricity,
    Ratio,
    Scalar,
    SemiMajorAxis,
)


class GeometryTestMethods(unittest.TestCase):

    def test_calculate_foci(self):
        self.assertEqual(
            calculate_foci(
                SemiMajorAxis(Distance(Scalar(10))),
                Eccentricity(Ratio(Scalar(0.5))),
                Coordinate2D(10, 2),
            ),
            (Coordinate2D(5, 2), Coordinate2D(15, 2)),
        )

        self.assertEqual(
            calculate_foci(
                SemiMajorAxis(Distance(Scalar(10))),
                Eccentricity(Ratio(Scalar(0.5))),
            ),
            (Coordinate2D(-5, 0), Coordinate2D(5, 0)),
        )

    def test_calculate_distance(self):
        self.assertEqual(
            calculate_distance(
                Coordinate2D(10, 2),
                Coordinate2D(20, 2),
            ),
            Distance(Scalar(10)),
        )

        self.assertEqual(
            calculate_distance(
                Coordinate2D(10, 256),
                Coordinate2D(2000, -1256),
            ),
            Distance(Scalar(2499.248687105787)),
        )


if __name__ == "__main__":
    unittest.main()
