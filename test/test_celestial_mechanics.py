import math
import unittest

from afmaths.afmath_types import AngularMomentum, Force, Mass, OrbitalDirection
from afmaths.constants import (
    ASTRONOMICAL_UNIT,
    EARTH_MASS,
    EARTH_MU,
    EXAMPLE_ELEMENTS,
    SUN_MASS,
    SUN_MU,
)
from afmaths.numerical_analysis import root_solver
from afmaths.operation import add, multiply, multiply, subtract
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    apoapsis_radius,
    distance_between_positions,
    orbit_gravitational_force,
    orbital_direction_from_inclination,
    periapsis_radius,
    swept_area_of_ellipse,
    vis_viva,
)
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Degrees,
    Distance,
    EccentricAnomaly,
    Eccentricity,
    GravitationalParameter,
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
    SemiLatusRectum,
    SemiMajorAxis,
    StateVector,
    TrueAnomaly,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.physics.space.celestial_mechanics.gravitation import (
    lagrange_points,
    planetary_sphere_of_influence_approximation,
    solve_for_equilibrium,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    eccentric_anomaly_from_true_anomaly,
    eccentric_anomaly_solved,
    newtons_method_eccentric_anomaly,
    orbital_elements_from_state_vectors,
)

from afmaths.physics.space.celestial_mechanics.state_vector import state_vector_at_time
from afmaths.physics.space.celestial_mechanics.time import (
    rate_of_change_true_anomaly,
    time_to_eccentric_anomaly,
    time_to_true_anomaly,
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

    def test_vis_viva(self):
        self.assertAlmostEqual(
            vis_viva(
                SUN_MU,
                periapsis_radius(
                    SemiMajorAxis(Distance(Scalar(149_597_870_700))),
                    Eccentricity(Ratio(Scalar(0.0167))),
                ),
                SemiMajorAxis(Distance(Scalar(149_597_870_700))),
            ),
            30286.31975564289,
            places=3,
        )

        self.assertAlmostEqual(
            vis_viva(
                SUN_MU,
                apoapsis_radius(
                    SemiMajorAxis(Distance(Scalar(149_597_870_700))),
                    Eccentricity(Ratio(Scalar(0.0167))),
                ),
                SemiMajorAxis(Distance(Scalar(149_597_870_700))),
            ),
            29291.37229834135,
            places=3,
        )

    def test_swept_area_of_ellipse(self):
        self.assertAlmostEqual(
            swept_area_of_ellipse(
                AngularMomentum(Vector3D(Scalar(1), Scalar(0), Scalar(0))),
                Second(Scalar(0)),
            ),
            0.0,
            places=20,
        )

        self.assertAlmostEqual(
            swept_area_of_ellipse(
                AngularMomentum(Vector3D(Scalar(1), Scalar(0), Scalar(0))),
                Second(Scalar(5000)),
            ),
            2500,
            places=20,
        )

    def test_rate_of_change_true_anomaly(self):
        self.assertAlmostEqual(
            rate_of_change_true_anomaly(
                SemiLatusRectum(Distance(Scalar(10000))),
                GravitationalParameter(Scalar(398600.4418)),
                Distance(Scalar(5000)),
            ),
            0.0025253924583715694,
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
            orbit_gravitational_force(
                Velocity(Scalar(2)),
                Distance(Scalar(4)),
                Mass(Scalar(10)),
            ),
            Force(Scalar(10)),
        )

        self.assertEqual(
            orbit_gravitational_force(
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

        solution_a = eccentric_anomaly_solved(
            newtons_method_eccentric_anomaly,
            Eccentricity(Ratio(Scalar(0.72))),
            MeanAnomaly(Anomaly(Radians(Scalar(0.8726646)))),
        )

        self.assertEqual(
            solution_a[0],
            1.5924951053340866,
        )

        self.assertEqual(
            len(solution_a[1]),
            6,
        )

        def example_fixed_point_function(
            E_i_guess: EccentricAnomaly, e: Eccentricity, M: MeanAnomaly
        ) -> MeanAnomaly:
            return add(M)(e * math.sin(E_i_guess))

        solution_b = eccentric_anomaly_solved(
            example_fixed_point_function,
            Eccentricity(Ratio(Scalar(0.72))),
            MeanAnomaly(Anomaly(Radians(Scalar(0.8726646)))),
            tolerance=1e-11,
        )

        self.assertAlmostEqual(solution_b[0], solution_a[0], 5)

        self.assertEqual(
            len(solution_b[1]),
            9,
        )

        self.assertTrue(len(solution_b[1]) > len(solution_a[1]))

        self.assertEqual(
            eccentric_anomaly_solved(
                newtons_method_eccentric_anomaly,
                Eccentricity(Ratio(Scalar(0.8))),
                MeanAnomaly(Anomaly(Radians(Scalar(5.5)))),
            )[0],
            4.70006079291257,
        )

    def test_time_to_true_anomaly(self):
        self.assertAlmostEqual(
            time_to_true_anomaly(
                EXAMPLE_ELEMENTS, TrueAnomaly(Anomaly(Radians(Scalar(4.2))))
            ),
            Second(Scalar(44103.88217238126)),
            places=7,
        )

        self.assertTrue(
            time_to_true_anomaly(EXAMPLE_ELEMENTS, EXAMPLE_ELEMENTS.true_anomaly)
            == Second(Scalar(0))
        )

        self.assertTrue(
            time_to_true_anomaly(
                EXAMPLE_ELEMENTS, TrueAnomaly(Anomaly(Radians(Scalar(5.0))))
            ),
            time_to_eccentric_anomaly(
                eccentric_anomaly_from_true_anomaly(
                    TrueAnomaly(Anomaly(Radians(Scalar(5.0)))),
                    EXAMPLE_ELEMENTS.eccentricity,
                ),
                EXAMPLE_ELEMENTS,
            ),
        )

    def test_planetary_sphere_of_influence_approximation(self):

        soi = planetary_sphere_of_influence_approximation(
            mean_distance=ASTRONOMICAL_UNIT,
            planet_mass=EARTH_MASS,
            star_mass=SUN_MASS,
        )
        self.assertIsNotNone(soi)
        self.assertAlmostEqual(soi, 924_625_176.0377866, 5)

        # Mercury
        self.assertAlmostEqual(
            planetary_sphere_of_influence_approximation(
                mean_distance=Distance(Scalar(ASTRONOMICAL_UNIT * 0.387)),
                planet_mass=Mass(3.301e23),
                star_mass=SUN_MASS,
            ),
            112_379_467.40321627,
            5,
        )

        # Neptune
        self.assertAlmostEqual(
            planetary_sphere_of_influence_approximation(
                mean_distance=Distance(Scalar(ASTRONOMICAL_UNIT * 30.05708)),
                planet_mass=Mass(1.024e26),
                star_mass=SUN_MASS,
            ),
            86_613_295_806.5268,
            5,
        )

    def test_root_solver(self):
        solution, history = root_solver(
            iteration_function=lambda x: 0.5 * (x + 2 / x),
            initial_guess=1.0,
            difference_function=lambda next_x, x: next_x - x,
        )

        self.assertAlmostEqual(solution, math.sqrt(2), places=6)

        self.assertEqual(history[0], (0, 1.0, None))
        self.assertTrue(len(history) > 1)

    def test_solve_for_equilibrium(self):
        mu = GravitationalParameter(Scalar(0.5))

        self.assertAlmostEqual(
            solve_for_equilibrium(mu, initial_guess=0.0),
            0.0,
            places=6,
        )

        self.assertAlmostEqual(
            solve_for_equilibrium(mu, initial_guess=1.0),
            1.19840614455492,
            places=6,
        )

        self.assertAlmostEqual(
            solve_for_equilibrium(mu, initial_guess=-1.0),
            -1.19840614455492,
            places=6,
        )

    def test_lagrange_points_equal_mass_bodies(self):
        m1 = Mass(Scalar(1))
        m2 = Mass(Scalar(1))
        r = Distance(Scalar(10))

        l1, l2, l3, l4, l5 = lagrange_points(m1, m2, r)

        self.assertAlmostEqual(l1.x, 0.0, places=6)
        self.assertAlmostEqual(l1.y, 0.0, places=6)

        self.assertAlmostEqual(l2.x, 11.9840614455492, places=6)
        self.assertAlmostEqual(l2.y, 0.0, places=6)

        self.assertAlmostEqual(l3.x, -11.9840614455492, places=6)
        self.assertAlmostEqual(l3.y, 0.0, places=6)

        self.assertAlmostEqual(l4.x, 0.0, places=6)
        self.assertAlmostEqual(l4.y, 8.660254037844386, places=6)

        self.assertAlmostEqual(l5.x, 0.0, places=6)
        self.assertAlmostEqual(l5.y, -8.660254037844386, places=6)


if __name__ == "__main__":
    unittest.main()
