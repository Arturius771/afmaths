import unittest

from afmaths.physics.space.engineering.astrodynamics import (
    anti_normal,
    anti_radial,
    hohmann_transfer,
    normal,
    prograde,
    radial,
    retrograde,
)
from astronomy_types import (
    Distance,
    Position,
    PositionVector,
    Scalar,
    StateVector,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.types import BurnDirection


class AstrodynamicsTestMethods(unittest.TestCase):

    def test_hohmann_transfer(self):

        result = hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000)))
        self.assertAlmostEqual(
            result[0],
            0.37539955175032447,
            places=10,
        )

        self.assertAlmostEqual(
            result[1],
            0.19003921507073027,
            places=10,
        )

        self.assertAlmostEqual(
            result[2],
            0.18536033667959417,
            places=10,
        )

        self.assertEqual(
            result[3],
            BurnDirection.PROGRADE,
        )

        self.assertAlmostEqual(
            result[4],
            2931.7611286318975,
            places=10,
        )

        result = hohmann_transfer(Distance(Scalar(1000)), Distance(Scalar(776)))
        self.assertAlmostEqual(
            result[0],
            0.11417803172385366,
            places=10,
        )

        self.assertAlmostEqual(
            result[1],
            0.057309034941426695,
            places=10,
        )

        self.assertAlmostEqual(
            result[2],
            0.05686899678242696,
            places=10,
        )

        self.assertEqual(
            result[3],
            BurnDirection.RETROGRADE,
        )

        self.assertAlmostEqual(
            result[4],
            3081.939034222961,
            places=10,
        )

    def test_radial(self):
        self.assertEqual(
            radial(
                PositionVector(
                    Position(Scalar(7000)), Position(Scalar(0.1)), Position(Scalar(0.1))
                )
            ),
            Vector3D(
                x=0.9999999997959184, y=1.4285714282798834e-05, z=1.4285714282798834e-05
            ),
        )

    def test_anti_radial(self):
        self.assertEqual(
            anti_radial(
                PositionVector(
                    Position(Scalar(7000)), Position(Scalar(0.1)), Position(Scalar(0.1))
                )
            ),
            Vector3D(
                x=-0.9999999997959184,
                y=-1.4285714282798834e-05,
                z=-1.4285714282798834e-05,
            ),
        )

    def test_prograde(self):
        self.assertEqual(
            prograde(
                VelocityVector(
                    Velocity(Scalar(0.1)), Velocity(Scalar(7.5)), Velocity(Scalar(0.1))
                )
            ),
            Vector3D(x=0.0133309635948745, y=0.9998222696155874, z=0.0133309635948745),
        )

    def test_retrograde(self):
        self.assertEqual(
            retrograde(
                VelocityVector(
                    Velocity(Scalar(0.1)), Velocity(Scalar(7.5)), Velocity(Scalar(0.1))
                )
            ),
            Vector3D(
                x=-0.0133309635948745, y=-0.9998222696155874, z=-0.0133309635948745
            ),
        )

    def test_normal(self):
        self.assertEqual(
            normal(
                StateVector(
                    PositionVector(
                        Position(Scalar(7000)),
                        Position(Scalar(0.1)),
                        Position(Scalar(0.1)),
                    ),
                    VelocityVector(
                        Velocity(Scalar(0.1)),
                        Velocity(Scalar(7.5)),
                        Velocity(Scalar(0.1)),
                    ),
                )
            ),
            Vector3D(
                x=-1.4093988070694925e-05, y=-0.013331960418386137, z=0.9999111253670309
            ),
        )

    def test_anti_normal(self):
        self.assertEqual(
            anti_normal(
                StateVector(
                    PositionVector(
                        Position(Scalar(7000)),
                        Position(Scalar(0.1)),
                        Position(Scalar(0.1)),
                    ),
                    VelocityVector(
                        Velocity(Scalar(0.1)),
                        Velocity(Scalar(7.5)),
                        Velocity(Scalar(0.1)),
                    ),
                )
            ),
            Vector3D(
                x=1.4093988070694925e-05, y=0.013331960418386137, z=-0.9999111253670309
            ),
        )


if __name__ == "__main__":
    unittest.main()
