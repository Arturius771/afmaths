import unittest

from afmaths.physics.space.engineering.astrodynamics.orbital_directions import (
    anti_normal,
    anti_radial,
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

from afmaths.physics.space.engineering.astrodynamics.hohmann_transfer import (
    hohmann_transfer_parameters,
)
from afmaths.types import OrbitalDirection


class AstrodynamicsTestMethods(unittest.TestCase):

    def test_hohmann_transfer(self):

        result = hohmann_transfer_parameters(
            Distance(Scalar(300)), Distance(Scalar(1000))
        )
        self.assertAlmostEqual(
            result[0][0],
            0.37539955175032447,
            places=7,
        )

        self.assertAlmostEqual(
            result[0][1],
            0.19003921507073027,
            places=7,
        )

        self.assertAlmostEqual(
            result[0][2],
            0.18536033667959417,
            places=7,
        )

        self.assertEqual(
            result[1],
            OrbitalDirection.PROGRADE,
        )

        self.assertAlmostEqual(
            result[2],
            2931.7613426663966,
            places=7,
        )

        result = hohmann_transfer_parameters(
            Distance(Scalar(1000)), Distance(Scalar(776))
        )
        self.assertAlmostEqual(
            result[0][0],
            0.11417802338823702,
            places=10,
        )

        self.assertAlmostEqual(
            result[0][1],
            0.057309030757556556,
            places=10,
        )

        self.assertAlmostEqual(
            result[0][2],
            0.05686899263068046,
            places=10,
        )

        self.assertEqual(
            result[1],
            OrbitalDirection.RETROGRADE,
        )

        self.assertAlmostEqual(
            result[2],
            3081.939259221263,
            places=10,
        )

    def test_radial(self):
        self.assertEqual(
            radial(
                PositionVector(
                    Position(Scalar(7000)), Position(Scalar(0.1)), Position(Scalar(0.1))
                )
            )[0],
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
            )[0],
            Vector3D(
                x=-0.9999999997959184,
                y=-1.4285714282798834e-05,
                z=-1.4285714282798834e-05,
            ),
        )

    def test_prograde(self):
        result = prograde(
            VelocityVector(
                Velocity(Scalar(0.1)), Velocity(Scalar(7.5)), Velocity(Scalar(0.1))
            )
        )
        self.assertEqual(
            result[0],
            Vector3D(x=0.0133309635948745, y=0.9998222696155874, z=0.0133309635948745),
        )
        self.assertEqual(
            result[1],
            OrbitalDirection.PROGRADE,
        )

    def test_retrograde(self):
        self.assertEqual(
            retrograde(
                VelocityVector(
                    Velocity(Scalar(0.1)), Velocity(Scalar(7.5)), Velocity(Scalar(0.1))
                )
            )[0],
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
            )[0],
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
            )[0],
            Vector3D(
                x=1.4093988070694925e-05, y=0.013331960418386137, z=-0.9999111253670309
            ),
        )


if __name__ == "__main__":
    unittest.main()
