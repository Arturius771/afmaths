import unittest

from afmaths.constants import Force, Mass
from afmaths.physics.space.celestial_mechanics import (
    orbit_centripetal_force,
    orbit_state_vector_prediction,
    orbital_elements_from_state_vectors,
)
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Degrees,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVector,
    TrueAnomaly,
    Velocity,
    VelocityVector,
)

from afmaths.physics.space.type_conversion_helpers import degrees_to_radians


class CelestialMechanicsTestMethods(unittest.TestCase):

    def test_orbit_elements_from_state_vectors(self):
        result = orbital_elements_from_state_vectors(
            StateVector(
                PositionVector(
                    Position(Scalar(10000)),
                    Position(Scalar(40000)),
                    Position(Scalar(-5000)),
                ),
                VelocityVector(
                    Velocity(Scalar(-1.5)),
                    Velocity(Scalar(1)),
                    Velocity(Scalar(-0.1)),
                ),
            )
        )
        self.assertAlmostEqual(result.inclination, 0.12166217595729033, places=10)

        self.assertAlmostEqual(
            result.right_ascension_of_ascending_node, 3.024483909022929, places=10
        )

        self.assertAlmostEqual(
            result.argument_of_periapsis, 1.5978995641224425, places=6
        )

        self.assertAlmostEqual(result.semi_major_axis, 25015.186690979368, places=1)

        self.assertAlmostEqual(result.eccentricity, 0.7079768603248032, places=6)

        self.assertAlmostEqual(result.true_anomaly, 2.987554518980773, places=6)

    def test_orbit_state_vector_prediction(self):
        result = orbit_state_vector_prediction(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPeriapsis(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1800)),
        )
        self.assertAlmostEqual(
            result.position.x,
            -1753.131769017119,
            places=2,
        )
        self.assertAlmostEqual(
            result.position.y,
            1070.9950241554125,
            places=1,
        )
        self.assertAlmostEqual(
            result.position.z,
            -6564.0676605044755,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.x,
            -3.478980009547892,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.y,
            6.473396036204375,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.z,
            1.986162313733967,
            places=2,
        )

        result = orbit_state_vector_prediction(
            orbital_elements_from_state_vectors(
                StateVector(
                    PositionVector(
                        Position(Scalar(10000)),
                        Position(Scalar(40000)),
                        Position(Scalar(-5000)),
                    ),
                    VelocityVector(
                        Velocity(Scalar(-1.5)),
                        Velocity(Scalar(1)),
                        Velocity(Scalar(-0.1)),
                    ),
                )
            )
        )
        self.assertAlmostEqual(
            result.position.x,
            10000.000000000027,
            places=2,
        )
        self.assertAlmostEqual(
            result.position.y,
            39999.999999999985,
            places=1,
        )
        self.assertAlmostEqual(
            result.position.z,
            -5000.0,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.x,
            -1.4999999999999996,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.y,
            1.0000000000000016,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.z,
            -0.1000000000000002,
            places=2,
        )

    def test_orbit_centripetal_force(self):
        self.assertEqual(
            orbit_centripetal_force(
                Velocity(Scalar(2)),
                Distance(Scalar(4)),
                Mass(Scalar(10)),
            ),
            Force(Scalar(10)),
        )

        self.assertEqual(
            orbit_centripetal_force(
                Velocity(Scalar(20)),
                Distance(Scalar(4124)),
                Mass(Scalar(11.4)),
            ),
            Force(Scalar(1.1057225994180406)),
        )


if __name__ == "__main__":
    unittest.main()
