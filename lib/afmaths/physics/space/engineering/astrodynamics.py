from dataclasses import replace
import math
from astronomy_types import (
    Distance,
    EccentricAnomaly,
    Eccentricity,
    EquatorialCoordinates,
    GravitationalParameter,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    Ratio,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVector,
    TrueAnomaly,
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
    DOUBLE,
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
    apoapsis_radius,
    eccentric_anomaly_from_true_anomaly,
    eccentricity_from_apsides,
    kepler_equation,
    nadir_vector,
    orbit_altitude,
    orbit_radius,
    orbital_elements_from_state_vectors,
    orbital_period,
    periapsis_radius,
    periapsis_velocity,
    radial_velocity,
    semi_major_axis_from_period,
    time_since_periapsis,
    velocity_difference,
    velocity_at_radius,
    vis_viva,
    zenith_vector,
)
from afmaths.tensors import (
    vector_magnitude,
    vector_negate,
    vector_normalise,
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


def signed_flight_path_angle(state: StateVector) -> Radians:
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
    return divide_by(sidereal_period)(DOUBLE(math.pi))


# region Directions


def radial(position: PositionVector) -> Vector3D:
    return zenith_vector(position)


def anti_radial(position: PositionVector) -> Vector3D:
    return nadir_vector(position)


def prograde(velocity: VelocityVector) -> Vector3D:
    return vector_normalise(velocity)


def retrograde(velocity: VelocityVector) -> Vector3D:
    return vector_negate(prograde(velocity))


def normal(state: StateVector) -> Vector3D:
    return vector_normalise(angular_momentum(state))


def anti_normal(state: StateVector) -> Vector3D:
    return vector_negate(normal(state))


def burn_direction_at_apsis(initial: Distance, target: Distance) -> BurnDirection:
    if initial > target:
        return BurnDirection.RETROGRADE
    return BurnDirection.PROGRADE


# endregion directions

# region Maneuvers

# TODO: function(s) to change specific orbital elements


def increase_semi_major_axis_at_periapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        velocity_at_radius(current_radius, mu),
        vis_viva(mu, current_radius, a),
    )


def increase_semi_major_axis_at_apoapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        vis_viva(mu, current_radius, a),
        velocity_at_radius(current_radius, mu),
    )


def decrease_semi_major_axis_at_periapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        vis_viva(mu, current_radius, a),
        velocity_at_radius(current_radius, mu),
    )


def decrease_semi_major_axis_at_apoapsis(
    a: SemiMajorAxis,
    current_radius: Distance,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> DeltaV:
    return velocity_difference(
        velocity_at_radius(current_radius, mu),
        vis_viva(mu, current_radius, a),
    )


def hohmann_transfer_from_orbital_elements(
    initial_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, DeltaV, BurnDirection, Second]:
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
) -> tuple[DeltaV, DeltaV, DeltaV, BurnDirection, Second]:
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
        if direction is BurnDirection.PROGRADE
        else decrease_semi_major_axis_at_apoapsis(
            semi_major_axis_transfer_ellipse, target_radius, mu
        )
    )

    circularise = (
        increase_semi_major_axis_at_apoapsis(
            semi_major_axis_transfer_ellipse, target_radius, mu
        )
        if direction is BurnDirection.PROGRADE
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


def inclination_change_at_node(
    velocity_at_node: Velocity,
    current_inclination: Inclination,
    target_inclination: Inclination,
) -> DeltaV:
    difference = abs(subtract(target_inclination)(current_inclination))
    return DeltaV(
        Velocity(Scalar(multiply(DOUBLE(velocity_at_node))(math.sin(HALF(difference)))))
    )


def hohmann_transfer(
    initial_altitude: Distance,
    target_altitude: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, DeltaV, BurnDirection, Second]:
    """Calculates the delta-v required for a Hohmann transfer. Assumes a circular initial and final orbit."""
    # www.braeunig.us/space/problem.htm#4.19

    return hohmann_transfer_from_radii(
        orbit_radius(initial_altitude, initial_body_radius),
        orbit_radius(target_altitude, initial_body_radius),
        mu,
    )


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

    return velocity_difference(velocity_at_periapsis, parabolic_escape_velocity)


# region Transfer Orbit


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


# region ## Phase Orbit


def phase_angle_time(
    E_phase_orbit: EccentricAnomaly,
    original_orbit: OrbitalElements,
    mu: GravitationalParameter,
) -> Second:
    return time_since_periapsis(
        original_orbit.semi_major_axis,
        mu,
        kepler_equation(E_phase_orbit, original_orbit.eccentricity),
    )


def phase_period(original_period: Second, phase_angle_time: Second) -> Second:
    """
    Return the phase orbit period.

    Positive phase_angle_time means move ahead, so the phase period is shorter.
    Negative phase_angle_time means fall behind, so the phase period is longer.
    """
    return subtract(phase_angle_time)(original_period)


def phase_semi_major_axis(
    original_orbit: OrbitalElements,
    true_anomaly_delta: TrueAnomaly,
    mu: GravitationalParameter,
) -> SemiMajorAxis:
    return semi_major_axis_from_period(
        phase_period(
            orbital_period(original_orbit.semi_major_axis, mu),
            phase_angle_time(
                eccentric_anomaly_from_true_anomaly(
                    true_anomaly_delta,
                    original_orbit.eccentricity,
                ),
                original_orbit,
                mu,
            ),
        ),
        mu,
    )


def phase_apsides(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> tuple[Distance, Distance]:
    """Return phase orbit periapsis and apoapsis."""
    two_a = DOUBLE(phase_semi_major_axis)

    if phase_semi_major_axis > original_orbit.semi_major_axis:
        # Higher / longer-period phase orbit:
        # original periapsis is shared with phase periapsis.
        periapsis = periapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )
        apoapsis = subtract(periapsis)(two_a)  # 2a - rp
    else:
        # Lower / shorter-period phase orbit:
        # original apoapsis is shared with phase apoapsis.
        apoapsis = apoapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )
        periapsis = subtract(apoapsis)(two_a)  # 2a - ra

    return periapsis, apoapsis


