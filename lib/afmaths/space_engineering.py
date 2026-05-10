from math import atan
import math

from .geometry import semi_major_axis_from_axes
from .operation import (
    CUBE,
    SQUARE,
    add,
    divide,
    dot_product_3d,
    exponentiate,
    multiply,
    square_root,
    subtract,
    vector_cross_multiplication_3d,
    vector_magnitude_3d,
    vector_multiplication_3d,
)
from astronomy_types import (
    GravitationalParameter,
    Latitude,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    RightAscension,
    Inclination,
    ArgumentOfPerigee,
    SemiMajorAxis,
    Eccentricity,
    StateVectors,
    TrueAnomaly,
    Scalar,
    Ratio,
    Vector3D,
    Velocity,
    VelocityVector,
    degrees_to_radians,
    Degrees,
    Distance,
)

EARTH_MU_KM_CUBED = GravitationalParameter(Scalar(398600.5))  # km^3 / s^2
EARTH_RADIUS_KM = Distance(Scalar(6378.0))  # km


def orbit_radius(
    altitude: Distance, initial_body_radius: Distance = EARTH_RADIUS_KM
) -> Distance:
    return add(altitude)(initial_body_radius)


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
                    subtract(divide(semi_major_axis)(1))(divide(orbit_radius)(2))
                )
            )
        )
    )


