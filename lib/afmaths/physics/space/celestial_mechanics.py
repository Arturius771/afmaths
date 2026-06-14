from dataclasses import replace
import math

from afmaths.constants import (
    EARTH_MU_KM_CUBED,
    EARTH_RADIUS_KM,
    GRAVITATIONAL_CONSTANT,
    DeltaV,
    Mass,
)
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    make_eccentric_anomaly,
    make_true_anomaly,
    position_vector_to_vector3d,
    velocity_vector_to_vector3d,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_cross_multiplication_3d,
    vector_magnitude,
)

from afmaths.geometry import (
    eccentricity_factor_minus,
    eccentricity_factor_plus,
    eccentricity,
    semi_minor_axis_from_semi_latus_rectum,
)
from afmaths.operation import (
    CUBE,
    HALF,
    SQUARE,
    add,
    divide_by,
    exponentiate,
    interval,
    multiply,
    newtons_raphson_method,
    ratio,
    square_root,
    subtract,
)
from astronomy_types import (
    Anomaly,
    EccentricAnomaly,
    GravitationalParameter,
    Latitude,
    MeanAnomaly,
    MeanMotion,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    Rate,
    RightAscension,
    Inclination,
    ArgumentOfPerigee,
    Second,
    SemiLatusRectum,
    SemiMajorAxis,
    Eccentricity,
    StateVectors,
    TrueAnomaly,
    Scalar,
    Vector3D,
    Velocity,
    VelocityVector,
    Distance,
)


def gravitational_parameter(
    mass1: Mass, mass2: Mass = Mass(0)
) -> GravitationalParameter:
    """
    Calculates the graviational parameter (Mu) of two objects in m^3/s^2

    :param mass1: The first bodies mass
    :type mass1: float
    :param mass2: The second bodies mass
    :type mass2: float
    :return: Mu = G * (mass1 + mass2)
    :rtype: Mass
    """
    return multiply(GRAVITATIONAL_CONSTANT)(add(mass1)(mass2))


def univesal_gravitation(
    mass1: Scalar, mass2: Scalar, distance_metres: Distance
) -> float:
    """
    Calculate the strength of the gravitational "force" between two objects.

    :param mass1: The first object's mass
    :type mass1: float
    :param mass2: The second object's mass
    :type mass2: float
    :param distance_metres: The distance between the two objects
    :type distance_metres: float
    :return: Description
    :rtype: float
    """
    return multiply(GRAVITATIONAL_CONSTANT)(
        multiply(mass1)(mass2) / SQUARE(distance_metres)
    )


def gravitational_acceleration(mu: GravitationalParameter, radius: Distance) -> Scalar:
    return divide_by(SQUARE(radius))(mu)


def gravity_at_altitude(
    altitude: Distance,
    initial_body_radius: Distance,
    mu: GravitationalParameter,
) -> Scalar:
    # From MSE SFM Exercise 1
    return gravitational_acceleration(
        mu,
        orbit_radius(altitude, initial_body_radius),
    )


def mean_angular_rate(
    semi_major_axis: SemiMajorAxis, gravitational_parameter: GravitationalParameter
) -> Rate:
    # From MSE SFM Exercise 1
    return Rate(
        Scalar(square_root(divide_by(CUBE(semi_major_axis))(gravitational_parameter)))
    )


def angular_momentum(state_vectors: StateVectors) -> Vector3D[Scalar]:
    # From MSE SFM Exercise 2
    return vector_cross_multiplication_3d(
        state_vectors.position, state_vectors.velocity
    )


def angular_momentum_magnitude(angular_momentum_vector: Vector3D[Scalar]) -> Scalar:
    # From MSE SFM Exercise 1
    return vector_magnitude(angular_momentum_vector)


def instantaneous_angular_velocity(state_vectors: StateVectors) -> Scalar:
    # From MSE SFM Exercise 1
    h = angular_momentum_magnitude(angular_momentum(state_vectors))
    r = vector_magnitude(position_vector_to_vector3d(state_vectors.position))

    return divide_by(SQUARE(r))(h)


def swept_area_of_ellipse(
    angular_momentum: Scalar, time_since_periapsis: Second
) -> Scalar:
    # From MSE SFM Exercise 1
    return multiply(HALF(angular_momentum))(time_since_periapsis)


def orbit_radius(
    altitude: Distance, initial_body_radius: Distance = EARTH_RADIUS_KM
) -> Distance:
    return add(altitude)(initial_body_radius)


def orbital_period(a: SemiMajorAxis, g: GravitationalParameter) -> Second:
    return multiply(2)(multiply(math.pi)(square_root(divide_by(g)(CUBE(a)))))


