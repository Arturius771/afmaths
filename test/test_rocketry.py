import unittest

from afmaths.types import Area, DeltaV, Force, Mass, Pressure
from afmaths.physics.space.engineering.astrodynamics.hohmann_transfer import (
    hohmann_transfer_parameters,
)
from afmaths.physics.space.engineering.rocketry import (
    burn_duration,
    delta_v_for_stages,
    delta_v_from_tsiolkovsky,
    effective_exhaust_velocity,
    full_mass,
    mass_flow_rate,
    max_payload_mass,
    propellant_mass_from_full_mass,
    required_mass_ratio,
    net_rocket_acceleration,
    specific_impulse,
    specific_impulse_from_exhaust_velocity,
    thrust_from_mass_flow_and_pressure,
    thrust_to_weight,
    total_impulse,
    total_impulse_from_exhaust_velocity,
)
from astronomy_types import Distance, Rate, Scalar, Second, Velocity


class RocketryTestMethods(unittest.TestCase):

    def test_propellant_mass_from_full_mass(self):

        self.assertEqual(
            propellant_mass_from_full_mass(
                Mass(1000),
                hohmann_transfer_parameters(
                    Distance(Scalar(300000)), Distance(Scalar(1000000))
                )[0][0],
                Velocity(Scalar(3000)),
            ),
            117.62061592204387,
        )

    def test_delta_v_for_stages(self):

        total_delta_v, stage_delta_vs = delta_v_for_stages(
            mass_per_stage=[
                Mass(1000),  # launch mass
                Mass(500),  # after stage 1 burn
                Mass(200),  # after stage 2 burn
            ],
            effective_exhaust_velocity=Velocity(Scalar(3000)),
        )

        self.assertEqual(
            total_delta_v,
            4828.313737302302,
        )
        self.assertEqual(
            stage_delta_vs,
            [2079.441541679836, 2748.8721956224654],
        )

    def test_max_payload_mass(self):

        self.assertEqual(
            max_payload_mass(
                Mass(5000),
                required_mass_ratio(
                    DeltaV(Velocity(Scalar(10_000))), Velocity(Scalar(500))
                ),
                Mass(500),
            ),
            -499.9999896942319,
        )

    def test_thrust_to_weight(self):

        self.assertEqual(
            thrust_to_weight(Force(Scalar(5_000)), Mass(500)),
            1.0197162129779282,
        )

    def test_net_rocket_acceleration(self):

        self.assertEqual(
            net_rocket_acceleration(
                Force(Scalar(5_000)),
                Mass(500),
            ),
            0.19335000000000058,
        )

    def test_burn_duration(self):

        self.assertEqual(
            burn_duration(
                mass_flow_rate=Rate(Scalar(5)),
                propellant_mass=Mass(100),
            ),
            20,
        )

        specific_impulse_seconds = Second(Scalar(100))

        dry_mass_value = Mass(100)

        full_mass_value = full_mass(
            dry_mass_value,
            Mass(100),
        )

        exhaust_velocity = effective_exhaust_velocity(
            specific_impulse_seconds,
        )

        self.assertAlmostEqual(
            burn_duration(
                mass_flow_rate(
                    thrust_from_mass_flow_and_pressure(
                        Rate(Scalar(5)),
                        exhaust_velocity,
                        Pressure(Scalar(0)),
                        Pressure(Scalar(0)),
                        Area(Scalar(1)),
                    ),
                    specific_impulse_seconds,
                ),
                propellant_mass_from_full_mass(
                    full_mass_value,
                    delta_v_from_tsiolkovsky(
                        exhaust_velocity,
                        full_mass_value,
                        dry_mass_value,
                    ),
                    exhaust_velocity,
                ),
            ),
            20,
        )

    def test_total_impulse_consistency_for_constant_thrust_burn(self):
        specific_impulse_seconds = Second(Scalar(300))
        propellant_mass = Mass(60)
        propellant_mass_flow_rate = Rate(Scalar(2))

        exhaust_velocity = effective_exhaust_velocity(
            specific_impulse_seconds,
        )
        thrust = thrust_from_mass_flow_and_pressure(
            mass_flow_rate=propellant_mass_flow_rate,
            effective_exhaust_velocity=exhaust_velocity,
            exhaust_pressure=Pressure(Scalar(0)),
            outside_pressure=Pressure(Scalar(0)),
            nozzle_exit=Area(Scalar(1)),
        )

        self.assertAlmostEqual(
            total_impulse(
                thrust,
                burn_duration(
                    mass_flow_rate=propellant_mass_flow_rate,
                    propellant_mass=propellant_mass,
                ),
            ),
            total_impulse_from_exhaust_velocity(
                exhaust_velocity,
                propellant_mass,
            ),
        )

        self.assertAlmostEqual(
            mass_flow_rate(
                thrust,
                specific_impulse_seconds,
            ),
            propellant_mass_flow_rate,
        )

        self.assertAlmostEqual(
            specific_impulse(
                thrust,
                propellant_mass_flow_rate,
            ),
            specific_impulse_seconds,
        )

        self.assertAlmostEqual(
            specific_impulse_from_exhaust_velocity(
                exhaust_velocity,
            ),
            specific_impulse_seconds,
        )


if __name__ == "__main__":
    unittest.main()
