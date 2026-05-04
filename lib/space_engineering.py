from dataclasses import dataclass
from math import atan
import math

from geometry import semi_major_axis_from_axes
from operation import (
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


@dataclass
class OrbitalElements:
    inclination: float  # radians
    right_ascension: float  # radians
    argument_of_perigee: float  # radians
    semi_major_axis: float  # km
    eccentricity: float
    true_anomaly: float  # radians


def orbit_radius(altitude: float, initial_body_radius: int = 6378000) -> float:
    return add(altitude)(initial_body_radius)


def vis_viva(
    gravitational_parameter: float, orbit_radius: float, semi_major_axis: float
) -> float:
    """Calculates the velocity of an object in an elliptical orbit using the vis-viva equation."""
    return square_root(
        multiply(gravitational_parameter)(
            subtract(divide(semi_major_axis)(1))(divide(orbit_radius)(2))
        )
    )


def velocity_for_altitude(
    orbit_radius: float, gravitational_parameter: float = 3.986005e14
) -> float:
    return square_root(divide(orbit_radius)(gravitational_parameter))


def velocity_difference(initial_velocity: float, final_velocity: float) -> float:
    return subtract(initial_velocity)(final_velocity)


def hohmann_transfer(
    initial_altitude_metres: int,
    target_altitude_metres: int,
    initial_body_radius: int = 6378000,
    gravitational_parameter: float = 3.986005e14,
    result_in_km: bool = True,
) -> tuple[float, float, float]:
    """Calculates the delta-v required for a Hohmann transfer"""
    # www.braeunig.us/space/problem.htm#4.19

    r_a = orbit_radius(initial_altitude_metres, initial_body_radius)
    r_b = orbit_radius(target_altitude_metres, initial_body_radius)

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
        initial_velocity, velocity_on_orbit_at_initial_orbit
    )
    final_velocity_change = velocity_difference(
        velocity_on_orbit_at_final_orbit, final_velocity
    )
    delta_v = add(initial_velocity_change)(final_velocity_change)

    divide_by_thousand = divide(1000)

    if result_in_km:
        delta_v = divide_by_thousand(delta_v)
        initial_velocity_change = divide_by_thousand(initial_velocity_change)
        final_velocity_change = divide_by_thousand(final_velocity_change)
    return (delta_v, initial_velocity_change, final_velocity_change)


def inclination_from_angular_momentum_vector(
    angular_momentum_vector: list[float],
) -> float:
    """Calculates the inclination of an orbit from the angular momentum vector"""
    x = SQUARE(angular_momentum_vector[0])
    y = SQUARE(angular_momentum_vector[1])
    numerator = square_root(add(x)(y))
    denominator = angular_momentum_vector[2]
    return atan(divide(denominator)(numerator))


def right_ascension_from_angular_momentum_vector(
    angular_momentum_vector: list[float],
) -> float:
    """Calculates the right ascension of an orbit from the angular momentum vector"""
    return add(atan(divide(-angular_momentum_vector[1])(angular_momentum_vector[0])))(
        math.pi
    )


def semi_major_axis_from_position_and_velocity(
    position_vector: list[float],
    velocity_vector: list[float],
    gravitational_parameter: float = 3.986005e14,
) -> float:
    """Calculates the semi major axis of an orbit from the position and velocity vectors"""
    r = vector_magnitude_3d(position_vector)
    v = vector_magnitude_3d(velocity_vector)
    # This is a rearranged vis-viva equation
    a = subtract(divide(gravitational_parameter)(SQUARE(v)))(divide(r)(2))
    return exponentiate(-1)(a)


def eccentricity_from_angular_momentum_vector(
    angular_momentum_vector: list[float],
    semi_major_axis: float,
    gravitational_parameter: float = 398600,
) -> float:
    """Calculates the eccentricity of an orbit from the angular momentum vector"""
    h = vector_magnitude_3d(angular_momentum_vector)
    denominator = multiply(gravitational_parameter)(semi_major_axis)
    division = divide(denominator)(SQUARE(h))
    return square_root(subtract(division)(1))


def mean_motion_from_semi_major_axis(
    semi_major_axis: float, gravitational_parameter: float = 398600
) -> float:
    """Calculates the mean motion of an orbit from the semi major axis in radians per second"""
    return square_root(divide(CUBE(semi_major_axis))(gravitational_parameter))


def mean_anomaly_from_eccentric_anomaly(E_rad: float, eccentricity: float) -> float:
    return subtract(multiply(eccentricity)(math.sin(E_rad)))(E_rad)


def mean_anomaly_at_time_offset(
    mean_anomaly: float, time_offset_s: float, mean_motion: float
) -> float:
    """Calculates the mean anomaly at a given time offset from the current mean anomaly"""
    # return add(math.radians(mean_anomaly))(multiply(mean_motion)(time_offset_s))
    return add(mean_anomaly)(multiply(mean_motion)(time_offset_s))


