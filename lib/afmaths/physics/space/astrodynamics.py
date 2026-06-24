import math
from astronomy_types import (
    Distance,
    Eccentricity,
    EquatorialCoordinates,
    GravitationalParameter,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVectors,
    Vector3D,
    Velocity,
    VelocityVector,
    Inclination,
    Latitude,
    Degrees,
    MeanMotion,
)
from afmaths.constants import (
    EARTH_MU_KM_CUBED,
    EARTH_RADIUS_KM,
    BurnDirection,
    DeltaV,
)
from afmaths.geometry.geometry import (
    eccentricity_factor_plus,
    semi_major_axis_from_vertex_distances,
)
from afmaths.operation import (
    HALF,
    add,
    divide_by,
    multiply,
    negate,
    square_root,
    subtract,
)
from afmaths.physics.space.type_conversion_helpers import (
    position_vector_to_vector3d,
    velocity_vector_to_vector3d,
)
from afmaths.physics.space.celestial_mechanics import (
    angular_momentum,
    nadir_vector,
    orbit_radius,
    orbital_elements_from_state_vectors,
    orbital_period,
    periapsis_radius,
    periapsis_velocity,
    radial_velocity,
    velocity_difference,
    velocity_at_altitude,
    vis_viva,
    zenith_vector,
)
from afmaths.tensors import (
    vector_magnitude,
    vector_negate,
    vector_normalise,
)

# def trajectory_propagation(
#     state: StateVectors, perturbations: list[Vector3D]
# ) -> StateVectors:

#     position = []

#     for p in perturbations:
#         propagate_vector_3d(
#             Coordinate3D(state.position.x, state.position.y, state.position.z), p
#         )


