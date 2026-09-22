from astronomy_types import (
    Acceleration,
    Coordinate2D,
    Coordinate3D,
    Distance,
    GravitationalParameter,
    Ratio,
    Scalar,
)

from afmaths.afmath_types import Mass
from afmaths.constants import (
    ASTRONOMICAL_UNIT,
    EARTH_MASS,
    GRAVITATIONAL_CONSTANT,
    SUN_MASS,
)
from afmaths.numerical_analysis import root_solver
from afmaths.operation import (
    HALF,
    SQUARE,
    add,
    divide_by,
    multiply,
    negate,
    newtons_raphson_method,
    square_root,
    subtract,
)


def barycenter(mass1: Mass, mass2: Mass, distance: Distance) -> Distance:
    """
    Calculate the barycenter (center of mass) of a two-body system.

    :param mass1: Mass of the first body.
    :param mass2: Mass of the second body.
    :param distance: Distance between the two bodies.
    :return: Distance from the first body to the barycenter.
    """
    return divide_by(add(mass1)(mass2))(multiply(mass2)(distance))


def solve_for_equilibrium(
    mu: float,
    initial_guess: float = 0.5,
    tolerance: float = 1e-6,
    max_iterations: int = 1000,
) -> float:
    """Solve for an equilibrium point using Newton-Raphson iteration."""

    def equilibrium(x: float) -> float:
        return (
            x
            - (1 - mu) * (x + mu) / abs(x + mu) ** 3
            - mu * (x - 1 + mu) / abs(x - 1 + mu) ** 3
        )

    def derivative(x: float) -> float:
        return 1 + 2 * (1 - mu) / abs(x + mu) ** 3 + 2 * mu / abs(x - 1 + mu) ** 3

    return root_solver(
        iteration_function=lambda x: newtons_raphson_method(
            x,
            equilibrium(x),
            derivative(x),
        ),
        initial_guess=initial_guess,
        difference_function=lambda next_x, x: next_x - x,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )[0]


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


def mass_parameter(mass1: Mass, mass2: Mass) -> Ratio:
    """
    Calculate the dimensionless mass parameter for the circular
    restricted three-body problem.

    mu = m2 / (m1 + m2)
    """
    return divide_by(add(mass1)(mass2))(mass2)


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


# region Lagrange points functions


def lagrange_points(m1: Mass, m2: Mass, r: Distance) -> list[Coordinate2D]:
    """
    Calculate the Lagrange points for a two-body system.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.


    Returns:
    - A list of Coordinate2D objects representing the positions of the Lagrange points.
    """
    return [
        lagrange_1(m1, m2, r),
        lagrange_2(m1, m2, r),
        lagrange_3(m1, m2, r),
        lagrange_4(m1, m2, r),
        lagrange_5(m1, m2, r),
    ]


def lagrange_points_3d(m1: Mass, m2: Mass, r: Distance) -> list[Coordinate3D]:
    """
    Calculate the Lagrange points for a two-body system in 3D.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.

    Returns:
    - A list of Coordinate3D objects representing the positions of the Lagrange points.
    """
    return [
        lagrange_1_3d(m1, m2, r),
        lagrange_2_3d(m1, m2, r),
        lagrange_3_3d(m1, m2, r),
        lagrange_4_3d(m1, m2, r),
        lagrange_5_3d(m1, m2, r),
    ]


def lagrange_1(m1: Mass, m2: Mass, r: Distance) -> Coordinate2D:
    """
    Calculate the position of the Lagrange point L1 for a two-body system.
    """
    mu = mass_parameter(m1, m2)
    distance = multiply(r)

    initial_guess = 1 - mu - (mu / 3) ** (1 / 3)

    return Coordinate2D(
        distance(solve_for_equilibrium(mu, initial_guess)),
        0,
    )


def lagrange_2(m1: Mass, m2: Mass, r: Distance) -> Coordinate2D:
    """
    Calculate the position of the Lagrange point L2 for a two-body system.
    """
    mu = mass_parameter(m1, m2)
    distance = multiply(r)

    initial_guess = 1 - mu + (mu / 3) ** (1 / 3)

    return Coordinate2D(
        distance(solve_for_equilibrium(mu, initial_guess)),
        0,
    )


def lagrange_3(m1: Mass, m2: Mass, r: Distance) -> Coordinate2D:
    """
    Calculate the position of the Lagrange point L3 for a two-body system.
    """
    mu = mass_parameter(m1, m2)
    distance = multiply(r)

    initial_guess = -1 - 5 * mu / 12

    return Coordinate2D(
        distance(solve_for_equilibrium(mu, initial_guess)),
        0,
    )


def lagrange_4(m1: Mass, m2: Mass, r: Distance) -> Coordinate2D:
    """
    Calculate the position of the Lagrange point L4 for a two-body system.
    """
    mu = mass_parameter(m1, m2)
    distance = multiply(r)

    return Coordinate2D(
        distance(subtract(mu)(HALF(1))),
        distance(HALF(square_root(3))),
    )


