from dataclasses import replace
import math
from typing import Callable

from afmaths.constants import (
    EARTH_MU,
    EARTH_RADIUS,
    GRAVITATIONAL_CONSTANT,
    SECONDS_PER_DAY,
    SIDEREAL_DAY,
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
    vector_negate,
    vector_normalise,
    vector_subtract_3d,
)

from afmaths.geometry.geometry import (
    calculate_distance_3d,
    eccentricity_factor_minus,
    eccentricity_factor_plus,
    eccentricity,
    generate_angles_on_circle,
    normalise_angle,
    semi_latus_rectum,
    semi_minor_axis,
    semi_minor_axis_from_semi_latus_rectum,
)
from afmaths.operation import (
    CUBE,
    DOUBLE,
    HALF,
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
    Area,
    DeltaV,
    Force,
    Mass,
    OrbitalDirection,
)

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


# TODO: FST 1 equations
# TODO: Increment of velocity


# region Directions


def nadir_vector(position: PositionVector) -> Vector3D:
    return vector_negate(zenith_vector(position))


def zenith_vector(position: PositionVector) -> Vector3D:
    return vector_normalise(position)


def orbital_direction_from_inclination(i: Inclination) -> OrbitalDirection:
    half_pi = HALF(math.pi)
    three_half_pi = multiply(3)(half_pi)

    prograde = i < half_pi or i > three_half_pi
    retrograde = half_pi < i < three_half_pi
    equatorial = i == 0 or i == math.pi
    polar = i == half_pi or i == three_half_pi

    if prograde and not equatorial and not polar:
        return OrbitalDirection.PROGRADE
    elif retrograde and not equatorial and not polar:
        return OrbitalDirection.RETROGRADE
    elif equatorial:
        return OrbitalDirection.RADIAL
    elif polar:
        return OrbitalDirection.NORMAL
    else:
        raise ValueError(
            f"Inclination {i} is somehow not valid for determining orbital direction."
        )


# endregion


# region Orbits


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


def gravitational_acceleration_at_radius(
    mu: GravitationalParameter, radius: Distance
) -> Acceleration:
    """Calculates the gravitational acceleration at a given radius from the central body."""
    return divide_by(SQUARE(radius))(mu)


def kepler_equation(E: EccentricAnomaly, e: Eccentricity) -> MeanAnomaly:
    """Calculates the mean anomaly from the eccentric anomaly and eccentricity."""
    # M = E - e * np.sin(E)
    return subtract(multiply(e)(math.sin(E)))(E)


def orbit_gravitational_force(
    velocity: Velocity, radius: Distance, mass: Mass
) -> Force:
    """Calculates the gravitational force of an orbiting object."""
    return centripetal_force(centripetal_acceleration(velocity, radius), mass)


def swept_area_of_ellipse(
    angular_momentum: AngularMomentum, time_since_periapsis: Second
) -> Area:
    """Calculates the area swept out by a satellite in an elliptical orbit since periapsis."""
    # From MSE SFM Exercise 1
    return multiply(HALF(angular_momentum_magnitude(angular_momentum)))(
        time_since_periapsis
    )


def mean_motion(
    a: SemiMajorAxis,
    mu: GravitationalParameter = EARTH_MU,
) -> MeanMotion:
    """Calculates the mean motion of an orbit from the semi major axis in radians per second"""
    # n = np.sqrt(mu / np.power(a, 3))
    return MeanMotion((mean_angular_rate(a, mu)))


def distance_between_positions(pos1: PositionVector, pos2: PositionVector) -> Distance:
    """Calculates the distance between two position vectors in 3D space."""
    return calculate_distance_3d(
        coordinate3d_from_vector(vector3d_from_position(pos1)),
        coordinate3d_from_vector(vector3d_from_position(pos2)),
    )


# region Latitude


def argument_of_latitude_from_true_anomaly(
    argument_of_periapsis: ArgumentOfPeriapsis, theta: TrueAnomaly
) -> Latitude:
    """Calculates the argument of latitude from the right ascension of the ascending node and the true anomaly."""
    return make_radians(add(argument_of_periapsis)(theta))


def argument_of_latitude(
    raan: RightAscension,
    i: Inclination,
    position: PositionVector,
) -> Latitude:
    """Finds the latitude of the satellite in the orbital plane from the position vector and the right ascension of the ascending node."""
    # u = np.arctan2(r[2] / np.sin(i), r[0] * np.cos(Omega) + r[1] * np.sin(Omega))
    # if u < 0:
    #     u += 2 * np.pi
    y = divide_by(math.sin(i))(position.z)
    x = add(multiply(position.x)(math.cos(raan)))(multiply(position.y)(math.sin(raan)))

    return normalise_angle(make_radians(math.atan2(y, x)))


# region Velocity
def vis_viva(
    mu: GravitationalParameter,
    radius: Distance,
    a: SemiMajorAxis,
) -> Velocity:
    """Calculates the velocity of an object in an elliptical orbit using the vis-viva equation."""
    return Velocity(
        Scalar(
            square_root(multiply(mu)(subtract(divide_by(a)(1))(divide_by(radius)(2))))
        )
    )


