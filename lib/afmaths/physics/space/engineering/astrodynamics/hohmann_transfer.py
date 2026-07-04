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
)
from afmaths.physics.space.engineering.astrodynamics.orbital_directions import (
    burn_direction_at_apsis,
)
from afmaths.types import OrbitalDirection, DeltaV
from afmaths.geometry.geometry import (
    eccentricity_factor_plus,
    semi_major_axis_from_vertex_distances,
)
from afmaths.operation import (
    add,
)
from afmaths.physics.space.type_conversion_helpers import (
    vector3d_from_position,
    vector3d_from_velocity,
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
) -> tuple[DeltaV, DeltaV, DeltaV, OrbitalDirection, Second]:
    """Assume a circular obit for initial and final."""
    return hohmann_transfer(
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


def hohmann_transfer_from_radii(
    initial_radius: Distance,
    target_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, DeltaV, OrbitalDirection, Second]:
    """Calculates the delta-v required for a Hohmann transfer. Assumes a circular initial and final orbit."""
    # www.braeunig.us/space/problem.htm#4.19

    semi_major_axis_transfer_ellipse = semi_major_axis_from_vertex_distances(
        initial_radius, target_radius
    )

    direction = burn_direction_at_apsis(initial_radius, target_radius)
    transfer_delta_v = (
        increase_semi_major_axis_at_periapsis(
            semi_major_axis_transfer_ellipse, initial_radius, mu
        )
        if direction is OrbitalDirection.PROGRADE
        else decrease_semi_major_axis_at_apoapsis(
            semi_major_axis_transfer_ellipse, target_radius, mu
        )
    )

    circularise = (
        increase_semi_major_axis_at_apoapsis(
            semi_major_axis_transfer_ellipse, target_radius, mu
        )
        if direction is OrbitalDirection.PROGRADE
        else decrease_semi_major_axis_at_periapsis(
            semi_major_axis_transfer_ellipse, initial_radius, mu
        )
    )

    total = DeltaV(add(transfer_delta_v)(circularise))

    period = transfer_period(
        mu,
        initial_radius,
        target_radius,
    )

    return (
        total,
        transfer_delta_v,
        circularise,
        burn_direction_at_apsis(initial_radius, target_radius),
        period,
    )


def hohmann_transfer(
    initial_altitude: Distance,
    target_altitude: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, DeltaV, OrbitalDirection, Second]:
    """Calculates the delta-v required for a Hohmann transfer. Assumes a circular initial and final orbit."""
    # www.braeunig.us/space/problem.htm#4.19

    return hohmann_transfer_from_radii(
        orbit_radius(initial_altitude, initial_body_radius),
        orbit_radius(target_altitude, initial_body_radius),
        mu,
    )
