import unittest

from afmaths.constants import EXAMPLE_ELEMENTS
from afmaths.physics.space.engineering.thermal_subsystem import beta_angle
from astronomy_types import EquatorialCoordinates, Radians, Scalar


class ThermalSubsystemTestMethods(unittest.TestCase):

    def test_beta_angle(self):
        self.assertAlmostEqual(
            beta_angle(
                EquatorialCoordinates(Radians(Scalar(12)), Radians(Scalar(12))),
                EXAMPLE_ELEMENTS,
            ),
            -0.5663706143591729,
            places=1,
        )


if __name__ == "__main__":
    unittest.main()
