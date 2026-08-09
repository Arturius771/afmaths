from dataclasses import replace
import math
from typing import Callable

from afmaths.constants import (
    EARTH_MU,
    UNIT_VECTOR_XY_PLANE,
)
from afmaths.geometry.transformations import (
    ellipse_perimeter_coordinate_from_eccentric_anomaly,
)
from afmaths.physics.physics import centripetal_acceleration, centripetal_force
from afmaths.physics.space.transformations import (
    transform_vector_from_perifocal,
)
from afmaths.physics.space.type_conversion_helpers import (
    coordinate3d_from_vector,
    make_eccentric_anomaly,
    coordinate2d_from_vector,
    make_radians,
    position_from_vector,
    make_state_vector,
    make_true_anomaly,
    velocity_from_vector,
    vector3d_from_position,
    make_vector2d,
    make_vector3d,
    vector3d_from_velocity,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_cross_multiplication_3d,
    vector_magnitude_3d,
    vector_multiplication_2d,
    vector_multiplication_3d,
)

from afmaths.geometry.geometry import (
    eccentricity_factor_minus,
    eccentricity_factor_plus,
    eccentricity,
    normalise_angle,
    semi_minor_axis,
    semi_minor_axis_from_semi_latus_rectum,
)
from afmaths.operation import (
    DOUBLE,
    SQUARE,
    add,
    divide_by,
    exponentiate,
    interval_points,
    multiply,
    negate,
    newtons_raphson_method,
    ratio,
    square_root,
    subtract,
)
from astronomy_types import (
    Acceleration,
    Anomaly,
    Coordinate2D,
    Coordinate3D,
    EccentricAnomaly,
    GravitationalParameter,
    Latitude,
    MeanAnomaly,
    MeanMotion,
    OrbitalElements,
    PositionVector,
    Radians,
    Rate,
    RightAscension,
    Inclination,
    ArgumentOfPeriapsis,
    Second,
    SemiLatusRectum,
    SemiMajorAxis,
    Eccentricity,
    StateVector,
    TrueAnomaly,
    Scalar,
    Vector3D,
    Velocity,
    VelocityVector,
    Distance,
)

from afmaths.afmath_types import (
    AngularMomentum,
)


from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    angular_momentum,
    angular_momentum_magnitude,
    argument_of_latitude,
    kepler_equation,
    mean_motion,
    orbit_equation,
)


def orbital_elements_from_degrees(orbital_elements: OrbitalElements) -> OrbitalElements:
    return OrbitalElements(
        Inclination(Radians(Scalar(math.radians(orbital_elements.inclination)))),
        RightAscension(
            Radians(
                Scalar(math.radians(orbital_elements.right_ascension_of_ascending_node))
            )
        ),
        ArgumentOfPeriapsis(
            Radians(Scalar(math.radians(orbital_elements.argument_of_periapsis)))
        ),
        orbital_elements.semi_major_axis,
        orbital_elements.eccentricity,
        TrueAnomaly(
            Anomaly(Radians(Scalar(math.radians(orbital_elements.true_anomaly))))
        ),
    )


def orbital_elements_from_state_vectors(
    state_vectors: StateVector,
    mu: GravitationalParameter = EARTH_MU,
) -> OrbitalElements:
    """Calculates the orbital elements of an orbit from the state vectors (position and velocity)"""
    # From TUB MSE SFM Exercise 2 solution

    angular_momentum_vector = angular_momentum(state_vectors)

    inclination = inclination_from_angular_momentum_vector(angular_momentum_vector)
    raan = right_ascension_of_ascending_node_from_angular_momentum_vector(
        angular_momentum_vector
    )
    semi_major_axis = semi_major_axis_from_state_vectors(state_vectors, mu)
    eccentricity = eccentricity_from_ellipse_equation(
        angular_momentum_vector, semi_major_axis, mu
    )
    true_anomaly = true_anomaly_from_eccentric_anomaly(
        eccentric_anomaly(
            state_vectors,
            semi_major_axis,
            mean_motion(semi_major_axis, mu),
        ),
        eccentricity,
    )

    return OrbitalElements(
        inclination=inclination,
        right_ascension_of_ascending_node=raan,
        argument_of_periapsis=argument_of_periapsis(
            true_anomaly,
            argument_of_latitude(raan, inclination, state_vectors.position),
        ),
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        true_anomaly=true_anomaly,
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


def propagate_orbit_to_time_2d(
    orbital_elements: OrbitalElements,
    target_time: Second,
) -> Coordinate2D:

    M = mean_anomaly_at_time(
        kepler_equation(
            eccentric_anomaly_from_true_anomaly(
                make_true_anomaly(0), orbital_elements.eccentricity
            ),
            orbital_elements.eccentricity,
        ),
        target_time,
        mean_motion(
            orbital_elements.semi_major_axis,
        ),
    )

    E, _ = eccentric_anomaly_solved(
        newtons_method_eccentric_anomaly, orbital_elements.eccentricity, M
    )

    return ellipse_perimeter_coordinate_from_eccentric_anomaly(
        orbital_elements.semi_major_axis,
        semi_minor_axis(
            orbital_elements.semi_major_axis,
            orbital_elements.eccentricity,
        ),
        E,
    )


def position_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset: Second = Second(Scalar(0)),
    mu: GravitationalParameter = EARTH_MU,
) -> PositionVector:
    return state_vector_at_time(orbital_elements, time_offset, mu).position


