from dataclasses import replace
import math

from afmaths.physics.space.astronomy.type_conversion_helpers import (
    degrees_to_radians,
    position_vector_to_vector3d,
    velocity_vector_to_vector3d,
)
from afmaths.physics.space.astronomy.coordinate_conversion import (
    eci_rotation_matrix_from_orbital_elements,
    transform_perifocal_to_earth_centred_inertial,
    vector_from_coordinates,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_cross_multiplication_3d,
    vector_magnitude_3d,
)

from afmaths.geometry import calculate_semi_minor_axis, semi_major_axis_from_axes
from afmaths.operation import (
    CUBE,
    SQUARE,
    add,
    divide,
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
    Coordinate2D,
    Coordinate3D,
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
    SemiMinorAxis,
    StateVectors,
    TrueAnomaly,
    Scalar,
    Ratio,
    Vector3D,
    Velocity,
    VelocityVector,
    Degrees,
    Distance,
)

EARTH_MU_KM_CUBED = GravitationalParameter(Scalar(398600.5))  # km^3 / s^2
EARTH_RADIUS_KM = Distance(Scalar(6378.0))  # km


def orbit_radius(
    altitude: Distance, initial_body_radius: Distance = EARTH_RADIUS_KM
) -> Distance:
    return add(altitude)(initial_body_radius)


def orbital_period(a: SemiMajorAxis, g: GravitationalParameter) -> Second:
    return multiply(2)(multiply(math.pi)(square_root(divide(g)(CUBE(a)))))


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
    h = vector_magnitude_3d(angular_momentum_vector)

    p = semi_latus_rectum_from_angular_momentum(
        h,
        gravitational_parameter,
    )

    return Eccentricity(
        Ratio(Scalar(square_root(subtract(divide(semi_major_axis)(p))(1))))
    )


