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
                    Position(Scalar(10000000)),
                    Position(Scalar(40000000)),
                    Position(Scalar(-5000000)),
                ),
                VelocityVector(
                    Velocity(Scalar(-1500)),
                    Velocity(Scalar(1000)),
                    Velocity(Scalar(-100)),
                ),
            )
        )
        self.assertAlmostEqual(
            result.argument_of_periapsis,
            1.597899323919624,
            places=6,
        )

        self.assertAlmostEqual(
            result.semi_major_axis,
            25_015_181.01846454,
            places=1,
        )

        self.assertAlmostEqual(
            result.eccentricity,
            0.7079771708731989,
            places=6,
        )

        self.assertAlmostEqual(
            result.true_anomaly,
            2.9875547591835923,
            places=6,
        )

    def test_orbit_state_vector_prediction(self):
        result = state_vector_at_time(
            OrbitalElements(
                Inclination(radians_from_degrees(Degrees(Scalar(98.371)))),
                RightAscension(radians_from_degrees(Degrees(Scalar(120.534)))),
                ArgumentOfPeriapsis(radians_from_degrees(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878100))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1800)),
        )
        self.assertAlmostEqual(
            result.position.x,
            -1_753_135.2394416651,
            places=2,
        )
        self.assertAlmostEqual(
            result.position.y,
            1_071_001.4816334906,
            places=2,
        )
        self.assertAlmostEqual(
            result.position.z,
            -6_564_065.679221897,
            places=2,
        )

        self.assertAlmostEqual(
            result.velocity.x,
            -3_478.9797952214476,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.y,
            6_473.398314925645,
            places=2,
        )
        self.assertAlmostEqual(
            result.velocity.z,
            1_986.1714357769285,
            places=2,
        )

        result = state_vector_at_time(
            orbital_elements_from_state_vectors(
                StateVector(
                    PositionVector(
                        Position(Scalar(10000000)),
                        Position(Scalar(40000000)),
                        Position(Scalar(-5000000)),
                    ),
                    VelocityVector(
                        Velocity(Scalar(-1500)),
                        Velocity(Scalar(1000)),
                        Velocity(Scalar(-100)),
                    ),
                )
            )
        )
        self.assertAlmostEqual(result.position.x, 10_000_000, places=2)
        self.assertAlmostEqual(result.position.y, 40_000_000, places=1)
        self.assertAlmostEqual(result.position.z, -5_000_000, places=2)

        self.assertAlmostEqual(result.velocity.x, -1_500, places=2)
        self.assertAlmostEqual(result.velocity.y, 1_000, places=2)
        self.assertAlmostEqual(result.velocity.z, -100, places=2)

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
