from astronomy_types import (
    Distance,
    GravitationalParameter,
    OrbitalElements,
    Second,
)
from afmaths.constants import (
    EARTH_MU_KM_CUBED,
    EARTH_RADIUS_KM,
)
from afmaths.physics.space.engineering.astrodynamics.maneuvers import (
    decrease_semi_major_axis_at_apoapsis,
    decrease_semi_major_axis_at_periapsis,
    increase_semi_major_axis_at_apoapsis,
    increase_semi_major_axis_at_periapsis,
    transfer_period,
    transfer_semi_major_axis,
)
from afmaths.physics.space.engineering.astrodynamics.orbital_directions import (
    burn_direction_at_apsis,
)
from afmaths.types import OrbitalDirection, DeltaV
from afmaths.operation import (
    add,
)
from afmaths.physics.space.celestial_mechanics import (
    apoapsis_radius,
    orbit_altitude,
    orbit_radius,
    periapsis_radius,
)


def hohmann_transfer_from_orbital_elements(
    initial_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[tuple[DeltaV, ...], OrbitalDirection, Second]:
    """Assume a circular obit for initial and final."""
    return hohmann_transfer_parameters(
        orbit_altitude(
            periapsis_radius(initial_orbit.semi_major_axis, initial_orbit.eccentricity),
            initial_body_radius,
        ),
        orbit_altitude(
            apoapsis_radius(final_orbit.semi_major_axis, final_orbit.eccentricity),
            initial_body_radius,
        ),
        initial_body_radius,
        mu,
    )


def hohmann_transfer_delta_v(
    initial_radius: Distance,
    target_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, ...]:
    """Calculates the delta-v required for a Hohmann transfer. Assumes a circular initial and final orbit."""
    # www.braeunig.us/space/problem.htm#4.19

    transfer_a = transfer_semi_major_axis(initial_radius, target_radius)

    direction = burn_direction_at_apsis(initial_radius, target_radius)
    prograde = direction is OrbitalDirection.PROGRADE
    transfer_delta_v = (
        increase_semi_major_axis_at_periapsis(transfer_a, initial_radius, mu)
        if prograde
        else decrease_semi_major_axis_at_apoapsis(transfer_a, target_radius, mu)
    )

    circularise = (
        increase_semi_major_axis_at_apoapsis(transfer_a, target_radius, mu)
        if prograde
        else decrease_semi_major_axis_at_periapsis(transfer_a, initial_radius, mu)
    )

    total = DeltaV(add(transfer_delta_v)(circularise))

    return (
        total,
        transfer_delta_v,
        circularise,
    )


def hohmann_transfer_parameters(
    initial_altitude: Distance,
    target_altitude: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[tuple[DeltaV, ...], OrbitalDirection, Second]:

    initial_r = orbit_radius(initial_altitude, initial_body_radius)
    target_r = orbit_radius(target_altitude, initial_body_radius)

    delta_v = hohmann_transfer_delta_v(
        initial_r,
        target_r,
        mu,
    )

    direction = burn_direction_at_apsis(
        initial_r,
        target_r,
    )

    period = transfer_period(
        initial_r,
        target_r,
        mu,
    )

    return (delta_v, direction, period)
