import math
from astronomy_types import (
    Distance,
    Eccentricity,
    EquatorialCoordinates,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Ratio,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVector,
    Velocity,
    Inclination,
)
from afmaths.constants import (
    EARTH_MU_KM_CUBED,
)
from afmaths.types import DeltaV
from afmaths.geometry.geometry import (
    eccentricity_factor_plus,
    semi_major_axis_from_vertex_distances,
)
from afmaths.operation import (
    DOUBLE,
    HALF,
    divide_by,
    multiply,
    square_root,
    subtract,
)
from afmaths.physics.space.type_conversion_helpers import (
    vector3d_from_position,
    vector3d_from_velocity,
)
from afmaths.physics.space.celestial_mechanics import (
    eccentricity_from_apsides,
    orbital_elements_from_state_vectors,
    orbital_period,
    periapsis_radius,
    periapsis_velocity,
    radial_velocity,
    delta_v,
    velocity_at_radius,
    vis_viva,
)
from afmaths.tensors import (
    vector_magnitude_3d,
)

# def trajectory_propagation(
#     state: StateVector, perturbations: list[Vector3D]
# ) -> StateVector:

#     position = []

#     for p in perturbations:
#         propagate_vector_3d(
#             Coordinate3D(state.position.x, state.position.y, state.position.z), p
#         )


def flight_path_angle(
    state: StateVector, mu: GravitationalParameter = EARTH_MU_KM_CUBED
) -> Radians:
    elements = orbital_elements_from_state_vectors(state)

    return Radians(
        Scalar(
            math.acos(
                divide_by(
                    multiply(
                        vector_magnitude_3d(vector3d_from_position(state.position))
                    )(vector_magnitude_3d(vector3d_from_velocity(state.velocity)))
                )(
                    multiply(
                        periapsis_radius(
                            elements.semi_major_axis, elements.eccentricity
                        )
                    )(periapsis_velocity(mu, elements))
                )
            )
        )
    )


def flight_path_angle_from_elements(elements: OrbitalElements) -> Radians:
    return Radians(
        Scalar(
            math.atan(
                divide_by(
                    eccentricity_factor_plus(
                        multiply(elements.eccentricity)(math.cos(elements.true_anomaly))
                    )
                )(multiply(elements.eccentricity)(math.sin(elements.true_anomaly)))
            )
        )
    )


def signed_flight_path_angle(state: StateVector) -> Radians:
    r = vector_magnitude_3d(vector3d_from_position(state.position))
    v = vector_magnitude_3d(vector3d_from_velocity(state.velocity))

    return Radians(Scalar(math.asin(divide_by(v)(radial_velocity(state)))))


def angle_above_orbital_plane(
    target_object: EquatorialCoordinates,
    orbit: OrbitalElements,
) -> Radians:
    value = math.cos(target_object.declination) * math.sin(
        orbit.inclination
    ) * math.sin(
        orbit.right_ascension_of_ascending_node - target_object.right_ascension
    ) + math.sin(
        target_object.declination
    ) * math.cos(
        orbit.inclination
    )

    # Prevent floating point drift errors at values close to +/-1.
    value = max(-1.0, min(1.0, value))

    return Radians(Scalar(math.asin(value)))


def angular_velocity_from_sidereal_period(
    sidereal_period: Second = Second(Scalar(86164.09)),
) -> Radians:
    return divide_by(sidereal_period)(DOUBLE(math.pi))


# region Maneuvers

# TODO: function(s) to change specific orbital elements


def increase_semi_major_axis_at_periapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return delta_v(
        velocity_at_radius(current_radius, mu),
        vis_viva(mu, current_radius, a),
    )


def increase_semi_major_axis_at_apoapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return delta_v(
        vis_viva(mu, current_radius, a),
        velocity_at_radius(current_radius, mu),
    )


def decrease_semi_major_axis_at_periapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return delta_v(
        vis_viva(mu, current_radius, a),
        velocity_at_radius(current_radius, mu),
    )


def decrease_semi_major_axis_at_apoapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return delta_v(
        velocity_at_radius(current_radius, mu),
        vis_viva(mu, current_radius, a),
    )


def inclination_change_at_node(
    velocity_at_node: Velocity,
    current_inclination: Inclination,
    target_inclination: Inclination,
) -> DeltaV:
    difference = abs(subtract(target_inclination)(current_inclination))
    return DeltaV(
        Velocity(Scalar(multiply(DOUBLE(velocity_at_node))(math.sin(HALF(difference)))))
    )


# region Transfer Orbit
def parabolic_escape(elements: OrbitalElements, mu: GravitationalParameter) -> DeltaV:
    velocity_at_periapsis = periapsis_velocity(mu, elements)
    parabolic_escape_velocity = Velocity(
        Scalar(
            square_root(
                divide_by(
                    periapsis_radius(elements.semi_major_axis, elements.eccentricity)
                )(DOUBLE(mu))
            )
        )
    )

    return delta_v(velocity_at_periapsis, parabolic_escape_velocity)


def transfer_period(
    mu: GravitationalParameter,
    initial_radius: Distance,
    final_radius: Distance,
) -> Second:
    """Assuming an elliptical transfer orbit."""

    return HALF(
        orbital_period(transfer_semi_major_axis(initial_radius, final_radius), mu)
    )


def transfer_semi_major_axis(
    initial_radius: Distance, final_radius: Distance
) -> SemiMajorAxis:
    return semi_major_axis_from_vertex_distances(initial_radius, final_radius)


def transfer_eccentricity(
    initial_radius: Distance, final_radius: Distance
) -> Eccentricity:
    return Eccentricity(
        Ratio(Scalar(abs(eccentricity_from_apsides(initial_radius, final_radius))))
    )
