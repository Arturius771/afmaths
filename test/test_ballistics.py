import unittest

from afmaths.physics.ballistics import (
    ballistic_vacuum_angle_to_target,
    ballistic_vacuum_displacement_at_time,
    ballistic_vacuum_initial_velocity,
    basllistic_vacuum_time_to_target,
)
from astronomy_types import Coordinate2D, Degrees, Scalar, Velocity, Second


class BallisticsTestMethods(unittest.TestCase):

    def test_ballistic_initial_velocity(self):
        result = ballistic_vacuum_initial_velocity(
            target_coordinates=Coordinate2D(100, 0),
            launch_angle=Degrees(Scalar(45)),
        )
        self.assertEqual(result, Velocity(Scalar(31.315571206669695)))

    def test_ballistic_displacement_at_time(self):
        result = ballistic_vacuum_displacement_at_time(
            initial_velocity=Velocity(Scalar(5)),
            launch_angle=Degrees(Scalar(45)),
            time=Second(Scalar(1)),
        )
        self.assertEqual(
            result, Coordinate2D(x=3.5355339059327378, y=-1.3677910940672624)
        )

    def test_ballistic_vacuum_angle_to_target(self):
        result = ballistic_vacuum_angle_to_target(
            target_coordinates=Coordinate2D(100, 0),
            initial_velocity=Velocity(Scalar(31.315571206669695)),
        )

        self.assertAlmostEqual(result[0], Degrees(Scalar(45)), places=2)
        self.assertAlmostEqual(result[1], Degrees(Scalar(45)), places=2)

    def test_basllistic_vacuum_time_to_target(self):
        result = basllistic_vacuum_time_to_target(
            target_coordinates=Coordinate2D(100, 0),
            initial_velocity=Velocity(Scalar(31.315571206669695)),
            launch_angle=Degrees(Scalar(45)),
        )
        self.assertAlmostEqual(result, Second(Scalar(4.516007557517875)))


if __name__ == "__main__":
    unittest.main()