def velocity_for_altitude(
    orbit_radius: Distance,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> Velocity:
    return Velocity(Scalar(square_root(divide(orbit_radius)(gravitational_parameter))))


def velocity_difference(
    initial_velocity: Velocity, final_velocity: Velocity
) -> Velocity:
    return subtract(initial_velocity)(final_velocity)


def hohmann_transfer(
    initial_altitude_km: Distance,
    target_altitude_km: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[float, float, float]:
    """Calculates the delta-v required for a Hohmann transfer"""
    # www.braeunig.us/space/problem.htm#4.19

    r_a = orbit_radius(initial_altitude_km, initial_body_radius)
    r_b = orbit_radius(target_altitude_km, initial_body_radius)

    semi_major_axis_transfer_ellipse = semi_major_axis_from_axes(r_a, r_b)
    initial_velocity = velocity_for_altitude(r_a, gravitational_parameter)
    final_velocity = velocity_for_altitude(r_b, gravitational_parameter)
    velocity_on_orbit_at_initial_orbit = vis_viva(
        gravitational_parameter, r_a, semi_major_axis_transfer_ellipse
    )
    velocity_on_orbit_at_final_orbit = vis_viva(
        gravitational_parameter, r_b, semi_major_axis_transfer_ellipse
    )
    initial_velocity_change = velocity_difference(
        initial_velocity, Velocity(Scalar(velocity_on_orbit_at_initial_orbit))
    )
    final_velocity_change = velocity_difference(
        velocity_on_orbit_at_final_orbit, final_velocity
    )
    delta_v = add(initial_velocity_change)(final_velocity_change)
    return (delta_v, initial_velocity_change, final_velocity_change)


def inclination_from_angular_momentum_vector(
    angular_momentum_vector: Vector3D,
) -> Inclination:
    """Calculates the inclination of an orbit from the angular momentum vector"""

    # # First formulation
    # i1 = np.arctan2(np.sqrt(np.square(h[0]) + np.square(h[1])), h[2])
    # # Second formulation
    # i2 = np.arccos(h[2] / np.linalg.norm(h))

    x = SQUARE(angular_momentum_vector.x)
    y = SQUARE(angular_momentum_vector.y)
    numerator = square_root(add(x)(y))
    denominator = angular_momentum_vector.z
    return Inclination(Radians(Scalar(atan(divide(denominator)(numerator)))))


def right_ascension_of_ascending_node_from_angular_momentum_vector(
    angular_momentum_vector: Vector3D,
) -> RightAscension:
    """Calculates the right ascension of ascending node of an orbit from the angular momentum vector.

    This relates the orbital plane to the celestial sphere.
    """

    # # But it's better to use arctan2 which handles the quadrants for you
    # Omega = np.arctan2(h[0], -h[1])
    # # Note: equivalent to np.arctan(h[0] / -h[1]) + np.pi

    return RightAscension(
        Radians(
            add(
                math.atan(divide(-angular_momentum_vector.y)(angular_momentum_vector.x))
            )(math.pi)
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

    position_vector = state_vectors.position
    velocity_vector = state_vectors.velocity

    r = vector_magnitude_3d(
        Vector3D(position_vector.x, position_vector.y, position_vector.z)
    )
    v = vector_magnitude_3d(
        Vector3D(velocity_vector.x, velocity_vector.y, velocity_vector.z)
    )
    # This is a rearranged vis-viva equation
    a = subtract(divide(gravitational_parameter)(SQUARE(v)))(divide(r)(2))
    return SemiMajorAxis(exponentiate(-1)(a))


def eccentricity_from_ellipse_equation(
    angular_momentum_vector: Vector3D[Scalar],
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> Eccentricity:
    """Calculates the eccentricity of an orbit from the angular momentum vector"""
    # p = np.square(h_norm) / mu
    # e = np.sqrt(1 - p / a)
    # e
    h = vector_magnitude_3d(angular_momentum_vector)
    denominator = multiply(gravitational_parameter)(semi_major_axis)
    division = divide(denominator)(SQUARE(h))
    return Eccentricity(Ratio(Scalar(square_root(subtract(division)(1)))))


def mean_motion(
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> float:
    """Calculates the mean motion of an orbit from the semi major axis in radians per second"""
    # n = np.sqrt(mu / np.power(a, 3))
    return square_root(divide(CUBE(semi_major_axis))(gravitational_parameter))


def mean_anomaly(E_rad: float, eccentricity: Eccentricity) -> float:
    # M = E - e * np.sin(E)
    return subtract(multiply(eccentricity)(math.sin(E_rad)))(E_rad)


def mean_anomaly_at_time_offset(
    mean_anomaly: float, time_offset_s: float, mean_motion: float
) -> float:
    """Calculates the mean anomaly at a given time offset from the current mean anomaly"""
    return add(mean_anomaly)(multiply(mean_motion)(time_offset_s))


def eccentric_anomaly(
    position_vector: PositionVector,
    velocity_vector: VelocityVector,
    semi_major_axis: SemiMajorAxis,
    mean_motion: float,
) -> Radians:
    # E = np.arctan2(np.dot(r, v) / (np.square(a) * n), 1 - r_norm / a)
    r = vector_magnitude_3d(
        Vector3D(position_vector.x, position_vector.y, position_vector.z)
    )
    r_dot_v = dot_product_3d(
        Vector3D(position_vector.x, position_vector.y, position_vector.z),
        Vector3D(velocity_vector.x, velocity_vector.y, velocity_vector.z),
    )

    y = r_dot_v
    x = SQUARE(semi_major_axis) * mean_motion * (1 - r / semi_major_axis)

    return Radians(Scalar(math.atan2(y, x) % (2 * math.pi)))


def eccentric_anomaly_from_true_anomaly(
    true_anomaly: float, eccentricity: Eccentricity
) -> float:
    return 2 * math.atan2(
        math.sqrt(1 - eccentricity) * math.sin(true_anomaly / 2),
        math.sqrt(1 + eccentricity) * math.cos(true_anomaly / 2),
    )


def eccentric_anomaly_solved(
    iteration_func,
    eccentricity: Eccentricity,
    mean_anomaly: float,
    tol=1e-6,
    max_iter=100,
) -> tuple[Radians, list]:
    history = []

    E_i = mean_anomaly
    delta_E = float("inf")

    i = 0
    history.append((i, E_i, math.degrees(E_i), None))

    while i < max_iter and abs(delta_E) > tol:
        E_next = iteration_func(E_i, eccentricity, mean_anomaly)
        delta_E = E_next - E_i
        i += 1

        history.append((i, E_next, math.degrees(E_next), delta_E))
        E_i = E_next

    return Radians(Scalar(E_i)), history


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
    E_rad: Radians, eccentricity: Eccentricity
) -> TrueAnomaly:
    # theta = np.arctan2(np.sqrt(1 - np.square(e)) * np.sin(E), np.cos(E) - e)
    sin_E = math.sin(E_rad)
    cos_E = math.cos(E_rad)

    sqrt_term = square_root(subtract(SQUARE(eccentricity))(1))

    y = multiply(sqrt_term)(sin_E)  # √(1 - e²) * sin(E)
    x = subtract(eccentricity)(cos_E)

    theta = math.atan(y / x)

    if x > 0:
        if y < 0:
            theta += 2 * math.pi
    elif x < 0:
        theta += math.pi
    else:  # x == 0
        if y > 0:
            theta = math.pi / 2
        elif y < 0:
            theta = 3 * math.pi / 2
        else:
            theta = 0

    return TrueAnomaly(Radians(Scalar(theta)))


def true_anomaly_from_mean_anomaly(
    eccentricity: Eccentricity, mean_anomaly: float
) -> TrueAnomaly:
    eccentric_anomaly, _ = eccentric_anomaly_solved(
        newton_iteration, eccentricity, mean_anomaly
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
    numerator = divide(math.sin(inclination))(position_vector.z)
    second_term = add(
        multiply(position_vector.x)(math.cos(right_ascension_of_ascending_node))
    )(multiply(position_vector.y)(math.sin(right_ascension_of_ascending_node)))

    x = numerator
    y = second_term
    u = atan(divide(second_term)(numerator))

    # Account for the correct quadrant of the latitude
    if x > 0:
        if y < 0:
            u += 2 * math.pi
    elif x < 0:
        u += math.pi
    else:  # x == 0
        if y > 0:
            u = math.pi / 2
        elif y < 0:
            u = 3 * math.pi / 2
        else:
            u = 0

    return Latitude(Radians(Scalar(u)))


def orbital_elements_from_state_vectors(
    state_vectors: StateVectors,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> OrbitalElements:
    """Calculates the orbital elements of an orbit from the state vectors (position and velocity)"""
    # From TUB MSE SFM Exercise 2 solution
    position_vector = state_vectors.position
    velocity_vector = state_vectors.velocity

    angular_momentum_vector = vector_cross_multiplication_3d(
        position_vector, velocity_vector
    )

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
    eccentric_an = eccentric_anomaly(
        position_vector, velocity_vector, semi_major_axis, n
    )
    true_anomaly = true_anomaly_from_eccentric_anomaly(eccentric_an, eccentricity)
    latitude = argument_of_latitude(raan, inclination, position_vector)
    argument_of_perigee = subtract(true_anomaly)(latitude)

    return OrbitalElements(
        inclination=inclination,
        right_ascension_of_ascending_node=raan,
        argument_of_perigee=argument_of_perigee,
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        true_anomaly=true_anomaly,
    )


def newton_iteration(E_i: float, eccentricity: Eccentricity, mean_anomaly: float):
    # E_i - (E_i - e * np.sin(E_i) - M) / (1 - e * np.cos(E_i))
    return E_i - (E_i - eccentricity * math.sin(E_i) - mean_anomaly) / (
        1 - eccentricity * math.cos(E_i)
    )


def perifocal_position_vector(
    radius: Distance, true_anomaly: TrueAnomaly
) -> Vector3D[Scalar]:
    """Calculates the position vector in the perifocal coordinate system"""
    return vector_multiplication_3d(
        Vector3D(
            Scalar(math.cos(true_anomaly)), Scalar(math.sin(true_anomaly)), Scalar(0)
        ),
        radius,
    )


def perifocal_velocity_vector(
    true_anomaly: float,
    eccentricity: Eccentricity,
    gravitational_parameter: GravitationalParameter,
    semi_major_axis: SemiMajorAxis,
) -> Vector3D[Scalar]:
    """Calculates the velocity vector in the perifocal coordinate system"""
    return vector_multiplication_3d(
        Vector3D(
            Scalar(-math.sin(true_anomaly)),
            Scalar(add(eccentricity)(math.cos(true_anomaly))),
            Scalar(0),
        ),
        square_root(
            divide(multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1)))(
                gravitational_parameter
            )
        ),
    )


def radius_at_true_anomaly(
    semi_major_axis: SemiMajorAxis,
    eccentricity: Eccentricity,
    true_anomaly: TrueAnomaly,
) -> Distance:
    """Calculates the radius of an orbit at a given true anomaly"""
    return divide(add(1)(multiply(eccentricity)(math.cos(true_anomaly))))(
        multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1))
    )


def eci_matrix_from_perifocal(
    inclination: Inclination,
    right_ascension_of_ascening_node: RightAscension,
    argument_of_perigee: ArgumentOfPerigee,
) -> Vector3D[Vector3D[Scalar]]:
    p = [
        math.cos(argument_of_perigee) * math.cos(right_ascension_of_ascening_node)
        - math.sin(argument_of_perigee)
        * math.cos(inclination)
        * math.sin(right_ascension_of_ascening_node),
        math.cos(argument_of_perigee) * math.sin(right_ascension_of_ascening_node)
        + math.sin(argument_of_perigee)
        * math.cos(inclination)
        * math.cos(right_ascension_of_ascening_node),
        math.sin(argument_of_perigee) * math.sin(inclination),
    ]

    q = [
        -math.sin(argument_of_perigee) * math.cos(right_ascension_of_ascening_node)
        - math.cos(argument_of_perigee)
        * math.cos(inclination)
        * math.sin(right_ascension_of_ascening_node),
        -math.sin(argument_of_perigee) * math.sin(right_ascension_of_ascening_node)
        + math.cos(argument_of_perigee)
        * math.cos(inclination)
        * math.cos(right_ascension_of_ascening_node),
        math.cos(argument_of_perigee) * math.sin(inclination),
    ]

    w = [
        math.sin(inclination) * math.sin(right_ascension_of_ascening_node),
        -math.sin(inclination) * math.cos(right_ascension_of_ascening_node),
        math.cos(inclination),
    ]

    return Vector3D(
        Vector3D(Scalar(p[0]), Scalar(q[0]), Scalar(w[0])),
        Vector3D(Scalar(p[1]), Scalar(q[1]), Scalar(w[1])),
        Vector3D(Scalar(p[2]), Scalar(q[2]), Scalar(w[2])),
    )


def transform_perifocal_to_eci(
    transposed_PQW: Vector3D[Vector3D[Scalar]],
    perifocal_vector: Vector3D[Scalar],
) -> Vector3D[Scalar]:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    return Vector3D(
        dot_product_3d(transposed_PQW.x, perifocal_vector),
        dot_product_3d(transposed_PQW.y, perifocal_vector),
        dot_product_3d(transposed_PQW.z, perifocal_vector),
    )


def true_anomaly_at_time_offset(
    eccentricity: Eccentricity,
    mean_anomaly: float,
    time_offset_s: float,
    mean_motion_n: float,
) -> TrueAnomaly:

    mean_anomaly_at_offset = mean_anomaly_at_time_offset(
        mean_anomaly, time_offset_s, mean_motion_n
    )

    # eccentric_anomaly_at_offset, _ = eccentric_anomaly_solved(
    #     newton_iteration, eccentricity, mean_anomaly_at_offset
    # )
    # return true_anomaly_from_eccentric_anomaly(
    #     eccentric_anomaly_at_offset, eccentricity
    # )

    return true_anomaly_from_mean_anomaly(eccentricity, mean_anomaly_at_offset)


def orbit_state_vector_prediction_from_orbital_elements(
    orbital_elements_radians: OrbitalElements,
    time_offset_s: float,
    initial_mean_anomaly_radians: float | None = None,  # Shortcut
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> StateVectors:
    """Calculates the state vectors (position and velocity) of an orbit from the orbital elements at a given time offset from the current position in the orbit"""
    semi_major_axis = orbital_elements_radians.semi_major_axis
    eccentricity = orbital_elements_radians.eccentricity

    if initial_mean_anomaly_radians is None:
        initial_mean_anomaly_radians = mean_anomaly(
            eccentric_anomaly_from_true_anomaly(
                orbital_elements_radians.true_anomaly, eccentricity
            ),
            eccentricity,
        )

    true_anomaly_at_offset = true_anomaly_at_time_offset(
        eccentricity,
        initial_mean_anomaly_radians,
        time_offset_s,
        mean_motion(orbital_elements_radians.semi_major_axis, gravitational_parameter),
    )

    radius_at_offset = radius_at_true_anomaly(
        semi_major_axis, eccentricity, true_anomaly_at_offset
    )

    perifocal_position = perifocal_position_vector(
        radius_at_offset, true_anomaly_at_offset
    )

    perifocal_velocity = perifocal_velocity_vector(
        true_anomaly_at_offset, eccentricity, gravitational_parameter, semi_major_axis
    )

    eci_matrix = eci_matrix_from_perifocal(
        orbital_elements_radians.inclination,
        orbital_elements_radians.right_ascension_of_ascending_node,
        orbital_elements_radians.argument_of_perigee,
    )

    position_vector = transform_perifocal_to_eci(eci_matrix, perifocal_position)

    velocity_vector = transform_perifocal_to_eci(eci_matrix, perifocal_velocity)

    return StateVectors(
        PositionVector(
            Position(position_vector.x),
            Position(position_vector.y),
            Position(position_vector.z),
        ),
        VelocityVector(
            Velocity(velocity_vector.x),
            Velocity(velocity_vector.y),
            Velocity(velocity_vector.z),
        ),
    )


# TODO: FST 1 equations
# TODO: Increment of velocity

if __name__ == "__main__":
    # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)
    print(hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000))))

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

    # {'position_vector': [-1753.131769017119, 1070.9950241554125, -6564.0676605044755], 'velocity_vector': [-3.478980009547892, 6.473396036204375, 1.986162313733967]}
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPerigee(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Radians(Scalar(2.8022276030554347))),
            ),
            1800,
            None,
        )
    )

    # StateVectors(position=Vector3D(x=10000.000000000027, y=39999.999999999985, z=-5000.0), velocity=Vector3D(x=-1.4999999999999996, y=1.0000000000000016, z=-0.1000000000000002))
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            orbital_elements_from_state_vectors(
                StateVectors(
                    PositionVector(
                        Position(Scalar(10000)),
                        Position(Scalar(40000)),
                        Position(Scalar(-5000)),
                    ),
                    VelocityVector(
                        Velocity(Scalar(-1.5)),
                        Velocity(Scalar(1)),
                        Velocity(Scalar(-0.1)),
                    ),
                )
            ),
            0,
        )
    )
