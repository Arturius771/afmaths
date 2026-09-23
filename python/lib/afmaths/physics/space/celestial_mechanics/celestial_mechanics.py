import math

from astronomy_types import (
    Acceleration,
    ArgumentOfPeriapsis,
    Coordinate3D,
    Distance,
    EccentricAnomaly,
    Eccentricity,
    EquatorialCoordinates,
    GravitationalParameter,
    Inclination,
    Latitude,
    MeanAnomaly,
    MeanMotion,
    OrbitalElements,
    PositionVector,
    Radians,
    Rate,
    RightAscension,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVector,
    TrueAnomaly,
    Vector3D,
    Velocity,
)

from afmaths.afmath_types import (
    AngularMomentum,
    Area,
    Force,
    Mass,
    OrbitalDirection,
)
from afmaths.constants import (
    EARTH_MU,
    EARTH_RADIUS,
    SIDEREAL_DAY,
    TWO_PI,
)
from afmaths.geometry.geometry import (
    eccentricity_factor_minus,
    eccentricity_factor_plus,
    euclidian_distance_3d,
    normalise_angle,
    semi_latus_rectum,
)
from afmaths.operation import (
    CUBE,
    DOUBLE,
    HALF,
    SQUARE,
    add,
    divide_by,
    multiply,
    square_root,
    subtract,
)
from afmaths.physics.physics import centripetal_acceleration, centripetal_force
from afmaths.physics.space.celestial_mechanics.gravitation import (
    gravitational_acceleration_at_radius,
)
from afmaths.physics.space.type_conversion_helpers import (
    coordinate3d_from_vector,
    make_radians,
    make_vector3d,
    vector3d_from_position,
    vector3d_from_velocity,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_cross_multiplication_3d,
    vector_magnitude_3d,
    vector_negate,
    vector_normalise,
    vector_subtract_3d,
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
    return MeanMotion(mean_angular_rate(a, mu))


def distance_between_positions(pos1: PositionVector, pos2: PositionVector) -> Distance:
    """Calculates the distance between two position vectors in 3D space."""
    return euclidian_distance_3d(
        coordinate3d_from_vector(vector3d_from_position(pos1)),
        coordinate3d_from_vector(vector3d_from_position(pos2)),
    )


# region Orbital Plane


def argument_of_latitude_from_true_anomaly(
    argument_of_periapsis: ArgumentOfPeriapsis, theta: TrueAnomaly
) -> Latitude:
    """Calculates the argument of latitude from the right ascension of the ascending node and the true anomaly. Latitude is the angle between the orbital plane and the position vector of the satellite."""
    return make_radians(add(argument_of_periapsis)(theta))


def argument_of_latitude(
    raan: RightAscension,
    i: Inclination,
    position: PositionVector,
) -> Latitude:
    """Finds the latitude (the angle between the orbital plane and the position vector of the satellite) of the satellite in the orbital plane from the position vector and the right ascension of the ascending node."""
    # u = np.arctan2(r[2] / np.sin(i), r[0] * np.cos(Omega) + r[1] * np.sin(Omega))
    # if u < 0:
    #     u += 2 * np.pi
    y = divide_by(math.sin(i))(position.z)
    x = add(multiply(position.x)(math.cos(raan)))(multiply(position.y)(math.sin(raan)))

    return normalise_angle(make_radians(math.atan2(y, x)))


def angle_above_orbital_plane(
    target_object: EquatorialCoordinates,
    orbit: OrbitalElements,
) -> Radians:
    """Calculates the angle of a target object above or below the orbital plane of a given orbit."""
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
    return divide_by(period)(TWO_PI)


# endregion
