import math

from afmaths.constants import STANDARD_GRAVITY
from afmaths.geometry.geometry import Area
from afmaths.operation import (
    add,
    divide_by,
    exponentiate,
    multiply,
    negate,
    subtract,
    summation,
)
from astronomy_types import (
    Acceleration,
    Rate,
    Ratio,
    Scalar,
    Velocity,
)

from afmaths.physics.physics import (
    net_acceleration,
    force,
    pushing_to_resisting_force_ratio,
    momentum,
)
from afmaths.physics.space.engineering.astrodynamics import DeltaV, hohmann_transfer
from afmaths.types import Force, Mass, Momentum, Pressure


def tsiolkovsky_ideal_rocket_equation(
    effective_exhaust_velocity: Velocity, initial_mass: Mass, dry_mass: Mass
) -> DeltaV:
    return multiply(math.log(rocket_mass_ratio(dry_mass, initial_mass)))(
        effective_exhaust_velocity
    )


def final_momentum(
    initial_mass: Mass,
    delta_mass: Mass,
    initial_velocity: Velocity,
    delta_v: Velocity,
) -> Momentum:
    """After shedding mass and gaining velocity"""
    return momentum(
        mass=(subtract(delta_mass)(initial_mass)),
        velocity=(add(initial_velocity)(delta_v)),
    )


# region Performance


def specific_impulse(force_newtons: float, mass_flow: Rate) -> float:
    return divide_by(multiply(mass_flow)(STANDARD_GRAVITY))(force_newtons)


def specific_impulse_from_exhaust_velocity(exhaust_velocity: Velocity) -> float:
    return divide_by(STANDARD_GRAVITY)(exhaust_velocity)


def effective_exhaust_velocity(specific_impulse: float) -> Velocity:
    return multiply(specific_impulse)(STANDARD_GRAVITY)


def delta_v_for_stages(
    mass_per_stage: list[Mass],
    effective_exhaust_velocity: Velocity,
) -> tuple[DeltaV, list[DeltaV]]:

    def stage_delta_v(i: int) -> DeltaV:
        return tsiolkovsky_ideal_rocket_equation(
            effective_exhaust_velocity,
            mass_per_stage[i],
            mass_per_stage[i + 1],
        )

    stage_delta_vs = [stage_delta_v(i) for i in range(len(mass_per_stage) - 1)]

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


def thrust_to_weight(
    thrust: Force,
    mass: Mass,
    gravitational_acceleration: Acceleration = STANDARD_GRAVITY,
) -> Ratio:
    """Greater than 1 to achieve flight"""
    return pushing_to_resisting_force_ratio(
        thrust, force(mass, gravitational_acceleration)
    )


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


# endregion


# region Equations of Mass


def dry_mass(structure_mass: Mass, payload_mass: Mass, motor_mass: Mass) -> Mass:
    return add(add(structure_mass)(motor_mass))(payload_mass)


def propellant_mass_from_initial_mass(
    full_mass: Mass, delta_v: DeltaV, effective_exhaust_velocity: Velocity
) -> Mass:
    return multiply(full_mass)(
        subtract(
            exponentiate(negate(divide_by(effective_exhaust_velocity)(delta_v)))(math.e)
        )(1)
    )


def propellant_mass_from_dry_mass(
    dry_mass: Mass, delta_v: DeltaV, effective_exhaust_velocity: Velocity
) -> Mass:
    return multiply(dry_mass)(
        subtract(1)(
            exponentiate(divide_by(effective_exhaust_velocity)(delta_v))(math.e)
        )
    )


def full_mass(dry_mass: Mass, propellant_mass: Mass) -> Mass:
    return add(dry_mass)(propellant_mass)


def rocket_mass_ratio(dry_mass: Mass, full_mass: Mass) -> Ratio:
    return divide_by(dry_mass)(full_mass)


def payload_mass_ratio(
    propellant_mass: Mass, structure_mass: Mass, payload_mass: Mass
) -> Ratio:
    return divide_by(add(structure_mass)(propellant_mass))(payload_mass)


def mass_ratio_from_ratio(
    structural_coefficient: Ratio, payload_mass_ratio: Ratio
) -> Ratio:
    add_payload_ratio = add(payload_mass_ratio)
    return divide_by(add_payload_ratio(structural_coefficient))(add_payload_ratio(1))


def rocket_acceleration(
    thrust: Force, mass: Mass, standard_g: Acceleration = STANDARD_GRAVITY
) -> Acceleration:
    return net_acceleration(thrust, mass, standard_g)


def required_mass_ratio(delta_v: DeltaV, effective_exhaust_velocity: Velocity) -> Ratio:
    """How much lighter the rocket must be to complete a burn with the required DeltaV"""
    return exponentiate(divide_by(effective_exhaust_velocity)(delta_v))(math.e)


def structural_coefficient(structure_mass: Mass, propellant_mass: Mass) -> Ratio:
    return divide_by(add(structure_mass)(propellant_mass))(structure_mass)


def payload_mass_for_delta_v(
    propellant_mass: Mass, required_mass_ratio: Ratio, dry_non_payload_mass: Mass
) -> Mass:
    """P = (M_p / (R-1)) - D"""
    return subtract(dry_non_payload_mass)(
        divide_by(subtract(1)(required_mass_ratio))(propellant_mass)
    )


# endregion
