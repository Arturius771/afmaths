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
    Second,
    Velocity,
)

from afmaths.physics.physics import (
    impulse_from_force,
    net_acceleration,
    force,
    pushing_to_resisting_force_ratio,
    momentum,
)

from afmaths.physics.space.engineering.astrodynamics.maneuvers import delta_v
from afmaths.types import DeltaV, Force, Impulse, Mass, Momentum, Pressure


def delta_v_from_tsiolkovsky(
    effective_exhaust_velocity: Velocity, full_mass: Mass, dry_mass: Mass
) -> DeltaV:
    """Calculates the change in velocity of a rocket given the effective exhaust velocity, initial mass, and dry mass."""
    return multiply(math.log(full_to_dry_mass_ratio(dry_mass, full_mass)))(
        effective_exhaust_velocity
    )


def post_burn_momentum(
    initial_mass: Mass,
    delta_mass: Mass,
    initial_velocity: Velocity,
    delta_v: Velocity,
) -> Momentum:
    """After shedding mass and gaining velocity"""
    return momentum(
        subtract(delta_mass)(initial_mass),
        add(initial_velocity)(delta_v),
    )


# region Performance


def mass_flow_rate(
    thrust: Force,
    specific_impulse: Second,
    gravitational_acceleration: Acceleration = STANDARD_GRAVITY,
) -> Rate:
    """The change in mass per unit time, as it is expelled out of the rocket."""
    return divide_by(multiply(specific_impulse)(gravitational_acceleration))(thrust)


def total_impulse(thrust: Force, burn_duration: Second) -> Impulse:
    """Assuming constant thrust"""
    return impulse_from_force(thrust, burn_duration)


def total_impulse_from_exhaust_velocity(
    effective_exhaust: Velocity, propellant_mass: Mass
) -> Impulse:
    return multiply(effective_exhaust)(propellant_mass)


def initial_momentum(rocket_mass: Mass, rocket_velocity: Velocity) -> Momentum:
    return momentum(rocket_mass, rocket_velocity)


def final_momentum(
    initial_rocket: Mass,
    final_rocket: Mass,
    initial_velocity: Velocity,
    final_velocity: Velocity,
) -> Momentum:
    delta_m = subtract(final_rocket)(initial_rocket)
    dv = delta_v(initial_velocity, final_velocity)
    return momentum(subtract(delta_m)(initial_rocket), add(initial_velocity)(dv))


def momentum_gain(initial: Momentum, final: Momentum) -> Momentum:
    return subtract(final)(initial)


def specific_impulse(
    thrust: float,
    mass_flow: Rate,
    gravitational_acceleration: Acceleration = STANDARD_GRAVITY,
) -> Second:
    """I_sp = thrust /"""
    return divide_by(multiply(mass_flow)(gravitational_acceleration))(thrust)


def specific_impulse_from_exhaust_velocity(
    exhaust_velocity: Velocity,
    gravitational_acceleration: Acceleration = STANDARD_GRAVITY,
) -> Second:
    """I_sp = C_e/g"""
    return divide_by(gravitational_acceleration)(exhaust_velocity)


def effective_exhaust_velocity(
    specific_impulse: Second,
    gravitational_acceleration: Acceleration = STANDARD_GRAVITY,
) -> Velocity:
    """
    C_e = I_sp * g

    specific_impulse = s
    gravitational_acceleration = m/s²

    s * m/s² = m/s"""
    return multiply(specific_impulse)(gravitational_acceleration)


def delta_v_for_stages(
    mass_per_stage: list[Mass],
    effective_exhaust_velocity: Velocity,
) -> tuple[DeltaV, list[DeltaV]]:

    def stage_delta_v(i: int) -> DeltaV:
        return delta_v_from_tsiolkovsky(
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


def thrust_from_mass_flow_and_pressure(
    mass_flow_rate: float,
    effective_exhaust_velocity: Velocity,
    exhaust_pressure: Pressure,
    outside_pressure: Pressure,
    nozzle_exit: Area,
) -> Force:
    return add(multiply(mass_flow_rate)(effective_exhaust_velocity))(
        multiply(subtract(outside_pressure)(exhaust_pressure))(nozzle_exit)
    )


def burn_duration(mass_flow_rate: Rate, propellant_mass: Mass) -> Second:
    return Second(Scalar(divide_by(mass_flow_rate)(propellant_mass)))


# endregion


# region Equations of Mass


def dry_mass(structure_mass: Mass, payload_mass: Mass, motor_mass: Mass) -> Mass:
    return add(add(structure_mass)(motor_mass))(payload_mass)


def propellant_mass_from_full_mass(
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


def full_to_dry_mass_ratio(dry_mass: Mass, full_mass: Mass) -> Ratio:
    return divide_by(dry_mass)(full_mass)


def payload_to_non_payload_stage_mass_ratio(
    propellant_mass: Mass, structure_mass: Mass, payload_mass: Mass
) -> Ratio:
    return divide_by(add(structure_mass)(propellant_mass))(payload_mass)


def mass_ratio(structural_coefficient: Ratio, payload_mass_ratio: Ratio) -> Ratio:
    add_payload_ratio = add(payload_mass_ratio)
    return divide_by(add_payload_ratio(structural_coefficient))(add_payload_ratio(1))


def net_rocket_acceleration(
    thrust: Force, mass: Mass, standard_g: Acceleration = STANDARD_GRAVITY
) -> Acceleration:
    return net_acceleration(thrust, mass, standard_g)


def required_mass_ratio(delta_v: DeltaV, effective_exhaust_velocity: Velocity) -> Ratio:
    """How much lighter the rocket must be to complete a burn with the required DeltaV"""
    return exponentiate(divide_by(effective_exhaust_velocity)(delta_v))(math.e)


def structural_coefficient(structure_mass: Mass, propellant_mass: Mass) -> Ratio:
    return divide_by(add(structure_mass)(propellant_mass))(structure_mass)


def max_payload_mass(
    propellant_mass: Mass, required_mass_ratio: Ratio, dry_non_payload_mass: Mass
) -> Mass:
    """P = (M_p / (R-1)) - D"""
    return subtract(dry_non_payload_mass)(
        divide_by(subtract(1)(required_mass_ratio))(propellant_mass)
    )


# endregion