def time_since_periapsis(
    a: SemiMajorAxis, g: GravitationalParameter, mean_anomaly: MeanAnomaly
) -> Second:
    return Second(
        Scalar(
            multiply(orbital_period(a, g))(
                ratio(float(mean_anomaly))(multiply(math.pi)(2))
            )
        )
    )


def vis_viva(
    gravitational_parameter: GravitationalParameter,
    orbit_radius: Distance,
    semi_major_axis: SemiMajorAxis,
) -> Velocity:
    """Calculates the velocity of an object in an elliptical orbit using the vis-viva equation."""
    return Velocity(
        Scalar(
            square_root(
                multiply(gravitational_parameter)(
                    subtract(divide_by(semi_major_axis)(1))(divide_by(orbit_radius)(2))
                )
            )
        )
    )


def velocity_for_altitude(
    orbit_radius: Distance,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> Velocity:
    return Velocity(
        Scalar(square_root(divide_by(orbit_radius)(gravitational_parameter)))
    )


def velocity_difference(initial_velocity: Velocity, final_velocity: Velocity) -> DeltaV:
    return subtract(initial_velocity)(final_velocity)


def inclination_from_angular_momentum_vector(
    angular_momentum_vector: Vector3D,
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


def radial_velocity(state: StateVectors) -> Velocity:
    position = position_vector_to_vector3d(state.position)

    return Velocity(
        divide_by(vector_magnitude(position))(
            dot_product_3d(position, velocity_vector_to_vector3d(state.velocity))
        )
    )


def right_ascension_of_ascending_node_from_angular_momentum_vector(
    angular_momentum_vector: Vector3D,
) -> RightAscension:
    """Calculates the right ascension of ascending node of an orbit from the angular momentum vector.

    This relates the orbital plane to the celestial sphere.
    """
    return RightAscension(
        Radians(
            Scalar(
                math.atan2(angular_momentum_vector.x, -angular_momentum_vector.y)
                % (2 * math.pi)
            )
        )
    )


def semi_major_axis_from_state_vectors(
    state_vectors: StateVectors,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> SemiMajorAxis:
    """Calculates the semi major axis of an orbit from the position and velocity vectors"""
    # r_norm = np.linalg.norm(r)
    # v_norm = np.linalg.norm(v)
    # print("Position norm: ", 1e-3 * r_norm, "Velocity norm: ", 1e-3 * v_norm)
    # a = 1 / (2 / r_norm - np.square(v_norm) / mu)
    # 1e-3 * a

    r = vector_magnitude(position_vector_to_vector3d(state_vectors.position))
    v = vector_magnitude(velocity_vector_to_vector3d(state_vectors.velocity))
    # This is a rearranged vis-viva equation
    a = subtract(divide_by(gravitational_parameter)(SQUARE(v)))(divide_by(r)(2))
    return SemiMajorAxis(exponentiate(-1)(a))


def eccentricity_from_ellipse_equation(
    angular_momentum_vector: Vector3D[Scalar],
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> Eccentricity:
    h = angular_momentum_magnitude(angular_momentum_vector)

    p = semi_latus_rectum_from_angular_momentum(
        h,
        gravitational_parameter,
    )

    b = semi_minor_axis_from_semi_latus_rectum(p, semi_major_axis)

    return eccentricity(semi_major_axis, b)


def mean_motion(
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> MeanMotion:
    """Calculates the mean motion of an orbit from the semi major axis in radians per second"""
    # n = np.sqrt(mu / np.power(a, 3))
    return MeanMotion((mean_angular_rate(semi_major_axis, gravitational_parameter)))


def kepler_equation(E_rad: EccentricAnomaly, eccentricity: Eccentricity) -> MeanAnomaly:
    """Kepler equation."""
    # M = E - e * np.sin(E)
    return subtract(multiply(eccentricity)(math.sin(E_rad)))(E_rad)


def mean_anomaly_at_time(
    mean_anomaly: MeanAnomaly, time_offset_s: Second, mean_motion: MeanMotion
) -> MeanAnomaly:
    """Calculates the mean anomaly at a given time offset from the current mean motion and mean anomaly"""
    return add(mean_anomaly)(multiply(mean_motion)(time_offset_s))


def eccentric_anomaly(
    state: StateVectors,
    semi_major_axis: SemiMajorAxis,
    mean_motion: MeanMotion,
) -> EccentricAnomaly:
    # E = np.arctan2(np.dot(r, v) / (np.square(a) * n), 1 - r_norm / a)
    pos_3d = position_vector_to_vector3d(state.position)
    radius = vector_magnitude(pos_3d)

    y = dot_product_3d(
        pos_3d,
        velocity_vector_to_vector3d(state.velocity),
    )
    x = multiply(SQUARE(semi_major_axis))(
        multiply(mean_motion)((subtract(divide_by(semi_major_axis)(radius))(1)))
    )

    return make_eccentric_anomaly(math.atan2(y, x) % (2 * math.pi))


def eccentric_anomaly_from_true_anomaly(
    theta: TrueAnomaly, e: Eccentricity
) -> EccentricAnomaly:
    return make_eccentric_anomaly(
        multiply(2)(
            math.atan2(
                math.sqrt(eccentricity_factor_minus(e)) * math.sin(theta / 2),
                math.sqrt(eccentricity_factor_plus(e)) * math.cos(theta / 2),
            )
        )
    )


def eccentric_anomaly_solved(
    iteration_func,
    eccentricity: Eccentricity,
    mean_anomaly: MeanAnomaly,
    tolerance=1e-6,
    max_iterations=100,
) -> tuple[EccentricAnomaly, list]:
    history = []  # TODO: make this more structured

    E_i = EccentricAnomaly(mean_anomaly)
    delta_E = float("inf")

    iteration = 0
    history.append((iteration, E_i, math.degrees(E_i), None))

    while iteration < max_iterations and abs(delta_E) > tolerance:
        E_next = iteration_func(E_i, eccentricity, mean_anomaly)
        delta_E = E_next - E_i
        iteration += 1

        history.append((iteration, E_next, math.degrees(E_next), delta_E))
        E_i = E_next

    return make_eccentric_anomaly(E_i), history


## Check if this belongs in geometry.py
# def true_anomaly_from_eccentric_anomaly(
#     eccentric_anomaly: float, eccentricity: Eccentricity
# ) -> TrueAnomaly:
#     """
#     Calculate the true anomaly from the eccentric anomaly and eccentricity.

#     Parameters:
#     E (float): The eccentric anomaly in radians.
#     e (float): The eccentricity of the orbit (0 <= eccentricity < 1).

#     Returns:
#     float: The true anomaly in radians.
#     """
#     if eccentricity < 0 or eccentricity >= 1:
#         raise ValueError("Eccentricity must be in the range [0, 1).")

#     return TrueAnomaly(
#         Radians(
#             Scalar(
#                 2
#                 * math.atan2(
#                     math.sqrt(1 + eccentricity) * math.sin(eccentric_anomaly / 2),
#                     math.sqrt(1 - eccentricity) * math.cos(eccentric_anomaly / 2),
#                 )
#             )
#         )
#     )


def true_anomaly_from_eccentric_anomaly(
    E_rad: EccentricAnomaly, eccentricity: Eccentricity
) -> TrueAnomaly:
    # theta = np.arctan2(np.sqrt(1 - np.square(e)) * np.sin(E), np.cos(E) - e)
    sin_E = math.sin(E_rad)
    cos_E = math.cos(E_rad)

    sqrt_term = square_root(eccentricity_factor_minus(SQUARE(eccentricity)))

    y = multiply(sqrt_term)(sin_E)  # √(1 - e²) * sin(E)
    x = subtract(eccentricity)(cos_E)

    theta = math.atan2(y, x) % (2 * math.pi)

    return make_true_anomaly(theta)


# TODO: define what we mean by angle more clearly
def true_anomaly_at_angle(
    orbit: OrbitalElements,
    inertial_angle: Radians,
) -> TrueAnomaly:
    return make_true_anomaly(subtract(orbit.argument_of_periapsis)(inertial_angle))


def true_anomaly(eccentricity: Eccentricity, mean_anomaly: MeanAnomaly) -> TrueAnomaly:
    eccentric_anomaly, _ = eccentric_anomaly_solved(
        newtons_method, eccentricity, mean_anomaly
    )

    return true_anomaly_from_eccentric_anomaly(eccentric_anomaly, eccentricity)


def argument_of_latitude(
    right_ascension_of_ascending_node: RightAscension,
    inclination: Inclination,
    position_vector: PositionVector,
) -> Latitude:
    # u = np.arctan2(r[2] / np.sin(i), r[0] * np.cos(Omega) + r[1] * np.sin(Omega))
    # if u < 0:
    #     u += 2 * np.pi
    y = divide_by(math.sin(inclination))(position_vector.z)
    x = add(multiply(position_vector.x)(math.cos(right_ascension_of_ascending_node)))(
        multiply(position_vector.y)(math.sin(right_ascension_of_ascending_node))
    )

    return Latitude(Radians(Scalar(math.atan2(y, x) % (2 * math.pi))))


def argument_of_periapsis(theta: TrueAnomaly, latitude: Latitude) -> ArgumentOfPerigee:
    return subtract(theta)(latitude)


def orbital_elements_from_state_vectors(
    state_vectors: StateVectors,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> OrbitalElements:
    """Calculates the orbital elements of an orbit from the state vectors (position and velocity)"""
    # From TUB MSE SFM Exercise 2 solution

    angular_momentum_vector = angular_momentum(state_vectors)

    inclination = inclination_from_angular_momentum_vector(angular_momentum_vector)
    raan = right_ascension_of_ascending_node_from_angular_momentum_vector(
        angular_momentum_vector
    )
    semi_major_axis = semi_major_axis_from_state_vectors(
        state_vectors, gravitational_parameter
    )
    eccentricity = eccentricity_from_ellipse_equation(
        angular_momentum_vector, semi_major_axis, gravitational_parameter
    )
    n = mean_motion(semi_major_axis, gravitational_parameter)
    eccentric_an = eccentric_anomaly(state_vectors, semi_major_axis, n)
    true_anomaly = true_anomaly_from_eccentric_anomaly(eccentric_an, eccentricity)
    latitude = argument_of_latitude(raan, inclination, state_vectors.position)
    argument_of_perigee = argument_of_periapsis(true_anomaly, latitude)

    return OrbitalElements(
        inclination=inclination,
        right_ascension_of_ascending_node=raan,
        argument_of_periapsis=argument_of_perigee,
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        true_anomaly=true_anomaly,
    )


def newtons_method(
    E_i_guess: EccentricAnomaly, eccentricity: Eccentricity, mean_anomaly: MeanAnomaly
) -> EccentricAnomaly:
    """Performs one iteration of Newton's method to solve Kepler's equation for the eccentric anomaly.

    Converges quckly if eccentricity is low."""
    # E_i - (E_i - e * np.sin(E_i) - M) / (1 - e * np.cos(E_i))
    # E_i - (E_i - eccentricity * math.sin(E_i) - mean_anomaly)
    # M = E - e * np.sin(E)
    return make_eccentric_anomaly(
        newtons_raphson_method(
            E_i_guess,
            subtract(mean_anomaly)(kepler_equation(E_i_guess, eccentricity)),
            subtract(multiply(eccentricity)(math.cos(E_i_guess)))(1),
        )
    )


def semi_latus_rectum(a: SemiMajorAxis, e: Eccentricity) -> SemiLatusRectum:
    return multiply(a)(eccentricity_factor_minus(SQUARE(e)))


def semi_latus_rectum_from_angular_momentum(
    angular_momentum_magnitude: Scalar,
    gravitational_parameter: GravitationalParameter,
) -> SemiLatusRectum:
    return divide_by(gravitational_parameter)(SQUARE(angular_momentum_magnitude))


def orbit_equation(
    semi_major_axis: SemiMajorAxis,
    eccentricity: Eccentricity,
    true_anomaly: TrueAnomaly,
) -> Distance:
    # Trajectory equation: r = p / (1 + e * cos(theta))
    # Kepler's first law: r = a * (1 - e^2) / (1 + e * cos(theta))
    """Calculates the instantaneos radius of an orbit at a given true anomaly"""
    return divide_by(
        eccentricity_factor_plus(multiply(eccentricity)(math.cos(true_anomaly)))
    )(semi_latus_rectum(semi_major_axis, eccentricity))


def periapsis_radius(a: SemiMajorAxis, e: Eccentricity) -> Distance:
    return multiply(a)(eccentricity_factor_minus(e))


def apoapsis_radius(a: SemiMajorAxis, e: Eccentricity) -> Distance:
    return multiply(a)(eccentricity_factor_plus(e))


# TODO: FST 1 equations
# TODO: Increment of velocity

if __name__ == "__main__":

    # {'inclination': 0.12166217595729033, 'right_ascension': 3.024483909022929, 'argument_of_perigee': 1.5978995641224425, 'semi_major_axis': 25015.186690979368, 'eccentricity': 0.7079768603248032, 'true_anomaly': 2.987554518980773}
    print(
        orbital_elements_from_state_vectors(
            StateVectors(
                PositionVector(
                    Position(Scalar(10000)),
                    Position(Scalar(40000)),
                    Position(Scalar(-5000)),
                ),
                VelocityVector(
                    Velocity(Scalar(-1.5)), Velocity(Scalar(1)), Velocity(Scalar(-0.1))
                ),
            )
        )
    )