def phase_periapsis(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    periapsis, _ = phase_apsides(phase_semi_major_axis, original_orbit)
    return periapsis


def phase_apoapsis(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    _, apoapsis = phase_apsides(phase_semi_major_axis, original_orbit)
    return apoapsis


def phase_eccentricity(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Eccentricity:

    periapsis, apoapsis = phase_apsides(phase_semi_major_axis, original_orbit)

    return Eccentricity(
        Ratio(Scalar(abs(eccentricity_from_apsides(periapsis, apoapsis))))
    )


def phase_poi_radius(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    """Returns the Point of Impulse (POI), which is either the apoapsis or periapsis of the original orbit."""
    if phase_semi_major_axis > original_orbit.semi_major_axis:
        return periapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )

    return apoapsis_radius(
        original_orbit.semi_major_axis,
        original_orbit.eccentricity,
    )


def phase_delta_v(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
    mu: GravitationalParameter,
) -> DeltaV:
    poi = phase_poi_radius(phase_semi_major_axis, original_orbit)

    original_velocity = vis_viva(
        mu,
        poi,
        original_orbit.semi_major_axis,
    )

    phase_velocity = vis_viva(
        mu,
        poi,
        phase_semi_major_axis,
    )

    return velocity_difference(original_velocity, phase_velocity)


def phase_orbit(
    original_orbit: OrbitalElements,
    true_anomaly_delta: TrueAnomaly,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, OrbitalElements]:
    """Returns the Point of Impulse (POI) DeltaV, total DeltaV, and phase orbital elements."""

    p_a = phase_semi_major_axis(original_orbit, true_anomaly_delta, mu)

    # This is the delta v to get from one orbit to the other, so half of the total required.
    poi_delta_v = phase_delta_v(p_a, original_orbit, mu)

    return (
        poi_delta_v,  # DeltaV to move orbit
        DOUBLE(poi_delta_v),  # Total DeltaV
        replace(
            original_orbit,
            semi_major_axis=p_a,
            eccentricity=phase_eccentricity(p_a, original_orbit),
        ),
    )


# endregion

# region Ground Track


def max_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(math.degrees(i)))


def min_latitude(i: Inclination) -> Latitude:
    return Degrees(Scalar(negate(math.degrees(i))))


def westward_drift(n: MeanMotion) -> Degrees:
    return Degrees(Scalar(multiply(360)(divide_by(n)(1))))


def westware_drift_from_angular_velocity_and_period(
    body_angular_velocity: Radians, orbital_period: Second
) -> Radians:
    return multiply(body_angular_velocity)(orbital_period)


# endregion
