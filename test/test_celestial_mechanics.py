import math
import unittest

from afmaths.types import Force, Mass, OrbitalDirection
from afmaths.physics.space.celestial_mechanics import (
    distance_between_positions,
    eccentric_anomaly_solved,
    newtons_method_eccentric_anomaly,
    orbit_centripetal_force,
    orbital_direction_from_inclination,
    state_vector_at_time,
    orbital_elements_from_state_vectors,
)
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Degrees,
    Distance,
    Eccentricity,
    Inclination,
    MeanAnomaly,
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

from afmaths.physics.space.type_conversion_helpers import radians_from_degrees


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
        result = state_vector_at_time(
            OrbitalElements(
                Inclination(radians_from_degrees(Degrees(Scalar(98.371)))),
                RightAscension(radians_from_degrees(Degrees(Scalar(120.534)))),
                ArgumentOfPeriapsis(radians_from_degrees(Degrees(Scalar(10.598)))),
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

        result = state_vector_at_time(
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

    def test_orbital_direction_from_inclination(self):
        self.assertEqual(
            orbital_direction_from_inclination(Inclination(Radians(Scalar(0)))),
            OrbitalDirection.RADIAL,
        )
        self.assertEqual(
            orbital_direction_from_inclination(
                Inclination(Radians(Scalar(math.pi / 2)))
            ),
            OrbitalDirection.NORMAL,
        )
        self.assertEqual(
            orbital_direction_from_inclination(Inclination(Radians(Scalar(math.pi)))),
            OrbitalDirection.RADIAL,
        )
        self.assertEqual(
            orbital_direction_from_inclination(
                Inclination(Radians(Scalar(3 * math.pi / 2)))
            ),
            OrbitalDirection.NORMAL,
        )
        self.assertEqual(
            orbital_direction_from_inclination(
                Inclination(Radians(Scalar(math.pi / 4)))
            ),
            OrbitalDirection.PROGRADE,
        )
        self.assertEqual(
            orbital_direction_from_inclination(
                Inclination(Radians(Scalar(5 * math.pi / 4)))
            ),
            OrbitalDirection.RETROGRADE,
        )

    def test_distance_between_positions(self):
        self.assertAlmostEqual(
            distance_between_positions(
                PositionVector(
                    Position(Scalar(2)),
                    Position(Scalar(4)),
                    Position(Scalar(1)),
                ),
                PositionVector(
                    Position(Scalar(3)),
                    Position(Scalar(5)),
                    Position(Scalar(2)),
                ),
            ),
            Distance(Scalar(1.73)),
            places=2,
        )

        self.assertAlmostEqual(
            distance_between_positions(
                PositionVector(
                    Position(Scalar(-22)),
                    Position(Scalar(4000)),
                    Position(Scalar(132)),
                ),
                PositionVector(
                    Position(Scalar(3)),
                    Position(Scalar(-500)),
                    Position(Scalar(1800)),
                ),
            ),
            Distance(Scalar(4799.25)),
            places=1,
        )

    def test_eccentric_anomaly_solved(self):
        self.assertEqual(
            eccentric_anomaly_solved(
                newtons_method_eccentric_anomaly,
                Eccentricity(Ratio(Scalar(0.4))),
                MeanAnomaly(Anomaly(Radians(Scalar(1.3)))),
            )[0],
            1.6968274346828216,
        )

        self.assertEqual(
            eccentric_anomaly_solved(
                newtons_method_eccentric_anomaly,
                Eccentricity(Ratio(Scalar(0.8))),
                MeanAnomaly(Anomaly(Radians(Scalar(5.5)))),
            )[0],
            4.70006079291257,
        )


if __name__ == "__main__":
    unittest.main()
