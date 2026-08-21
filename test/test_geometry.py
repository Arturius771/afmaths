import unittest

from afmaths.geometry.geometry import (
    angle_of_alpha,
    angle_of_alpha_from_a_b,
    angle_of_alpha_from_a_c,
    angle_of_alpha_from_b_c,
    angle_of_beta,
    angle_of_beta_from_a_b,
    angle_of_beta_from_a_c,
    angle_of_beta_from_b_c,
    area_of_sphere,
    calculate_distance,
    calculate_foci,
    euclidian_distance,
    euclidian_heading,
    length_of_a_side_of_right_triangle,
    length_of_b_side_of_right_triangle,
    pythagoras_theorem,
    signed_rotation_offset,
)
from astronomy_types import (
    Coordinate2D,
    Degrees,
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

    def test_area_of_sphere(self):
        self.assertEqual(
            area_of_sphere(Distance(Scalar(1737.5))),
            37936694.78750525,
        )

    def test_euclidian_distance(self):
        self.assertEqual(
            euclidian_distance(
                Coordinate2D(0, 0),
                Coordinate2D(3, 4),
            ),
            Distance(Scalar(5)),
        )

        self.assertEqual(
            euclidian_distance(
                Coordinate2D(1, 1),
                Coordinate2D(4, 5),
            ),
            calculate_distance(
                Coordinate2D(1, 1),
                Coordinate2D(4, 5),
            ),
        )

    def test_euclidian_heading(self):
        self.assertEqual(
            euclidian_heading(
                Coordinate2D(0, 0),
                Coordinate2D(1, 1),
            ),
            Degrees(Scalar(45)),
        )

        self.assertEqual(
            euclidian_heading(
                Coordinate2D(-10000, 0),
                Coordinate2D(1000, 0),
            ),
            Degrees(Scalar(90)),
        )

        self.assertEqual(
            euclidian_heading(
                Coordinate2D(0, 0),
                Coordinate2D(-1, 1),
            ),
            Degrees(Scalar(315)),
        )

        self.assertEqual(
            euclidian_heading(
                Coordinate2D(0, 0),
                Coordinate2D(-1, -1),
            ),
            Degrees(Scalar(225)),
        )

        self.assertEqual(
            euclidian_heading(
                Coordinate2D(0, 0),
                Coordinate2D(1, -1),
            ),
            Degrees(Scalar(135)),
        )

        self.assertEqual(
            euclidian_heading(
                Coordinate2D(-45, 12),
                Coordinate2D(-55, -5),
            ),
            Degrees(Scalar(210.46554491945986)),
        )

    def test_signed_rotation_offset(self):
        self.assertEqual(
            signed_rotation_offset(
                Degrees(Scalar(0)),
                euclidian_heading(
                    Coordinate2D(0, 0),
                    Coordinate2D(1, 1),
                ),
            ),
            Degrees(Scalar(45)),
        )

        self.assertEqual(
            signed_rotation_offset(
                Degrees(Scalar(190)),
                euclidian_heading(
                    Coordinate2D(0, 0),
                    Coordinate2D(10, 0),
                ),
            ),
            Degrees(Scalar(-100)),
        )

    def test_pythagoras_theorem(self):
        self.assertEqual(
            pythagoras_theorem(3)(4),
            5,
        )

        self.assertEqual(
            pythagoras_theorem(5)(12),
            13,
        )

    def test_length_of_a_side_of_right_triangle(self):
        self.assertEqual(
            length_of_a_side_of_right_triangle(4, 5),
            3,
        )

        self.assertEqual(
            length_of_a_side_of_right_triangle(12, 13),
            5,
        )

    def test_length_of_b_side_of_right_triangle(self):
        self.assertEqual(
            length_of_b_side_of_right_triangle(3, 5),
            4,
        )

        self.assertEqual(
            length_of_b_side_of_right_triangle(5, 13),
            12,
        )

    def test_angle_of_alpha(self):
        self.assertEqual(
            angle_of_alpha(Degrees(Scalar(30))),
            Degrees(Scalar(60)),
        )

        self.assertEqual(
            angle_of_alpha(Degrees(Scalar(45))),
            Degrees(Scalar(45)),
        )

    def test_angle_of_beta(self):
        self.assertEqual(
            angle_of_beta(Degrees(Scalar(60))),
            Degrees(Scalar(30)),
        )

        self.assertEqual(
            angle_of_beta(Degrees(Scalar(45))),
            Degrees(Scalar(45)),
        )

    def test_angle_of_alpha_from_a_c(self):
        self.assertAlmostEqual(
            float(angle_of_alpha_from_a_c(3, 5)),
            36.86989764584402,
        )

    def test_angle_of_alpha_from_b_c(self):
        self.assertAlmostEqual(
            float(angle_of_alpha_from_b_c(4, 5)),
            36.86989764584402,
        )

    def test_angle_of_alpha_from_a_b(self):
        self.assertAlmostEqual(
            float(angle_of_alpha_from_a_b(3, 4)),
            36.86989764584402,
        )

    def test_angle_of_beta_from_a_c(self):
        self.assertAlmostEqual(
            float(angle_of_beta_from_a_c(3, 5)),
            53.13010235415598,
        )

    def test_angle_of_beta_from_b_c(self):
        self.assertAlmostEqual(
            float(angle_of_beta_from_b_c(4, 5)),
            53.13010235415598,
        )

    def test_angle_of_beta_from_a_b(self):
        self.assertAlmostEqual(
            float(angle_of_beta_from_a_b(3, 4)),
            53.13010235415598,
        )


if __name__ == "__main__":
    unittest.main()
