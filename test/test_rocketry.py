import unittest

from afmaths.constants import DeltaV, Force, Mass
from afmaths.physics.space.engineering.astrodynamics import hohmann_transfer
from afmaths.physics.space.rocketry import (
    delta_v_for_stages,
    payload_mass_for_delta_v,
    propellant_mass_from_initial_mass,
    required_mass_ratio,
    rocket_acceleration,
    thrust_to_weight,
)
from astronomy_types import Distance, Scalar, Velocity


class RocketryTestMethods(unittest.TestCase):

    def test_propellant_mass_from_initial_mass(self):

        self.assertEqual(
            propellant_mass_from_initial_mass(
                Mass(1000),
                hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000)))[0],
                Velocity(Scalar(3)),
            ),
            117.62062398293438,
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

    def test_payload_mass_for_delta_v(self):

        self.assertEqual(
            payload_mass_for_delta_v(
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

    def test_rocket_acceleration(self):

        self.assertEqual(
            rocket_acceleration(
                Force(Scalar(5_000)),
                Mass(500),
            ),
            0.19335000000000058,
        )


if __name__ == "__main__":
    unittest.main()
