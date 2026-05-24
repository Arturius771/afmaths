import math
from afmaths.formula import inverse_square_law, trapezoidal_rule
from afmaths.geometry import area_of_right_triangle
from afmaths.graph import slope_gradiant
from afmaths.operation import (
    HALF,
    SQUARE,
    add,
    divide,
    exponentiate,
    multiply,
    subtract,
)
from astronomy_types import (
    Acceleration,
    Coordinate2D,
    Coordinate3D,
    Displacement,
    Scalar,
    Distance,
    Second,
    Vector2D,
    Vector3D,
    Velocity,
    dataclass,
)


@dataclass(frozen=True)
class TriangleDescription:
    start: Coordinate2D
    peak: Coordinate2D
    end: Coordinate2D


SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(-34)(10))
GRAVITATIONAL_CONSTANT = multiply(6.67430)(exponentiate(-11)(10))  # 6.67430e-11


### PHYSICS FORMULAS
def radiowave_relative_power_distances(distance1: float, distance2: float) -> tuple:
    """Calculates the relative power distances of two radio waves"""
    ##TM255 Block 1
    distance_ratio = divide(distance1)(distance2)
    quartic = exponentiate(4)
    distance1_strength = quartic(distance_ratio)
    divide_by_distance_1_strength = divide(distance1_strength)
    distance2_strength = divide_by_distance_1_strength(1)

    return distance_ratio, distance1_strength, distance2_strength


def radiowave_received_power_difference_by_distance(
    power_in_watts_at_distance1: float, distance1: float, distance2: float
) -> float:
    """Calculates the difference in received power between two distances"""
    # https://www.youtube.com/watch?v=BF73QaY1aEg
    cross_multiply = multiply(power_in_watts_at_distance1)(SQUARE(distance1))
    return divide(SQUARE(distance2))(cross_multiply)


def photon_energy_from_wavelength(wavelength_in_micrometer: float) -> float:
    """Returns photon energy in electrovolts"""
    return divide(wavelength_in_micrometer)(1.2398)


def photon_energy_from_frequency(frequency_in_hertz: float) -> float:
    """Returns photon energy in joules"""
    return multiply(PLANCK_CONSTANT)(frequency_in_hertz)


def frequency_to_wavelength(frequency_in_hertz: float) -> float:
    """Returns wavelength in metres"""
    return divide(frequency_in_hertz)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def wavelength_to_frequency(wavelength_in_metres: float) -> float:
    """Returns frequency in hertz"""
    return divide(wavelength_in_metres)(SPEED_OF_LIGHT_METRES_PER_SECONDS)


def dynamic_pressure(fluid_mass_density: float, flow_speed: float) -> float:
    """Calculates the dynamic pressure of a fluid"""
    return multiply(HALF(fluid_mass_density))(SQUARE(flow_speed))


def watts_to_decibel_milliwatts(power_in_watts: float) -> float:
    """Converts watts to decibels relative to one milliwatt"""
    return decibels(power_in_watts)(0.001)


def decibels(power1: float):
    """Returns a function that calculates the decibels between two powers"""
    return lambda power2: math.log(power1 / power2, 10)


def flux_density(luminosity: float, distance_metres: float) -> float:
    """Calculates the flux density of a light source"""
    return inverse_square_law(luminosity, distance_metres)


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


def angular_diameter_degrees(distance: float, diameter: float) -> float:
    """Calculates the angular diameter of an object in degrees"""
    return math.degrees(diameter / distance)


def diameter_of_distant_object(
    distance: float, angular_diameter_degrees: float
) -> float:
    """Returns the diameter of an object if the distance and angular diameter are known"""
    # Rearranges the equation in angular_diameter_degrees()
    return math.tan(math.radians(angular_diameter_degrees)) * distance


def calculate_gravitional_parameter(mass1: float, mass2: float) -> float:
    """
    Calculates the graviational parameter (Mu) of two objects in m^3/s^2

    :param mass1: The first bodies mass
    :type mass1: float
    :param mass2: The second bodies mass
    :type mass2: float
    :return: Mu = G * (mass1 + mass2)
    :rtype: float
    """
    return multiply(GRAVITATIONAL_CONSTANT)(mass1 + mass2)


def calculate_schwarzschild_radius(mass: float) -> float:
    """
    Calculates the size an object would have to be shrunk down to to become a black hole.

    :param mass: The mass of the object d
    :type mass: float
    :return: The radius in metres
    :rtype: float
    """
    return divide(SQUARE(SPEED_OF_LIGHT_METRES_PER_SECONDS))(
        multiply(multiply(2)(GRAVITATIONAL_CONSTANT))(mass)
    )


def displacement_from_velocity_flat(
    flat_component_start: Coordinate2D = Coordinate2D(0, 0),
    flat_component_end: Coordinate2D = Coordinate2D(0, 0),
) -> Displacement:
    return multiply(flat_component_start.y)(
        flat_component_end.x - flat_component_start.x
    )


def displacement_from_velocity_curve(
    start: Coordinate2D,
    end: Coordinate2D,
) -> Displacement:
    """Area under a straight-line velocity-time segment."""

    # Credit: https://www.khanacademy.org/science/ap-college-physics-1/xf557a762645cccc5:kinematics/xf557a762645cccc5:visual-models-of-motion/a/what-are-velocity-vs-time-graphs

    if start.y == 0 or end.y == 0:
        area = area_of_right_triangle(
            end.x - start.x,
            max(start.y, end.y),
        )
    else:
        area = trapezoidal_rule(start, end)

    return Displacement(Scalar(area))