def mean_motion(
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> MeanMotion:
    """Calculates the mean motion of an orbit from the semi major axis in radians per second"""
    # n = np.sqrt(mu / np.power(a, 3))
    return MeanMotion(
        Rate(
            Scalar(square_root(divide(CUBE(semi_major_axis))(gravitational_parameter)))
        )
    )


def kepler_equation(E_rad: EccentricAnomaly, eccentricity: Eccentricity) -> MeanAnomaly:
    """Kepler equation."""
    # M = E - e * np.sin(E)
    return subtract(multiply(eccentricity)(math.sin(E_rad)))(E_rad)


def mean_anomaly_at_time_offset(
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
    radius = vector_magnitude_3d(
        Vector3D(state.position.x, state.position.y, state.position.z)
    )

    y = dot_product_3d(
        Vector3D(state.position.x, state.position.y, state.position.z),
        Vector3D(state.velocity.x, state.velocity.y, state.velocity.z),
    )
    x = multiply(SQUARE(semi_major_axis))(
        multiply(mean_motion)((subtract(divide(semi_major_axis)(radius))(1)))
    )

    return EccentricAnomaly(Anomaly(Radians(Scalar(math.atan2(y, x) % (2 * math.pi)))))


def eccentric_anomaly_from_true_anomaly(
    true_anomaly: TrueAnomaly, eccentricity: Eccentricity
) -> EccentricAnomaly:
    return EccentricAnomaly(
        Anomaly(
            Radians(
                Scalar(
                    multiply(2)(
                        math.atan2(
                            math.sqrt(1 - eccentricity) * math.sin(true_anomaly / 2),
                            math.sqrt(1 + eccentricity) * math.cos(true_anomaly / 2),
                        )
                    )
                )
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

    return EccentricAnomaly(Anomaly(Radians(Scalar(E_i)))), history


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

    return TrueAnomaly(Anomaly(Radians(Scalar(theta))))


def true_anomaly_from_mean_anomaly(
    eccentricity: Eccentricity, mean_anomaly: MeanAnomaly
) -> TrueAnomaly:
    eccentric_anomaly, _ = eccentric_anomaly_solved(
        newtons_method, eccentricity, mean_anomaly
    )

    return true_anomaly_from_eccentric_anomaly(eccentric_anomaly, eccentricity)


def true_anomaly_at_time_offset(
    eccentricity: Eccentricity,
    mean_anomaly: MeanAnomaly,
    time_offset_s: Second,
    mean_motion_n: MeanMotion,
) -> TrueAnomaly:
    return true_anomaly_from_mean_anomaly(
        eccentricity,
        mean_anomaly_at_time_offset(mean_anomaly, time_offset_s, mean_motion_n),
    )


def argument_of_latitude(
    right_ascension_of_ascending_node: RightAscension,
    inclination: Inclination,
    position_vector: PositionVector,
) -> Latitude:
    # u = np.arctan2(r[2] / np.sin(i), r[0] * np.cos(Omega) + r[1] * np.sin(Omega))
    # if u < 0:
    #     u += 2 * np.pi
    y = divide(math.sin(inclination))(position_vector.z)
    x = add(multiply(position_vector.x)(math.cos(right_ascension_of_ascending_node)))(
        multiply(position_vector.y)(math.sin(right_ascension_of_ascending_node))
    )

    return Latitude(Radians(Scalar(math.atan2(y, x) % (2 * math.pi))))


def orbital_elements_from_state_vectors(
    state_vectors: StateVectors,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> OrbitalElements:
    """Calculates the orbital elements of an orbit from the state vectors (position and velocity)"""
    # From TUB MSE SFM Exercise 2 solution

    angular_momentum_vector = vector_cross_multiplication_3d(
        state_vectors.position, state_vectors.velocity
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
    eccentric_an = eccentric_anomaly(state_vectors, semi_major_axis, n)
    true_anomaly = true_anomaly_from_eccentric_anomaly(eccentric_an, eccentricity)
    latitude = argument_of_latitude(raan, inclination, state_vectors.position)
    argument_of_perigee = subtract(true_anomaly)(latitude)

    return OrbitalElements(
        inclination=inclination,
        right_ascension_of_ascending_node=raan,
        argument_of_perigee=argument_of_perigee,
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
    return EccentricAnomaly(
        Anomaly(
            Radians(
                Scalar(
                    newtons_raphson_method(
                        E_i_guess,
                        subtract(mean_anomaly)(
                            kepler_equation(E_i_guess, eccentricity)
                        ),
                        subtract(multiply(eccentricity)(math.cos(E_i_guess)))(1),
                    )
                )
            )
        )
    )


def perifocal_position_vector(
    radius: Distance, true_anomaly: TrueAnomaly
) -> PositionVector:
    """Calculates the position vector in the perifocal coordinate system"""
    vector = vector_from_coordinates(
        Coordinate3D(
            x=Scalar(math.cos(true_anomaly)),
            y=Scalar(math.sin(true_anomaly)),
            z=Scalar(0),
        ),
        radius,
    )
    return PositionVector(Position(vector.x), Position(vector.y), Position(vector.z))


def perifocal_velocity_vector(
    true_anomaly: TrueAnomaly,
    eccentricity: Eccentricity,
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter,
) -> VelocityVector:
    """Calculates the velocity vector in the perifocal coordinate system"""
    vector = vector_from_coordinates(
        Coordinate3D(
            Scalar(-math.sin(true_anomaly)),
            Scalar(add(eccentricity)(math.cos(true_anomaly))),
            Scalar(0),
        ),
        Scalar(
            square_root(
                divide(multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1)))(
                    gravitational_parameter
                )
            )
        ),
    )

    return VelocityVector(Velocity(vector.x), Velocity(vector.y), Velocity(vector.z))


def semi_latus_rectum(a: SemiMajorAxis, e: Eccentricity) -> SemiLatusRectum:
    return multiply(a)(subtract(SQUARE(e))(1))


def semi_latus_rectum_from_angular_momentum(
    angular_momentum_magnitude: Scalar,
    gravitational_parameter: GravitationalParameter,
) -> SemiLatusRectum:
    return divide(gravitational_parameter)(SQUARE(angular_momentum_magnitude))


def orbit_equation(
    semi_major_axis: SemiMajorAxis,
    eccentricity: Eccentricity,
    true_anomaly: TrueAnomaly,
) -> Distance:
    # Trajectory equation: r = p / (1 + e * cos(theta))
    # Kepler's first law: r = a * (1 - e^2) / (1 + e * cos(theta))
    """Calculates the radius of an orbit at a given true anomaly"""
    return divide(add(1)(multiply(eccentricity)(math.cos(true_anomaly))))(
        semi_latus_rectum(semi_major_axis, eccentricity)
    )


def orbit_state_vector_prediction_from_orbital_elements(
    orbital_elements: OrbitalElements,
    time_offset_s: Second = Second(Scalar(0)),
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> StateVectors:
    """Calculates the state vectors (position and velocity) of an orbit from the orbital elements at a given time offset from the current position in the orbit"""

    initial_mean_anomaly = kepler_equation(
        eccentric_anomaly_from_true_anomaly(
            orbital_elements.true_anomaly, orbital_elements.eccentricity
        ),
        orbital_elements.eccentricity,
    )

    true_anomaly_at_offset = true_anomaly_at_time_offset(
        orbital_elements.eccentricity,
        initial_mean_anomaly,
        time_offset_s,
        mean_motion(orbital_elements.semi_major_axis, gravitational_parameter),
    )

    radius_at_offset = orbit_equation(
        orbital_elements.semi_major_axis,
        orbital_elements.eccentricity,
        true_anomaly_at_offset,
    )

    perifocal_position = perifocal_position_vector(
        radius_at_offset, true_anomaly_at_offset
    )

    perifocal_velocity = perifocal_velocity_vector(
        true_anomaly_at_offset,
        orbital_elements.eccentricity,
        orbital_elements.semi_major_axis,
        gravitational_parameter,
    )

    eci_rotation_matrix = eci_rotation_matrix_from_orbital_elements(orbital_elements)

    position_vector = transform_perifocal_to_earth_centred_inertial(
        eci_rotation_matrix,
        position_vector_to_vector3d(perifocal_position),
    )

    velocity_vector = transform_perifocal_to_earth_centred_inertial(
        eci_rotation_matrix, velocity_vector_to_vector3d(perifocal_velocity)
    )

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


def generate_angles_on_circle(resolution: int) -> list[Radians]:
    typed = []
    for val in interval(0, 2 * math.pi, resolution):
        typed.append(Radians(Scalar(val)))

    return typed


def generate_all_orbit_positions(
    orbital_elements: OrbitalElements,
    resolution: int,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> list[PositionVector]:
    if resolution < 5:
        raise ValueError("Resolution must be greater than 5.")
    position_list = []
    for true_anomaly in generate_angles_on_circle(resolution):
        position_list.append(
            orbit_state_vector_prediction_from_orbital_elements(
                replace(
                    orbital_elements,
                    true_anomaly=true_anomaly,
                ),
                gravitational_parameter=gravitational_parameter,
            ).position
        )
    return position_list


def coordinate_from_eccentric_anomaly(
    semi_major_axis: SemiMajorAxis,
    semi_minor_axis: SemiMinorAxis,
    eccentric_anomaly: EccentricAnomaly,
) -> Coordinate2D:
    return Coordinate2D(
        x=multiply(semi_major_axis)(math.cos(eccentric_anomaly)),
        y=multiply(semi_minor_axis)(math.sin(eccentric_anomaly)),
    )


def orbit_coordinate_prediction(
    orbital_elements: OrbitalElements,
    target_time: Second,
) -> Coordinate2D:

    M = mean_anomaly_at_time_offset(
        kepler_equation(
            eccentric_anomaly_from_true_anomaly(
                TrueAnomaly(Anomaly(Radians(Scalar(0)))), orbital_elements.eccentricity
            ),
            orbital_elements.eccentricity,
        ),
        target_time,
        mean_motion(
            orbital_elements.semi_major_axis,
        ),
    )

    E, _ = eccentric_anomaly_solved(newtons_method, orbital_elements.eccentricity, M)

    return coordinate_from_eccentric_anomaly(
        orbital_elements.semi_major_axis,
        calculate_semi_minor_axis(
            orbital_elements.semi_major_axis,
            orbital_elements.eccentricity,
        ),
        E,
    )


def generate_relative_coordinate_from_eccentric_anomaly(
    reference_central_body: Coordinate2D,
    semi_major_axis: SemiMajorAxis,
    semi_minor_axis: SemiMinorAxis,
    eccentric_anomaly: EccentricAnomaly,
) -> Coordinate2D:

    relative = coordinate_from_eccentric_anomaly(
        semi_major_axis,
        semi_minor_axis,
        eccentric_anomaly,
    )

    return Coordinate2D(
        x=reference_central_body.x + relative.x,
        y=reference_central_body.y + relative.y,
    )


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

    # {'position_vector': [-1753.131769017119, 1070.9950241554125, -6564.0676605044755], 'velocity_vector': [-3.478980009547892, 6.473396036204375, 1.986162313733967]}
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPerigee(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1800)),
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
            )
        )
    )

    print(
        orbit_coordinate_prediction(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPerigee(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1000)),
        )
    )
