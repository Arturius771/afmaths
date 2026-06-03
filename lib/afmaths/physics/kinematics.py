from astronomy_types import (
    Acceleration,
    Coordinate2D,
    Coordinate3D,
    Displacement,
    Scalar,
    Second,
    Vector2D,
    Vector3D,
    Velocity,
)

from afmaths.formula import trapezoidal_rule
from afmaths.geometry import area
from afmaths.graph import slope_gradiant
from afmaths.operation import add, multiply


def velocity_time_displacement_flat(
    flat_component_start: Coordinate2D = Coordinate2D(0, 0),
    flat_component_end: Coordinate2D = Coordinate2D(0, 0),
) -> Displacement:
    return Displacement(
        Scalar(
            area(flat_component_start.y, flat_component_end.x - flat_component_start.x)
        )
    )


def velocity_time_curve_displacement(
    curve: list[Coordinate2D],
) -> Displacement:
    """Signed area under a straight-line velocity-time segment."""

    # Credit: https://www.khanacademy.org/science/ap-college-physics-1/xf557a762645cccc5:kinematics/xf557a762645cccc5:visual-models-of-motion/a/what-are-velocity-vs-time-graphs
    return Displacement(Scalar(trapezoidal_rule(curve)))


def velocity_time_displacement_curve_section(
    start: Coordinate2D,
    end: Coordinate2D,
) -> Displacement:
    """Signed area under a straight-line velocity-time segment."""

    return Displacement(Scalar(trapezoidal_rule([start, end])))


def velocity_time_average_acceleration_from_slope(
    time_and_velocity1: Coordinate2D, time_and_velocity2: Coordinate2D
) -> Acceleration:
    """Calculates the average acceleration of an object given two points on a velocity-time graph. The points must be in the form (time, velocity)"""
    return Acceleration(Scalar(slope_gradiant(time_and_velocity1, time_and_velocity2)))


def velocity_after_duration(
    acceleration: Acceleration, initial_velocity: Velocity, duration: Second
) -> Velocity:
    """Calculates the velocity of an object after a given duration of constant acceleration, starting from an initial velocity."""
    return add(initial_velocity)(multiply(acceleration)(duration))


def velocity_time_total_displacement(sorted_points: list[Coordinate2D]) -> Displacement:
    """Calculates the total displacement of an object given a velocity-time graph with multiple segments. The points must be sorted in order of time."""
    total = 0

    for start, end in zip(sorted_points, sorted_points[1:]):
        total += velocity_time_displacement_curve_section(start, end)

    return Displacement(Scalar(total))


def propogate_vector(
    initial: Coordinate2D[float], vector: Vector2D, iterations: int = 100
) -> list[Coordinate2D]:
    """Propogates a vector through 2D space for a given number of iterations, returning the coordinates at each iteration. This is useful for detecting collisions between two objects with known initial coordinates and vectors."""
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
    """Propogates a vector through 3D space for a given number of iterations, returning the coordinates at each iteration. This is useful for detecting collisions between two objects with known initial coordinates and vectors."""
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
    margin: int = 1,
) -> tuple[bool, Coordinate2D]:
    """Detects if two objects will collide given their initial coordinates and vectors. Returns a tuple of (collision_detected, collision_coordinates)"""
    a_positions = propogate_vector(object_a_coordinates, object_a_vector)
    b_positions = propogate_vector(object_b_coordinates, object_b_vector)

    for i in range(len(a_positions)):
        if a_positions[i] == b_positions[i] or (
            abs(a_positions[i].x - b_positions[i].x) < margin
            and abs(a_positions[i].y - b_positions[i].y) < margin
        ):
            return True, a_positions[i]

    return False, Coordinate2D(0, 0)


def detect_collision_3d(
    object_a_coordinates: Coordinate3D,
    object_b_coordinates: Coordinate3D,
    object_a_vector: Vector3D,
    object_b_vector: Vector3D,
) -> tuple[bool, Coordinate3D]:
    """Detects if two objects will collide given their initial coordinates and vectors. Returns a tuple of (collision_detected, collision_coordinates)"""
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