def velocity_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset_s: Second = Second(Scalar(0)),
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> VelocityVector:
    return state_vector_at_time(
        orbital_elements, time_offset_s, gravitational_parameter
    ).velocity


def perifocal_radial_unit_vector(
    theta: TrueAnomaly,
) -> Vector3D[Scalar]:
    """Calculates the direction vector of an orbit in the perifocal coordinate system from the orbital elements.

    [cos(theta), sin(theta), 0] is the unit vector in the direction of the radius vector in the perifocal coordinate system.
    """
    # MSE SFM L02.
    return make_vector3d(
        Scalar(math.cos(theta)),
        Scalar(math.sin(theta)),
        Scalar(0),
    )


def perifocal_velocity_direction_vector(
    theta: TrueAnomaly,
    e: Eccentricity,
) -> Vector3D[Scalar]:
    """Calculates the direction vector of an orbit in the perifocal coordinate system from the orbital elements."""

    return make_vector3d(
        Scalar(negate(math.sin(theta))),
        Scalar(add(e)(math.cos(theta))),
        Scalar(0),
    )


def perifocal_position_coordinate_2d(
    orbital_elements: OrbitalElements,
) -> Coordinate2D[Scalar]:
    """Calculates the position coordinate of an orbit in the perifocal coordinate system from the orbital elements.

    This is a 2D coordinate in the orbital plane, with the origin at the focus of the ellipse (the central body).
    """
    pqw = perifocal_radial_unit_vector(orbital_elements.true_anomaly)

    return coordinate2d_from_vector(
        vector_multiplication_2d(
            make_vector2d(
                pqw.x,
                pqw.y,
            ),
            orbit_equation(
                orbital_elements.semi_major_axis,
                orbital_elements.eccentricity,
                orbital_elements.true_anomaly,
            ),
        )
    )


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