def eccentric_anomaly(
    position_vector: list[float],
    velocity_vector: list[float],
    semi_major_axis: float,
    mean_motion: float,
) -> float:
    r = vector_magnitude_3d(position_vector)
    r_dot_v = dot_product_3d(position_vector, velocity_vector)

    y = r_dot_v
    x = semi_major_axis**2 * mean_motion * (1 - r / semi_major_axis)

    return math.atan2(y, x) % (2 * math.pi)


def eccentric_anomaly_from_true_anomaly(
    true_anomaly: float, eccentricity: float
) -> float:
    return 2 * math.atan2(
        math.sqrt(1 - eccentricity) * math.sin(true_anomaly / 2),
        math.sqrt(1 + eccentricity) * math.cos(true_anomaly / 2),
    )


def eccentric_anomaly_solved(
    iteration_func, eccentricity, mean_anomaly, tol=1e-6, max_iter=100
):
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

    return E_i, history


def true_anomaly_from_eccentric_anomaly(E_rad: float, e: float) -> float:
    sin_E = math.sin(E_rad)
    cos_E = math.cos(E_rad)

    sqrt_term = square_root(subtract(SQUARE(e))(1))

    y = multiply(sqrt_term)(sin_E)  # √(1 - e²) * sin(E)
    x = subtract(e)(cos_E)

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

    return theta


def true_anomaly_from_mean_anomaly(eccentricity: float, mean_anomaly: float) -> float:
    eccentric_anomaly, _ = eccentric_anomaly_solved(
        newton_iteration, eccentricity, mean_anomaly
    )

    return true_anomaly_from_eccentric_anomaly(eccentric_anomaly, eccentricity)


def argument_of_latitude(
    right_ascension_of_ascending_node: float,
    inclination: float,
    position_vector: list[float],
) -> float:
    numerator = divide(math.sin(inclination))(position_vector[2])
    second_term = add(
        multiply(position_vector[0])(math.cos(right_ascension_of_ascending_node))
    )(multiply(position_vector[1])(math.sin(right_ascension_of_ascending_node)))

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

    return u


def orbital_elements_from_state_vectors(
    position_vector: list[float],
    velocity_vector: list[float],
    gravitational_parameter: float = 398600,
) -> OrbitalElements:
    """Calculates the orbital elements of an orbit from the state vectors (position and velocity)"""
    # From TUB MSE SFM Exercise 2 solution
    angular_momentum_vector = vector_cross_multiplication_3d(
        position_vector, velocity_vector
    )
    inclination = inclination_from_angular_momentum_vector(angular_momentum_vector)
    right_ascension = right_ascension_from_angular_momentum_vector(
        angular_momentum_vector
    )
    semi_major_axis = semi_major_axis_from_position_and_velocity(
        position_vector, velocity_vector, gravitational_parameter
    )
    eccentricity = eccentricity_from_angular_momentum_vector(
        angular_momentum_vector, semi_major_axis, gravitational_parameter
    )
    mean_motion = mean_motion_from_semi_major_axis(
        semi_major_axis, gravitational_parameter
    )
    eccentric_an = eccentric_anomaly(
        position_vector, velocity_vector, semi_major_axis, mean_motion
    )
    true_anomaly = true_anomaly_from_eccentric_anomaly(eccentric_an, eccentricity)
    latitude = argument_of_latitude(right_ascension, inclination, position_vector)
    argument_of_perigee = subtract(true_anomaly)(latitude)

    return OrbitalElements(
        inclination=inclination,
        right_ascension=right_ascension,
        argument_of_perigee=argument_of_perigee,
        semi_major_axis=semi_major_axis,
        eccentricity=eccentricity,
        true_anomaly=true_anomaly,
    )


def newton_iteration(E_i, eccentricity, mean_anomaly):
    return E_i - (E_i - eccentricity * math.sin(E_i) - mean_anomaly) / (
        1 - eccentricity * math.cos(E_i)
    )


def perifocal_position_vector(radius: float, true_anomaly: float) -> list[float]:
    """Calculates the position vector in the perifocal coordinate system"""
    return vector_multiplication_3d(
        [math.cos(true_anomaly), math.sin(true_anomaly), 0],
        radius,
    )


def perifocal_velocity_vector(
    true_anomaly: float,
    eccentricity: float,
    gravitational_parameter: float,
    semi_major_axis: float,
) -> list[float]:
    """Calculates the velocity vector in the perifocal coordinate system"""
    return vector_multiplication_3d(
        [
            -math.sin(true_anomaly),
            add(eccentricity)(math.cos(true_anomaly)),
            0,
        ],
        square_root(
            divide(multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1)))(
                gravitational_parameter
            )
        ),
    )


def radius_at_true_anomaly(
    semi_major_axis: float, eccentricity: float, true_anomaly: float
) -> float:
    """Calculates the radius of an orbit at a given true anomaly"""
    return divide(add(1)(multiply(eccentricity)(math.cos(true_anomaly))))(
        multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1))
    )