def lagrange_5(m1: Mass, m2: Mass, r: Distance) -> Coordinate2D:
    """
    Calculate the position of the Lagrange point L5 for a two-body system.
    """
    mu = mass_parameter(m1, m2)
    distance = multiply(r)

    return Coordinate2D(
        distance(subtract(mu)(HALF(1))),
        distance(negate(HALF(square_root(3)))),
    )


def lagrange_1_3d(m1: Mass, m2: Mass, r: Distance) -> Coordinate3D:
    """
    Calculate the position of the Lagrange point L1 for a two-body system.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.

    Returns:
    - A Coordinate3D object representing the position of the Lagrange point L1.
    """
    # Calculate the Lagrange point L1 here
    # This is a placeholder implementation and should be replaced with the actual calculation
    return Coordinate3D(0, 0, 0)


def lagrange_2_3d(m1: Mass, m2: Mass, r: Distance) -> Coordinate3D:
    """
    Calculate the position of the Lagrange point L2 for a two-body system.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.

    Returns:
    - A Coordinate3D object representing the position of the Lagrange point L2.
    """
    # Calculate the Lagrange point L2 here
    # This is a placeholder implementation and should be replaced with the actual calculation
    return Coordinate3D(0, 0, 0)


def lagrange_3_3d(m1: Mass, m2: Mass, r: Distance) -> Coordinate3D:
    """
    Calculate the position of the Lagrange point L3 for a two-body system.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.

    Returns:
    - A Coordinate3D object representing the position of the Lagrange point L3.
    """
    # Calculate the Lagrange point L3 here
    # This is a placeholder implementation and should be replaced with the actual calculation
    return Coordinate3D(0, 0, 0)


def lagrange_4_3d(m1: Mass, m2: Mass, r: Distance) -> Coordinate3D:
    """
    Calculate the position of the Lagrange point L4 for a two-body system.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.

    Returns:
    - A Coordinate3D object representing the position of the Lagrange point L4.
    """
    # Calculate the Lagrange point L4 here
    # This is a placeholder implementation and should be replaced with the actual calculation
    return Coordinate3D(0, 0, 0)


def lagrange_5_3d(m1: Mass, m2: Mass, r: Distance) -> Coordinate3D:
    """
    Calculate the position of the Lagrange point L5 for a two-body system.

    Parameters:
    - m1: Mass of the first body.
    - m2: Mass of the second body.
    - r: Distance between the two bodies.

    Returns:
    - A Coordinate3D object representing the position of the Lagrange point L5.
    """
    # Calculate the Lagrange point L5 here
    # This is a placeholder implementation and should be replaced with the actual calculation
    return Coordinate3D(0, 0, 0)


def is_trojan_capable(mass1: Mass, mass2: Mass) -> bool:
    """
    Determine if a two-body system is capable of having Trojan asteroids.

    Parameters:
    - mass1: Mass of the first body (typically the primary, e.g., a star).
    - mass2: Mass of the second body (typically the secondary, e.g., a planet).

    Returns:
    - True if the system can have Trojan asteroids, False otherwise.

    See:
    - https://www.youtube.com/watch?v=_DYZF-piKKU
    """
    # A system is generally considered capable of having Trojans if the mass ratio is below a certain threshold.
    # For the Sun-Jupiter system, this threshold is approximately 0.0385.

    return mass_parameter(mass1, mass2) < 0.04


# region Sphere of Influence functions


def planetary_sphere_of_influence_approximation(
    mean_distance: Distance = ASTRONOMICAL_UNIT,
    planet_mass: Mass = EARTH_MASS,
    star_mass: Mass = SUN_MASS,
) -> Distance:
    """
    Calculate the approximate sphere of influence of a planet around a star using the patched conics approximation.

    Parameters
    ----------
    mean_distance : Distance
        The mean distance between the planet and the star (default is the astronomical unit).
    planet_mass : Mass
        The mass of the planet (default is the mass of the Earth).
    star_mass : Mass
        The mass of the star (default is the mass of the Sun).

    Returns
    -------
    Distance
        The radius of the planet's sphere of influence.
    """
    # Using the formula for the sphere of influence: r_SOI = a * (m/M)^(2/5)
    return mean_distance * (planet_mass / star_mass) ** (2 / 5)


def hill_sphere_approximation(
    mean_distance: Distance = ASTRONOMICAL_UNIT,
    planet_mass: Mass = EARTH_MASS,
    star_mass: Mass = SUN_MASS,
) -> Distance:
    """
    Calculate the Hill sphere of a planet around a star.

    Parameters
    ----------
    mean_distance : Distance
        The mean distance between the planet and the star (default is the astronomical unit).
    planet_mass : Mass
        The mass of the planet (default is the mass of the Earth).
    star_mass : Mass
        The mass of the star (default is the mass of the Sun).

    Returns
    -------
    Distance
        The radius of the planet's Hill sphere.
    """
    # Using the formula for the Hill sphere: r_Hill = a * (m/(3*M))^(1/3)
    return mean_distance * (planet_mass / (3 * star_mass)) ** (1 / 3)