def oribtal_plane_position_at_true_anomaly(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    """Calculates the position vector of an orbit at a given true anomaly in the orbital plane reference frame."""
    return perifocal_position_vector(orbital_elements)


# region Argument of Periapsis


def argument_of_periapsis(
    theta: TrueAnomaly, latitude: Latitude
) -> ArgumentOfPeriapsis:
    return subtract(theta)(latitude)


# region Eccentricity


def eccentricity_from_ellipse_equation(
    angular_momentum_vector: AngularMomentum,
    a: SemiMajorAxis,
    mu: GravitationalParameter = EARTH_MU,
) -> Eccentricity:
    """Calculates the eccentricity of an orbit from the angular momentum vector and semi major axis"""

    return eccentricity(
        a,
        semi_minor_axis_from_semi_latus_rectum(
            semi_latus_rectum_from_angular_momentum(
                angular_momentum_vector,
                mu,
            ),
            a,
        ),
    )


def eccentricity_from_apsides(periapsis: Distance, apoapsis: Distance) -> Eccentricity:
    return divide_by(add(apoapsis)(periapsis))(subtract(periapsis)(apoapsis))


# region Inclination


def inclination_from_angular_momentum_vector(
    angular_momentum_vector: AngularMomentum,
) -> Inclination:
    """Calculates the inclination of an orbit from the angular momentum vector"""
    return Inclination(
        Radians(
            Scalar(
                math.atan2(
                    math.sqrt(
                        angular_momentum_vector.x * angular_momentum_vector.x
                        + angular_momentum_vector.y * angular_momentum_vector.y
                    ),
                    angular_momentum_vector.z,
                )
            )
        )
    )


# region Right Ascension of Ascending Node


def ascending_node_vector_from_angular_momentum_vector(
    angular_momentum_vector: AngularMomentum,
) -> Vector3D:
    """Calculates the vector pointing to the ascending node of an orbit from the angular momentum vector."""
    return vector_cross_multiplication_3d(
        UNIT_VECTOR_XY_PLANE,
        angular_momentum_vector,
    )


def right_ascension_of_ascending_node_from_angular_momentum_vector(
    angular_momentum_vector: AngularMomentum,
) -> RightAscension:
    """Calculates the right ascension of ascending node of an orbit from the angular momentum vector.

    This relates the orbital plane to the celestial sphere.
    """
    n = ascending_node_vector_from_angular_momentum_vector(angular_momentum_vector)

    divide_by_vector_magnitude = divide_by(vector_magnitude_3d(n))
    if n.y >= 0:
        return RightAscension(make_radians(math.acos(divide_by_vector_magnitude(n.x))))
    else:
        return RightAscension(
            make_radians(
                subtract(math.acos(divide_by_vector_magnitude(n.x)))(DOUBLE(math.pi))
            )
        )


# region Semi Major Axis


def semi_major_axis_from_state_vectors(
    state_vectors: StateVector,
    mu: GravitationalParameter = EARTH_MU,
) -> SemiMajorAxis:
    """Calculates the semi major axis of an orbit from the position and velocity vectors"""
    # r_norm = np.linalg.norm(r)
    # v_norm = np.linalg.norm(v)
    # print("Position norm: ", 1e-3 * r_norm, "Velocity norm: ", 1e-3 * v_norm)
    # a = 1 / (2 / r_norm - np.square(v_norm) / mu)
    # 1e-3 * a

    r = vector_magnitude_3d(vector3d_from_position(state_vectors.position))
    v = vector_magnitude_3d(vector3d_from_velocity(state_vectors.velocity))
    # This is a rearranged vis-viva equation
    a = subtract(divide_by(mu)(SQUARE(v)))(divide_by(r)(2))
    return SemiMajorAxis(exponentiate(-1)(a))


def semi_major_axis_from_period(
    orbital_period: Second, mu: GravitationalParameter = EARTH_MU
) -> SemiMajorAxis:
    return exponentiate(divide_by(3)(2))(
        divide_by(DOUBLE(math.pi))(multiply(square_root(mu))(orbital_period))
    )


# region True Anomaly


def true_anomaly_from_eccentric_anomaly(
    E_rad: EccentricAnomaly, e: Eccentricity
) -> TrueAnomaly:
    # theta = np.arctan2(np.sqrt(1 - np.square(e)) * np.sin(E), np.cos(E) - e)
    sin_E = math.sin(E_rad)
    cos_E = math.cos(E_rad)

    sqrt_term = square_root(eccentricity_factor_minus(SQUARE(e)))

    y = multiply(sqrt_term)(sin_E)  # √(1 - e²) * sin(E)
    x = subtract(e)(cos_E)

    theta = normalise_angle(make_radians(math.atan2(y, x)))

    return make_true_anomaly(theta)


def true_anomaly_at_inertial_angle(
    orbit: OrbitalElements,
    inertial_angle: Radians,
) -> TrueAnomaly:
    return make_true_anomaly(subtract(orbit.argument_of_periapsis)(inertial_angle))


def true_anomaly(eccentricity: Eccentricity, mean_anomaly: MeanAnomaly) -> TrueAnomaly:
    eccentric_anomaly, _ = eccentric_anomaly_solved(
        newtons_method_eccentric_anomaly, eccentricity, mean_anomaly
    )

    return true_anomaly_from_eccentric_anomaly(eccentric_anomaly, eccentricity)


def true_anomaly_at_time(
    eccentricity: Eccentricity,
    mean_anomaly: MeanAnomaly,
    time_offset: Second,
    mean_motion: MeanMotion,
) -> TrueAnomaly:
    return true_anomaly(
        eccentricity,
        mean_anomaly_at_time(mean_anomaly, time_offset, mean_motion),
    )


def periapsis_true_anomaly() -> TrueAnomaly:
    return make_true_anomaly(0)


def apoapsis_true_anomaly() -> TrueAnomaly:
    return make_true_anomaly(math.pi)


# region Eccentric Anomaly


def newtons_method_eccentric_anomaly(
    E_i_guess: EccentricAnomaly, e: Eccentricity, M: MeanAnomaly
) -> EccentricAnomaly:
    """Performs one iteration of Newton's method to solve Kepler's equation for the eccentric anomaly.

    Converges quckly if eccentricity is low.

    Kepler Equation: M = E - e * np.sin(E)

    Setting to find for 0, by subtracting M: (E_i - e * np.sin(E_i) - M).

    For an incorrect guess: E_i - e * sin(E_i) - M != 0

    Derivative: (1 - e * np.cos(E_i).

    This is used in iterative methods to find the root of the equation, which is the eccentric anomaly E that satisfies Kepler's equation for a given mean anomaly M and eccentricity e.
    """

    return make_eccentric_anomaly(
        newtons_raphson_method(
            # Initial guess
            E_i_guess,
            # (E_i - e * np.sin(E_i) - M)
            subtract(M)(kepler_equation(E_i_guess, e)),
            # (1 - e * np.cos(E_i)
            subtract(multiply(e)(math.cos(E_i_guess)))(1),
        )
    )


def eccentric_anomaly(
    state: StateVector,
    a: SemiMajorAxis,
    n: MeanMotion,
) -> EccentricAnomaly:
    # E = np.arctan2(np.dot(r, v) / (np.square(a) * n), 1 - r_norm / a)
    pos_3d = vector3d_from_position(state.position)
    radius = vector_magnitude_3d(pos_3d)

    y = dot_product_3d(
        pos_3d,
        vector3d_from_velocity(state.velocity),
    )
    x = multiply(SQUARE(a))(multiply(n)((subtract(divide_by(a)(radius))(1))))

    return make_eccentric_anomaly(normalise_angle(make_radians(math.atan2(y, x))))


def eccentric_anomaly_from_true_anomaly(
    theta: TrueAnomaly, e: Eccentricity
) -> EccentricAnomaly:
    return make_eccentric_anomaly(
        normalise_angle(
            DOUBLE(
                math.atan2(
                    math.sqrt(eccentricity_factor_minus(e)) * math.sin(theta / 2),
                    math.sqrt(eccentricity_factor_plus(e)) * math.cos(theta / 2),
                )
            )
        )
    )


def eccentric_anomaly_solved(
    iteration_function: Callable,
    e: Eccentricity,
    M: MeanAnomaly,
    tolerance=1e-6,
    max_iterations=100,
) -> tuple[EccentricAnomaly, list]:
    """Solves for Eccentric Anomaly by repeatedly applying the iteration_function until the delta between the guess and the next guess is basically 0."""

    history = []  # TODO: make this more structured

    E_i = EccentricAnomaly(M)
    delta_E = float(
        "inf"
    )  # When this delta is 0 or close to it, we have arrived at the answer

    iteration = 0
    history.append((iteration, E_i, math.degrees(E_i), None))

    while iteration < max_iterations and abs(delta_E) > tolerance:
        # Find the next guess for E
        E_next = iteration_function(E_i, e, M)

        # Calculate the delta between the first and next guess
        delta_E = E_next - E_i

        # Track iterations
        iteration += 1

        # Update history
        history.append((iteration, E_next, math.degrees(E_next), delta_E))

        # Set the next guess
        E_i = E_next

    # Return an answer once the loop is broken
    return make_eccentric_anomaly(E_i), history


def eccentric_anomaly_at_time(
    orbital_elements: OrbitalElements,
    time_seconds: Second,
    g: GravitationalParameter = EARTH_MU,
) -> EccentricAnomaly:

    initial_mean_anomaly = kepler_equation(
        eccentric_anomaly_from_true_anomaly(
            orbital_elements.true_anomaly, orbital_elements.eccentricity
        ),
        orbital_elements.eccentricity,
    )

    return eccentric_anomaly_from_true_anomaly(
        true_anomaly_at_time(
            orbital_elements.eccentricity,
            initial_mean_anomaly,
            time_seconds,
            mean_motion(orbital_elements.semi_major_axis, g),
        ),
        orbital_elements.eccentricity,
    )


# region Semi Latus Rectum


def semi_latus_rectum_from_angular_momentum(
    angular_momentum: AngularMomentum,
    mu: GravitationalParameter,
) -> SemiLatusRectum:
    return divide_by(mu)(SQUARE(angular_momentum_magnitude(angular_momentum)))


# region Mean Anomaly


def mean_anomaly_at_time(
    M: MeanAnomaly, time_offset: Second, n: MeanMotion
) -> MeanAnomaly:
    """Calculates the mean anomaly at a given time offset from the current mean motion and mean anomaly"""
    return add(M)(multiply(n)(time_offset))


# endregion