def perifocal_to_eci_matrix(
    inclination,
    right_ascension,
    argument_of_perigee,
) -> list[list[float]]:
    p = [
        math.cos(argument_of_perigee) * math.cos(right_ascension)
        - math.sin(argument_of_perigee)
        * math.cos(inclination)
        * math.sin(right_ascension),
        math.cos(argument_of_perigee) * math.sin(right_ascension)
        + math.sin(argument_of_perigee)
        * math.cos(inclination)
        * math.cos(right_ascension),
        math.sin(argument_of_perigee) * math.sin(inclination),
    ]

    q = [
        -math.sin(argument_of_perigee) * math.cos(right_ascension)
        - math.cos(argument_of_perigee)
        * math.cos(inclination)
        * math.sin(right_ascension),
        -math.sin(argument_of_perigee) * math.sin(right_ascension)
        + math.cos(argument_of_perigee)
        * math.cos(inclination)
        * math.cos(right_ascension),
        math.cos(argument_of_perigee) * math.sin(inclination),
    ]

    w = [
        math.sin(inclination) * math.sin(right_ascension),
        -math.sin(inclination) * math.cos(right_ascension),
        math.cos(inclination),
    ]

    return [[p[0], q[0], w[0]], [p[1], q[1], w[1]], [p[2], q[2], w[2]]]


def transform_perifocal_to_eci(transposed_PQW, perifocal_vector) -> list[float]:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    return [
        dot_product_3d(transposed_PQW[0], perifocal_vector),
        dot_product_3d(transposed_PQW[1], perifocal_vector),
        dot_product_3d(transposed_PQW[2], perifocal_vector),
    ]


def true_anomaly_at_time_offset(
    eccentricity: float,
    mean_anomaly: float,
    time_offset_s: float,
    mean_motion: float,
    semi_major_axis: float,
    gravitational_parameter: float,
) -> float:
    mean_motion = mean_motion_from_semi_major_axis(
        semi_major_axis, gravitational_parameter
    )

    mean_anomaly_at_offset = mean_anomaly_at_time_offset(
        mean_anomaly, time_offset_s, mean_motion
    )

    eccentric_anomaly_at_offset, _ = eccentric_anomaly_solved(
        newton_iteration, eccentricity, mean_anomaly_at_offset
    )

    return true_anomaly_from_eccentric_anomaly(
        eccentric_anomaly_at_offset, eccentricity
    )


def orbit_state_vector_prediction_from_orbital_elements(
    orbital_elements_radians: OrbitalElements,
    time_offset_s: float,
    initial_mean_anomaly_radians: float | None = None,  # Shortcut
    gravitational_parameter: float = 398600,
) -> dict:
    """Calculates the state vectors (position and velocity) of an orbit from the orbital elements at a given time offset from the current position in the orbit"""
    inclination = orbital_elements_radians.inclination
    right_ascension = orbital_elements_radians.right_ascension
    argument_of_perigee = orbital_elements_radians.argument_of_perigee
    semi_major_axis = orbital_elements_radians.semi_major_axis
    eccentricity = orbital_elements_radians.eccentricity
    true_anomaly = orbital_elements_radians.true_anomaly

    if initial_mean_anomaly_radians is None:
        initial_mean_anomaly_radians = mean_anomaly_from_eccentric_anomaly(
            eccentric_anomaly_from_true_anomaly(true_anomaly, eccentricity),
            eccentricity,
        )

    true_anomaly_at_offset = true_anomaly_at_time_offset(
        eccentricity,
        initial_mean_anomaly_radians,
        time_offset_s,
        mean_motion_from_semi_major_axis(semi_major_axis, gravitational_parameter),
        semi_major_axis,
        gravitational_parameter,
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

    transposed_PQW = perifocal_to_eci_matrix(
        inclination, right_ascension, argument_of_perigee
    )

    position_vector = transform_perifocal_to_eci(transposed_PQW, perifocal_position)

    velocity_vector = transform_perifocal_to_eci(transposed_PQW, perifocal_velocity)

    return {"position_vector": position_vector, "velocity_vector": velocity_vector}


# TODO: FST 1 equations
# TODO: Increment of velocity

if __name__ == "__main__":
    # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)
    print(hohmann_transfer(300000, 1000000))

    # {'inclination': 0.12166217595729033, 'right_ascension': 3.024483909022929, 'argument_of_perigee': 1.5978995641224425, 'semi_major_axis': 25015.186690979368, 'eccentricity': 0.7079768603248032, 'true_anomaly': 2.987554518980773}
    print(orbital_elements_from_state_vectors([10000, 40000, -5000], [-1.5, 1, -0.1]))

    # {'position_vector': [-1753.131769017119, 1070.9950241554125, -6564.0676605044755], 'velocity_vector': [-3.478980009547892, 6.473396036204375, 1.986162313733967]}
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            OrbitalElements(
                inclination=math.radians(98.371),
                right_ascension=math.radians(120.534),
                argument_of_perigee=math.radians(10.598),
                semi_major_axis=6878.1,
                eccentricity=10e-5,
                true_anomaly=2.8022276030554347,
            ),
            1800,
            None,
        )
    )

    # {'position_vector': [10000.000000000044, 39999.99999999998, -4999.999999999999], 'velocity_vector': [-1.4999999999999984, 1.000000000000004, -0.1000000000000005]}
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            orbital_elements_from_state_vectors([10000, 40000, -5000], [-1.5, 1, -0.1]),
            1000000,
        )
    )
