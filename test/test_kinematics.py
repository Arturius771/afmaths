import unittest

from afmaths.physics.kinematics import (
    detect_collision,
    propagate_vector,
    velocity_after_duration,
    velocity_time_average_acceleration_from_slope,
    velocity_time_curve_displacement,
    velocity_time_displacement_curve_section,
    velocity_time_displacement_flat,
)
from astronomy_types import (
    Acceleration,
    Coordinate2D,
    Scalar,
    Second,
    Vector2D,
    Velocity,
)


class KinematicsTestMethods(unittest.TestCase):

    def assert_scalar_almost_equal(
        self,
        actual,
        expected: float,
        places: int = 7,
    ):
        self.assertAlmostEqual(float(actual), expected, places=places)

    def test_velocity_time_displacement_curve_section_plus_flat_section(self):
        displacement = velocity_time_displacement_curve_section(
            Coordinate2D(3, 6),
            Coordinate2D(7, 0),
        ) + velocity_time_displacement_flat(
            Coordinate2D(0, 6),
            Coordinate2D(3, 6),
        )

        self.assert_scalar_almost_equal(displacement, 30)

    def test_velocity_time_average_acceleration_from_slope(self):
        self.assert_scalar_almost_equal(
            velocity_time_average_acceleration_from_slope(
                Coordinate2D(0, 3),
                Coordinate2D(6, 0),
            ),
            -0.5,
        )

    def test_velocity_time_displacement_curve_section_negative_area(self):
        self.assert_scalar_almost_equal(
            velocity_time_displacement_curve_section(
                Coordinate2D(2, 0),
                Coordinate2D(3, -5),
            ),
            -2.5,
        )

    def test_velocity_time_displacement_curve_section_flat_then_negative_area(self):
        displacement = velocity_time_displacement_curve_section(
            Coordinate2D(0, 0),
            Coordinate2D(2, 0),
        ) + velocity_time_displacement_curve_section(
            Coordinate2D(2, 0),
            Coordinate2D(3, -5),
        )

        self.assert_scalar_almost_equal(displacement, -2.5)

    def test_velocity_time_curve_displacement(self):
        self.assert_scalar_almost_equal(
            velocity_time_curve_displacement(
                [
                    Coordinate2D(1, 5),
                    Coordinate2D(0.5, 2.5),
                    Coordinate2D(1.5, 2.5),
                ]
            ),
            3.75,
        )

    def test_velocity_time_displacement_curve_section_plus_flat_section_from_non_zero_time(
        self,
    ):
        displacement = velocity_time_displacement_curve_section(
            Coordinate2D(1, 0),
            Coordinate2D(3, 4),
        ) + velocity_time_displacement_flat(
            Coordinate2D(3, 4),
            Coordinate2D(4, 4),
        )

        self.assert_scalar_almost_equal(displacement, 8)

    def test_velocity_after_duration(self):
        self.assertEqual(
            velocity_after_duration(
                Acceleration(Scalar(1)),
                Velocity(Scalar(0)),
                Second(Scalar(5)),
            ),
            Velocity(Scalar(5)),
        )

    def test_propagate_vector(self):
        self.assertEqual(
            propagate_vector(
                Coordinate2D(0, 0),
                Vector2D(1, 1),
                2,
            )[-1],
            Coordinate2D(2, 2),
        )

    def test_detect_collision(self):
        self.assertTrue(
            detect_collision(
                Coordinate2D(0, 0),
                Coordinate2D(2, 0),
                Vector2D(1, 0),
                Vector2D(-1, 0),
            )
        )


if __name__ == "__main__":
    unittest.main()