def radial_velocity(state: StateVector) -> Velocity:
    position = vector3d_from_position(state.position)

    return Velocity(
        divide_by(vector_magnitude_3d(position))(
            dot_product_3d(position, vector3d_from_velocity(state.velocity))
        )
    )


def velocity_at_radius(
    r: Distance,
    mu: GravitationalParameter = EARTH_MU,
) -> Velocity:
    return Velocity(Scalar(square_root(divide_by(r)(mu))))


def periapsis_velocity(
    mu: GravitationalParameter, elements: OrbitalElements
) -> Velocity:
    return vis_viva(
        mu,
        periapsis_radius(elements.semi_major_axis, elements.eccentricity),
        elements.semi_major_axis,
    )


def apoapsis_velocity(
    mu: GravitationalParameter, elements: OrbitalElements
) -> Velocity:
    return vis_viva(
        mu,
        apoapsis_radius(elements.semi_major_axis, elements.eccentricity),
        elements.semi_major_axis,
    )


# region Radius


def orbit_equation(
    a: SemiMajorAxis,
    e: Eccentricity,
    theta: TrueAnomaly,
) -> Distance:
    """Calculates the instantaneos radius of an orbit at a given true anomaly. This is the equation of motion for an elliptical orbit."""
    # Trajectory equation: r = p / (1 + e * cos(theta))
    # Kepler's first law: r = a * (1 - e^2) / (1 + e * cos(theta))
    return divide_by(eccentricity_factor_plus(multiply(e)(math.cos(theta))))(
        semi_latus_rectum(a, e)
    )


def gravitational_acceleration_at_altitude(
    alt: Distance,
    central_body_radius: Distance,
    mu: GravitationalParameter,
) -> Acceleration:
    """Calculates the gravitational acceleration at a given altitude above a central body."""
    # From MSE SFM Exercise 1
    return gravitational_acceleration_at_radius(
        mu,
        orbit_radius(alt, central_body_radius),
    )


def orbit_radius(
    alt: Distance, central_body_radius: Distance = EARTH_RADIUS
) -> Distance:
    """Calculates the radius of an orbit from the altitude and the central body radius."""
    return add(alt)(central_body_radius)


def orbit_altitude(
    radius: Distance, central_body_radius: Distance = EARTH_RADIUS
) -> Distance:
    """Calculates the altitude of an orbit from the radius and the central body radius."""
    return Distance(subtract(central_body_radius)(radius))


def distance_satellite_observer(
    itrf_position: PositionVector, observer: Coordinate3D
) -> Distance:
    # MSE ISG
    return Distance(
        Scalar(
            vector_magnitude_3d(
                vector_subtract_3d(
                    itrf_position, make_vector3d(observer.x, observer.y, observer.z)
                )
            )
        )
    )


def orbital_radius_from_position_vector(pos: PositionVector) -> Distance:
    return Distance(vector_magnitude_3d(make_vector3d(pos.x, pos.y, pos.z)))


def periapsis_radius(a: SemiMajorAxis, e: Eccentricity) -> Distance:
    """r_p=a(1-e)"""
    return multiply(a)(eccentricity_factor_minus(e))


def apoapsis_radius(a: SemiMajorAxis, e: Eccentricity) -> Distance:
    """r_p=a(1+e)"""
    return multiply(a)(eccentricity_factor_plus(e))


# region Angular Momentum


def mean_angular_rate(a: SemiMajorAxis, mu: GravitationalParameter) -> Rate:
    """Calculates the mean angular rate of an orbit from the semi major axis and gravitational parameter."""
    # From MSE SFM Exercise 1
    return Rate(Scalar(square_root(divide_by(CUBE(a))(mu))))


def angular_momentum(state_vectors: StateVector) -> AngularMomentum:
    """Calculates the angular momentum vector of an orbiting object from its position and velocity vectors."""
    # From MSE SFM Exercise 2
    return AngularMomentum(
        vector_cross_multiplication_3d(state_vectors.position, state_vectors.velocity)
    )


def angular_momentum_magnitude(angular_momentum_vector: Vector3D[Scalar]) -> Scalar:
    # From MSE SFM Exercise 1
    return vector_magnitude_3d(angular_momentum_vector)


def instantaneous_angular_velocity(state_vectors: StateVector) -> Scalar:
    # From MSE SFM Exercise 1
    h = angular_momentum_magnitude(angular_momentum(state_vectors))
    r = vector_magnitude_3d(vector3d_from_position(state_vectors.position))

    return divide_by(SQUARE(r))(h)


def angular_momentum_magnitude_from_apsides(
    periapsis: Distance, apoapsis: Distance, mu: GravitationalParameter
) -> Scalar:
    return multiply(square_root(DOUBLE(mu)))(
        square_root(divide_by(add(apoapsis)(periapsis))(multiply(apoapsis)(periapsis)))
    )


# endregion

# region Angular Velocity


def angular_velocity_from_period(period: Second = SIDEREAL_DAY) -> Radians:
    """Calculates the angular velocity of a body given a period."""
    return divide_by(period)(DOUBLE(math.pi))


# endregion
