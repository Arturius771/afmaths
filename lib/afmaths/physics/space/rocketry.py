import math
from typing import NewType

from afmaths.constants import STANDARD_GRAVITY
from afmaths.geometry import Area
from afmaths.operation import (
    add,
    divide_by,
    exponentiate,
    multiply,
    negate,
    ratio,
    subtract,
    summation,
)
from astronomy_types import (
    Distance,
    Rate,
    Ratio,
    Scalar,
    Velocity,
)

from afmaths.physics.space.astrodynamics import DeltaV, hohmann_transfer

Mass = NewType("Mass", float)
Pressure = NewType("Pressure", float)
Force = NewType("Force", float)


def ideal_rocket_equation(
    effective_exhaust_velocity: Velocity, initial_mass: Mass, final_mass: Mass
) -> Velocity:
    return multiply(math.log(mass_ratio(final_mass, initial_mass)))(
        effective_exhaust_velocity
    )


def propellant_mass_from_initial_mass(
    initial_mass: Mass, delta_v: DeltaV, effective_exhaust_velocity: Velocity
) -> Mass:
    return multiply(initial_mass)(
        subtract(
            exponentiate(negate(divide_by(effective_exhaust_velocity)(delta_v)))(math.e)
        )(1)
    )


def propellant_mass_from_final_mass(
    final_mass: Mass, delta_v: DeltaV, effective_exhaust_velocity: Velocity
) -> Mass:
    return multiply(final_mass)(
        subtract(1)(
            exponentiate(divide_by(effective_exhaust_velocity)(delta_v))(math.e)
        )
    )


def empty_weight(structure_mass: Mass, payload_mass: Mass, motor_mass: Mass) -> Mass:
    return add(add(structure_mass)(motor_mass))(payload_mass)


def total_rocket_mass(empty_weight: Mass, propellant_mass: Mass) -> Mass:
    return add(empty_weight)(propellant_mass)


def mass_ratio(empty_weight: Mass, initial_mass: Mass) -> float:
    return divide_by(empty_weight)(initial_mass)


def specific_impulse(force_newtons: float, mass_flow: Rate) -> float:
    return divide_by(multiply(mass_flow)(STANDARD_GRAVITY))(force_newtons)


def specific_impulse_from_exhause_velocity(exhaust_velocity: Velocity) -> float:
    return divide_by(STANDARD_GRAVITY)(exhaust_velocity)


def effective_exhaust_velocity(specific_impulse: float) -> Velocity:
    return multiply(specific_impulse)(STANDARD_GRAVITY)


def delta_v_for_stages(
    mass_per_stage: list[Mass],
    effective_exhaust_velocity: Velocity,
) -> tuple[DeltaV, list[DeltaV]]:

    def stage_delta_v(i: int) -> float:
        return ideal_rocket_equation(
            effective_exhaust_velocity,
            mass_per_stage[i],
            mass_per_stage[i + 1],
        )

    stage_delta_vs = [
        DeltaV(Velocity(Scalar(stage_delta_v(i))))
        for i in range(len(mass_per_stage) - 1)
    ]

    total_delta_v = DeltaV(
        Velocity(
            Scalar(
                summation(
                    stage_delta_v,
                    0,
                    len(mass_per_stage) - 2,
                )
            )
        )
    )

    return total_delta_v, stage_delta_vs


def momentum(
    initial_mass: Mass,
    delta_mass: Mass,
    initial_velocity: Velocity,
    delta_v: Velocity,
) -> float:
    return multiply(subtract(delta_mass)(initial_mass))(add(initial_velocity)(delta_v))


def thrust(
    mass_flow_rate: float,
    exit_velocity: Velocity,
    exit_pressure: Pressure,
    outside_pressure: Pressure,
    nozzle_exit: Area,
) -> Force:
    return add(multiply(mass_flow_rate)(exit_velocity))(
        multiply(subtract(outside_pressure)(exit_pressure))(nozzle_exit)
    )


def thrust_to_weight(thrust: Force, weight: Mass) -> Ratio:
    return Ratio(Scalar(ratio(thrust)(weight)))


if __name__ == "__main__":

    print(
        propellant_mass_from_initial_mass(
            Mass(1000),
            hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000)))[0],
            Velocity(Scalar(3)),
        )
    )

    total_delta_v, stage_delta_vs = delta_v_for_stages(
        mass_per_stage=[
            Mass(1000),  # launch mass
            Mass(500),  # after stage 1 burn
            Mass(200),  # after stage 2 burn
        ],
        effective_exhaust_velocity=Velocity(Scalar(3000)),
    )

    print(f"Total Δv: {total_delta_v}")
    print(f"Stage Δvs: {stage_delta_vs}")