def flight_path_angle(
    state: StateVectors, mu: GravitationalParameter = EARTH_MU_KM_CUBED
) -> Radians:
    elements = orbital_elements_from_state_vectors(state)

    return Radians(
        Scalar(
            math.acos(
                divide_by(
                    multiply(
                        vector_magnitude(position_vector_to_vector3d(state.position))
                    )(vector_magnitude(velocity_vector_to_vector3d(state.velocity)))
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


def signed_flight_path_angle(state: StateVectors) -> Radians:
    r = vector_magnitude(position_vector_to_vector3d(state.position))
    v = vector_magnitude(velocity_vector_to_vector3d(state.velocity))

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
    return divide_by(sidereal_period)(multiply(2)(math.pi))


# region Directions


def radial(position: PositionVector) -> Vector3D:
    return zenith_vector(position)


def anti_radial(position: PositionVector) -> Vector3D:
    return nadir_vector(position)


def prograde(velocity: VelocityVector) -> Vector3D:
    return vector_normalise(velocity)


def retrograde(velocity: VelocityVector) -> Vector3D:
    return vector_negate(prograde(velocity))


def normal(state: StateVectors) -> Vector3D:
    return vector_normalise(angular_momentum(state))


def anti_normal(state: StateVectors) -> Vector3D:
    return vector_negate(normal(state))


def burn_direction_at_apsis(
    initial_altitude: Distance, target_altitude: Distance
) -> BurnDirection:
    if initial_altitude > target_altitude:
        return BurnDirection.RETROGRADE
    return BurnDirection.PROGRADE


# endregion directions

# region Maneuvers


def increase_semi_major_axis_at_periapsis(
    a: SemiMajorAxis,
    current_altitude: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        velocity_at_altitude(current_altitude, mu),
        vis_viva(mu, current_altitude, a),
    )


def increase_semi_major_axis_at_apoapsis(
    a: SemiMajorAxis,
    current_altitude: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        vis_viva(mu, current_altitude, a),
        velocity_at_altitude(current_altitude, mu),
    )


def decrease_semi_major_axis_at_periapsis(
    a: SemiMajorAxis,
    current_altitude: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        vis_viva(mu, current_altitude, a),
        velocity_at_altitude(current_altitude, mu),
    )


def decrease_semi_major_axis_at_apoapsis(
    a: SemiMajorAxis,
    current_altitude: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        velocity_at_altitude(current_altitude, mu),
        vis_viva(mu, current_altitude, a),
    )


def hohmann_transfer(
    initial_altitude_km: Distance,
    target_altitude_km: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, DeltaV, BurnDirection, Second]:
    """Calculates the delta-v required for a Hohmann transfer. Assumes a circular initial and final orbit."""
    # www.braeunig.us/space/problem.htm#4.19

    r_a = orbit_radius(initial_altitude_km, initial_body_radius)
    r_b = orbit_radius(target_altitude_km, initial_body_radius)

    semi_major_axis_transfer_ellipse = semi_major_axis_from_vertex_distances(r_a, r_b)

    direction = burn_direction_at_apsis(initial_altitude_km, target_altitude_km)
    transfer_delta_v = (
        increase_semi_major_axis_at_periapsis(
            semi_major_axis_transfer_ellipse, r_a, gravitational_parameter
        )
        if direction is BurnDirection.PROGRADE
        else decrease_semi_major_axis_at_apoapsis(
            semi_major_axis_transfer_ellipse, r_b, gravitational_parameter
        )
    )

    circularise = (
        increase_semi_major_axis_at_apoapsis(
            semi_major_axis_transfer_ellipse, r_b, gravitational_parameter
        )
        if direction is BurnDirection.PROGRADE
        else decrease_semi_major_axis_at_periapsis(
            semi_major_axis_transfer_ellipse, r_a, gravitational_parameter
        )
    )

    total = DeltaV(add(transfer_delta_v)(circularise))

    period = transfer_period(
        gravitational_parameter,
        initial_altitude_km,
        target_altitude_km,
        initial_body_radius,
    )

    return (
        total,
        transfer_delta_v,
        circularise,
        burn_direction_at_apsis(initial_altitude_km, target_altitude_km),
        period,
    )


def transfer_period(
    mu: GravitationalParameter,
    initial_altitude_km: Distance,
    target_altitude_km: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
) -> Second:
    """Assuming an elliptical transfer orbit."""
    r_a = orbit_radius(initial_altitude_km, initial_body_radius)
    r_b = orbit_radius(target_altitude_km, initial_body_radius)

    semi_major_axis_transfer_ellipse = semi_major_axis_from_vertex_distances(r_a, r_b)
    return HALF(orbital_period(semi_major_axis_transfer_ellipse, mu))


def transfer_semi_major_axis(
    initial_altitude_km: Distance, final_altitude_km: Distance
) -> SemiMajorAxis:
    return divide_by(2)(add(initial_altitude_km)(final_altitude_km))


def transfer_eccentricity(
    initial_altitude_km: Distance, final_altitude_km: Distance
) -> Eccentricity:
    return divide_by(add(final_altitude_km)(initial_altitude_km))(
        subtract(initial_altitude_km)(final_altitude_km)
    )


def inclination_change_at_node(
    velocity_at_node: Velocity,
    current_inclination: Inclination,
    target_inclination: Inclination,
) -> DeltaV:
    difference = abs(subtract(target_inclination)(current_inclination))
    return DeltaV(
        Velocity(
            Scalar(multiply(multiply(2)(velocity_at_node))(math.sin(HALF(difference))))
        )
    )


def parabolic_escape(elements: OrbitalElements, mu: GravitationalParameter) -> DeltaV:
    velocity_at_periapsis = periapsis_velocity(mu, elements)
    parabolic_escape_velocity = Velocity(
        Scalar(
            square_root(
                divide_by(
                    periapsis_radius(elements.semi_major_axis, elements.eccentricity)
                )(multiply(2)(mu))
            )
        )
    )

    return velocity_difference(velocity_at_periapsis, parabolic_escape_velocity)


# TODO: function(s) to change specific orbital elements

# endregion

# region Ground Track


def max_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(math.degrees(i)))


def min_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(negate(math.degrees(i))))


def westward_drift(mean_motion: MeanMotion) -> Degrees:
    return Degrees(Scalar(multiply(360)(divide_by(mean_motion)(1))))


def westware_drift_from_angular_velocity_and_period(
    body_angular_velocity: Radians, orbital_period: Second
) -> Radians:
    return multiply(body_angular_velocity)(orbital_period)


# endregion


if __name__ == "__main__":

    # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)
    print(hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000))))

    position = PositionVector(
        Position(Scalar(7000)), Position(Scalar(0.1)), Position(Scalar(0.1))
    )

    velocity = VelocityVector(
        Velocity(Scalar(0.1)), Velocity(Scalar(7.5)), Velocity(Scalar(0.1))
    )

    print(f"Radial      : {radial(position)}")
    print(f"Anti-radial : {anti_radial(position)}")
    print(f"Zenith      : {zenith_vector(position)}")
    print(f"Nadir       : {nadir_vector(position)}")
    print(f"Prograde    : {prograde(velocity)}")
    print(f"Retrograde  : {retrograde(velocity)}")
    print(f"Normal      : {normal(StateVectors(position, velocity))}")
    print(f"Anti-normal : {anti_normal(StateVectors(position, velocity))}")
    print(
        f"Flight path angle (deg): {math.degrees(flight_path_angle(StateVectors(position, velocity)))}"
    )
    print(
        f"Flight path angle (deg): {math.degrees(signed_flight_path_angle(StateVectors(position, velocity)))}"
    )
    print(
        f"Flight path angle (deg): {math.degrees(flight_path_angle_from_elements(orbital_elements_from_state_vectors(StateVectors(position, velocity))))}"
    )