def displacement_of_velocity_curve_section(
    triangle_on_graph: TriangleDescription,
    first_slice: TriangleDescription,
    second_slice: TriangleDescription,
) -> Displacement:
    """Calculate a sectional area under a triangular curve of a velocity-time graph."""

    whole_area = displacement_from_velocity_curve(
        triangle_on_graph.start,
        triangle_on_graph.end,
    )

    first_slice_area = displacement_from_velocity_curve(
        first_slice.start,
        first_slice.end,
    )

    second_slice_area = displacement_from_velocity_curve(
        second_slice.start,
        second_slice.end,
    )

    section_area = subtract(add(first_slice_area)(second_slice_area))(whole_area)

    return Displacement(Scalar(section_area))


def average_acceleration_from_slope(
    time_and_velocity1: Coordinate2D, time_and_velocity2: Coordinate2D
) -> Acceleration:
    return Acceleration(Scalar(slope_gradiant(time_and_velocity1, time_and_velocity2)))


def velocity_after_duration(
    acceleration: Acceleration, initial_velocity: Velocity, duration: Second
) -> Velocity:
    return add(initial_velocity)(multiply(acceleration)(duration))


def total_displacement(sorted_points: list[Coordinate2D]) -> Displacement:
    total = 0

    for start, end in zip(sorted_points, sorted_points[1:]):
        total += displacement_from_velocity_curve(start, end)

    return Displacement(Scalar(total))


def propogate_vector(
    initial: Coordinate2D, vector: Vector2D, iterations: int = 100
) -> list[Coordinate2D]:
    x = [initial]
    for i in range(iterations):
        x.append(
            Coordinate2D(
                float(x[i].x) + float(vector.x), float(x[i].y) + float(vector.y)
            )
        )

    return x


def propogate_vector_3d(
    initial: Coordinate3D, vector: Vector3D, iterations: int = 100
) -> list[Coordinate3D]:
    x = [initial]
    for i in range(iterations):
        x.append(
            Coordinate3D(
                float(x[i].x) + float(vector.x),
                float(x[i].y) + float(vector.y),
                float(x[i].z) + float(vector.z),
            )
        )

    return x


def detect_collision(
    object_a_coordinates: Coordinate2D,
    object_b_coordinates: Coordinate2D,
    object_a_vector: Vector2D,
    object_b_vector: Vector2D,
) -> tuple[bool, Coordinate2D]:
    a_positions = propogate_vector(object_a_coordinates, object_a_vector)
    b_positions = propogate_vector(object_b_coordinates, object_b_vector)

    length_a = len(a_positions)
    length_b = len(b_positions)

    if length_a > length_b:
        for i in range(length_a):
            if a_positions[i] == b_positions[i]:
                return True, a_positions[i]
    else:
        for i in range(length_b):
            if a_positions[i] == b_positions[i]:
                return True, b_positions[i]

    return False, Coordinate2D(0, 0)


def detect_collision_3d(
    object_a_coordinates: Coordinate3D,
    object_b_coordinates: Coordinate3D,
    object_a_vector: Vector3D,
    object_b_vector: Vector3D,
) -> tuple[bool, Coordinate3D]:
    a_positions = propogate_vector_3d(object_a_coordinates, object_a_vector)
    b_positions = propogate_vector_3d(object_b_coordinates, object_b_vector)

    length_a = len(a_positions)
    length_b = len(b_positions)

    if length_a > length_b:
        for i in range(length_a):
            if a_positions[i] == b_positions[i]:
                return True, a_positions[i]
    else:
        for i in range(length_b):
            if a_positions[i] == b_positions[i]:
                return True, b_positions[i]

    return False, Coordinate3D(0, 0, 0)


if __name__ == "__main__":
    print(
        displacement_from_velocity_curve(
            Coordinate2D(3, 6),
            Coordinate2D(7, 0),
        )
        + displacement_from_velocity_flat(
            Coordinate2D(0, 6),
            Coordinate2D(3, 6),
        )
    )  # 30
    print(
        average_acceleration_from_slope(Coordinate2D(0, 3), Coordinate2D(6, 0))
    )  # -0.5
    print(
        displacement_from_velocity_curve(
            Coordinate2D(2, 0),
            Coordinate2D(3, -5),
        )
    )  # -2.5
    print(
        displacement_from_velocity_curve(
            Coordinate2D(0, 0),
            Coordinate2D(2, 0),
        )
        + displacement_from_velocity_curve(
            Coordinate2D(2, 0),
            Coordinate2D(3, -5),
        )
    )  # 2.5

    print(
        displacement_of_velocity_curve_section(
            TriangleDescription(
                Coordinate2D(0, 0),
                Coordinate2D(1, 5),
                Coordinate2D(2, 0),
            ),
            TriangleDescription(
                Coordinate2D(0, 0),
                Coordinate2D(0.5, 2.5),
                Coordinate2D(0.5, 2.5),
            ),
            TriangleDescription(
                Coordinate2D(1.5, 2.5),
                Coordinate2D(1.5, 2.5),
                Coordinate2D(2, 0),
            ),
        )
    )  # 3.75

    print(
        displacement_from_velocity_curve(
            Coordinate2D(1, 0),
            Coordinate2D(3, 4),
        )
        + displacement_from_velocity_flat(
            Coordinate2D(3, 4),
            Coordinate2D(4, 4),
        )
    )  # 8

    print(
        displacement_from_velocity_curve(
            Coordinate2D(1, 5),
            Coordinate2D(2, 9),
        )
    )  # 2.5

    print(
        velocity_after_duration(
            Acceleration(Scalar(1)), Velocity(Scalar(0)), Second(Scalar(5))
        )
    )

    print(propogate_vector(Coordinate2D(0, 0), Vector2D(1, 1), 2))

    print(
        detect_collision(
            Coordinate2D(0, 0), Coordinate2D(2, 0), Vector2D(1, 0), Vector2D(-1, 0)
        )
    )
