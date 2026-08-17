import unittest

from afmaths.constants import EXAMPLE_ELEMENTS, MEAN_SOLAR_DAY, SIDEREAL_DAY
from afmaths.operation import divide_by, multiply
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    angular_velocity_from_period,
    mean_motion,
)
from afmaths.physics.space.celestial_mechanics.time import (
    orbital_period_from_mean_motion,
)
from afmaths.physics.space.engineering.astrodynamics import phase_orbit
from afmaths.physics.space.engineering.astrodynamics.orbital_directions import (
    anti_normal,
    anti_radial,
    normal,
    prograde,
    radial,
    retrograde,
)
from astronomy_types import (
    Anomaly,
    Distance,
    Position,
    PositionVector,
    Radians,
    Scalar,
    SemiMajorAxis,
    StateVector,
    TrueAnomaly,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.physics.space.engineering.astrodynamics.hohmann_transfer import (
    hohmann_is_efficient,
    hohmann_transfer_parameters,
)
from afmaths.afmath_types import OrbitalDirection
from afmaths.physics.space.engineering.astrodynamics.phase_orbit import (
    phase_orbit_parameters,
)
from afmaths.physics.space.engineering.astrodynamics.westward_drift import (
    westward_drift_from_angular_velocity_and_period,
    westward_drift_from_mean_motion,
)


class AstrodynamicsTestMethods(unittest.TestCase):

    def test_hohmann_transfer(self):

        result = hohmann_transfer_parameters(
            Distance(Scalar(300_000)), Distance(Scalar(1000000))
        )
        self.assertAlmostEqual(
            result[0][0],
            375.3885342162439,
            places=7,
        )

        self.assertAlmostEqual(
            result[0][1],
            190.0335919432273,
            places=7,
        )

        self.assertAlmostEqual(
            result[0][2],
            185.3549422730166,
            places=7,
        )

        self.assertEqual(
            result[1],
            OrbitalDirection.PROGRADE,
        )

        self.assertAlmostEqual(
            result[2],
            2931.8470683197825,
            places=7,
        )

        result = hohmann_transfer_parameters(
            Distance(Scalar(1000000)), Distance(Scalar(776000))
        )
        self.assertAlmostEqual(
            result[0][0],
            114.174793850831523,
            places=10,
        )

        self.assertAlmostEqual(
            result[0][1],
            56.8673882343528,
            places=10,
        )

        self.assertAlmostEqual(
            result[0][2],
            57.30740561647872,
            places=10,
        )

        self.assertEqual(
            result[1],
            OrbitalDirection.RETROGRADE,
        )

        self.assertAlmostEqual(
            result[2],
            3082.026424305649,
            places=10,
        )

        result = hohmann_transfer_parameters(
            Distance(Scalar(300_000)), Distance(Scalar(35_786_000))
        )
        self.assertAlmostEqual(
            result[0][0],
            3892.5565137899894,
            places=7,
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

    def test_westward_drift(self):
        n = mean_motion(SemiMajorAxis(Distance(Scalar(7000))))
        orbital_period = orbital_period_from_mean_motion(n)
        mean_solar_day_angular_velocity = angular_velocity_from_period(MEAN_SOLAR_DAY)

        self.assertAlmostEqual(
            westward_drift_from_angular_velocity_and_period(
                orbital_period=orbital_period,
                body_angular_velocity=mean_solar_day_angular_velocity,
            ),
            westward_drift_from_mean_motion(n, mean_solar_day_angular_velocity),
            places=4,
        )

        mean_solar_day_angular_velocity = angular_velocity_from_period(SIDEREAL_DAY)

        self.assertAlmostEqual(
            westward_drift_from_angular_velocity_and_period(
                orbital_period=orbital_period,
                body_angular_velocity=mean_solar_day_angular_velocity,
            ),
            westward_drift_from_mean_motion(n, mean_solar_day_angular_velocity),
            places=4,
        )

        self.assertAlmostEqual(
            westward_drift_from_angular_velocity_and_period(
                orbital_period=orbital_period,
            ),
            westward_drift_from_mean_motion(n),
            places=4,
        )

    def test_phase_orbit_parameters(self):

        delta_v, total_delta_v, phase_orbit = phase_orbit_parameters(
            EXAMPLE_ELEMENTS, EXAMPLE_ELEMENTS.true_anomaly
        )

        self.assertAlmostEqual(delta_v, 0.000000000000000, places=7)
        self.assertAlmostEqual(total_delta_v, 0.000000000000000, places=7)
        self.assertAlmostEqual(phase_orbit.semi_major_axis, 384447999.9999996, places=7)

        delta_v, total_delta_v, phase_orbit = phase_orbit_parameters(
            EXAMPLE_ELEMENTS, TrueAnomaly(Anomaly(Radians(Scalar(5.0))))
        )

        self.assertAlmostEqual(delta_v, 25.62612052468353, places=7)
        self.assertAlmostEqual(total_delta_v, 51.25224104936706, places=7)
        self.assertAlmostEqual(phase_orbit.semi_major_axis, 374513611.4854905, places=7)
        self.assertAlmostEqual(
            phase_orbit.eccentricity,
            0.590095,
            places=5,
        )
        self.assertEqual(phase_orbit.inclination, EXAMPLE_ELEMENTS.inclination)
        self.assertEqual(
            phase_orbit.right_ascension_of_ascending_node,
            EXAMPLE_ELEMENTS.right_ascension_of_ascending_node,
        )
        self.assertEqual(
            phase_orbit.argument_of_periapsis,
            EXAMPLE_ELEMENTS.argument_of_periapsis,
        )
        self.assertEqual(
            phase_orbit.true_anomaly,
            EXAMPLE_ELEMENTS.true_anomaly,
        )

    def test_hohmann_is_efficient(self):
        self.assertTrue(
            hohmann_is_efficient(
                Distance(Scalar(16378137)), Distance(Scalar(16378137 * 2))
            )
        )

        self.assertTrue(
            hohmann_is_efficient(
                Distance(Scalar(16378137)), Distance(Scalar(16378137 * 11.97))
            )
        )

        self.assertFalse(
            hohmann_is_efficient(
                Distance(Scalar(16378137)), Distance(Scalar(16378137 * 11.99))
            )
        )

        self.assertFalse(
            hohmann_is_efficient(
                Distance(Scalar(16378137)), Distance(Scalar(256378137))
            )
        )


if __name__ == "__main__":
    unittest.main()
