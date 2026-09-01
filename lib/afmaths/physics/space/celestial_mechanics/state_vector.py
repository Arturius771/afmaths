from dataclasses import replace


from afmaths.constants import (
    EARTH_MU,
)

from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    apoapsis_true_anomaly,
    eccentric_anomaly_from_true_anomaly,
    periapsis_true_anomaly,
    perifocal_radial_unit_vector,
    perifocal_velocity_direction_vector,
    true_anomaly_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.transformations import (
    transform_vector_from_perifocal,
)
from afmaths.physics.space.type_conversion_helpers import (
    position_from_vector,
    make_state_vector,
    velocity_from_vector,
    vector3d_from_position,
    vector3d_from_velocity,
)
from afmaths.tensors import (
    vector_multiplication_3d,
)
from afmaths.operation import (
    SQUARE,
    divide_by,
    multiply,
    square_root,
    subtract,
)
from astronomy_types import (
    GravitationalParameter,
    OrbitalElements,
    PositionVector,
    Second,
    SemiMajorAxis,
    Eccentricity,
    StateVector,
    TrueAnomaly,
    Scalar,
    VelocityVector,
)


from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    kepler_equation,
    mean_motion,
    orbit_equation,
)


def position_vectors_for_period(
    orbital_elements: OrbitalElements,
    number_of_orbits: int = 1,
    mu: GravitationalParameter = EARTH_MU,
    time_step: Second = Second(Scalar(1)),
) -> list[PositionVector]:
    """Calculates the position vectors of an orbit over one orbital period."""
    period = orbital_period(orbital_elements.semi_major_axis, mu) * number_of_orbits
    time_steps = [Second(Scalar(t)) for t in range(0, int(period), int(time_step))]
    return [position_vector_at_time(orbital_elements, t, mu) for t in time_steps]


def velocity_vectors_for_period(
    orbital_elements: OrbitalElements,
    number_of_orbits: int = 1,
    mu: GravitationalParameter = EARTH_MU,
    time_step: Second = Second(Scalar(1)),
) -> list[VelocityVector]:
    """Calculates the velocity vectors of an orbit over one orbital period."""
    period = orbital_period(orbital_elements.semi_major_axis, mu) * number_of_orbits
    time_steps = [Second(Scalar(t)) for t in range(0, int(period), int(time_step))]
    return [velocity_vector_at_time(orbital_elements, t, mu) for t in time_steps]


def position_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset: Second = Second(Scalar(0)),
    mu: GravitationalParameter = EARTH_MU,
) -> PositionVector:
    """Calculates the position vector of an orbit from the orbital elements at a given time offset from the current position in the orbit."""
    return state_vector_at_time(orbital_elements, time_offset, mu).position


def perifocal_position_vector(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    """Calculates the position vector in the perifocal coordinate system"""
    # SFM L02: r = p / (1 + e * cos(theta)) * [cos(theta), sin(theta), 0]
    return position_from_vector(
        vector_multiplication_3d(
            perifocal_radial_unit_vector(orbital_elements.true_anomaly),
            orbit_equation(
                orbital_elements.semi_major_axis,
                orbital_elements.eccentricity,
                orbital_elements.true_anomaly,
            ),
        )
    )


def perifocal_position_at_periapsis(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    """Calculates the position vector of an orbit at periapsis in the perifocal reference frame."""
    return perifocal_position_vector(
        replace(
            orbital_elements,
            true_anomaly=periapsis_true_anomaly(),
        )
    )


def perifocal_position_at_apoapsis(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    """Calculates the position vector of an orbit at apoapsis in the perifocal reference frame."""
    return perifocal_position_vector(
        replace(
            orbital_elements,
            true_anomaly=apoapsis_true_anomaly(),
        )
    )


def orbital_plane_position_at_true_anomaly(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    """Calculates the position vector of an orbit at a given true anomaly in the orbital plane reference frame."""
    return perifocal_position_vector(orbital_elements)


def velocity_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset_s: Second = Second(Scalar(0)),
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> VelocityVector:
    """Calculates the velocity vector of an orbit from the orbital elements at a given time offset from the current position in the orbit."""
    return state_vector_at_time(
        orbital_elements, time_offset_s, gravitational_parameter
    ).velocity


def perifocal_velocity_vector(
    theta: TrueAnomaly,
    e: Eccentricity,
    a: SemiMajorAxis,
    mu: GravitationalParameter,
) -> VelocityVector:
    """Calculates the velocity vector in the perifocal coordinate system"""

    return velocity_from_vector(
        vector_multiplication_3d(
            perifocal_velocity_direction_vector(theta, e),
            Scalar(square_root(divide_by(multiply(a)(subtract(SQUARE(e))(1)))(mu))),
        )
    )


def state_vector_from_orbital_elements(
    orbital_elements: OrbitalElements,
    mu: GravitationalParameter = EARTH_MU,
) -> StateVector:
    """Calculates the state vectors (position and velocity) of an orbit from the orbital elements.

    The reference frame for the state vector will match the reference frame for the orbital elements. However it is calculated using idea two body interactions. Perturbations are not accounted for.
    """

    # PQW frame position and velocity vectors
    perifocal_position_gaussian = perifocal_position_vector(orbital_elements)
    perifocal_velocity_gaussian = perifocal_velocity_vector(
        orbital_elements.true_anomaly,
        orbital_elements.eccentricity,
        orbital_elements.semi_major_axis,
        mu,
    )

    return make_state_vector(
        position_from_vector(
            transform_vector_from_perifocal(
                orbital_elements,
                vector3d_from_position(perifocal_position_gaussian),
            )
        ),
        velocity_from_vector(
            transform_vector_from_perifocal(
                orbital_elements,
                vector3d_from_velocity(perifocal_velocity_gaussian),
            )
        ),
    )


def state_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset: Second = Second(Scalar(0)),
    mu: GravitationalParameter = EARTH_MU,
) -> StateVector:
    """Calculates the state vectors (position and velocity) of an orbit from the orbital elements at a given time offset from the current position in the orbit."""

    initial_mean_anomaly = kepler_equation(
        eccentric_anomaly_from_true_anomaly(
            orbital_elements.true_anomaly, orbital_elements.eccentricity
        ),
        orbital_elements.eccentricity,
    )

    true_anomaly_at_offset = true_anomaly_at_time(
        orbital_elements.eccentricity,
        initial_mean_anomaly,
        time_offset,
        mean_motion(orbital_elements.semi_major_axis, mu),
    )

    return state_vector_from_orbital_elements(
        replace(orbital_elements, true_anomaly=true_anomaly_at_offset), mu
    )
