from astronomy_types import (
    Acceleration,
    Coordinate2D,
    Coordinate3D,
    Displacement,
    Position,
    PositionVector,
    Scalar,
    Second,
    Vector2D,
    Vector3D,
    Velocity,
)

from afmaths.geometry.geometry import area_rectangle
from afmaths.graph import slope_gradiant
from afmaths.operation import add, multiply, trapezoidal_rule
from afmaths.physics.space.type_conversion_helpers import make_vector3d
from afmaths.tensors import vector_multiplication_2d, vector_multiplication_3d


def position_displacement(
    coords: Coordinate3D[Scalar],
    origin: Coordinate3D[Scalar],
) -> PositionVector:
    """displacement interpreted as position relative to origin"""
    v = displacement_vector(coords, origin)
    return PositionVector(
        Position(
            v.x,
        ),
        Position(v.y),
        Position(v.z),
    )


# region Displacement


def displacement_vector(
    coords: Coordinate3D[Scalar],
    origin: Coordinate3D[Scalar],
) -> Vector3D[Displacement]:
    """target coordinate − origin coordinate"""
    return make_vector3d(
        Displacement(Scalar(coords.x - origin.x)),
        Displacement(Scalar(coords.y - origin.y)),
        Displacement(Scalar(coords.z - origin.z)),
    )


def velocity_time_displacement_flat(
    flat_component_start: Coordinate2D = Coordinate2D(0, 0),
    flat_component_end: Coordinate2D = Coordinate2D(0, 0),
) -> Displacement:
    return Displacement(
        Scalar(
            area_rectangle(
                flat_component_start.y, flat_component_end.x - flat_component_start.x
            )
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


# endregion
# region Speed & Velocity
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


# endregion


# region Propagation
def propagate_vector(
    initial: Coordinate2D[float],
    vector: Vector2D,
    iterations: int = 100,
) -> list[Coordinate2D]:
    """Propogates a vector through 2D space for a given number of iterations, returning the coordinates at each iteration. This is useful for detecting collisions between two objects with known initial coordinates and vectors."""

    positions = []

    for i in range(iterations + 1):
        displacement = vector_multiplication_2d(vector, Scalar(i))

        positions.append(
            Coordinate2D(
                float(initial.x) + float(displacement.x),
                float(initial.y) + float(displacement.y),
            )
        )

    return positions


def propagate_vector_3d(
    initial: Coordinate3D,
    vector: Vector3D,
    iterations: int = 100,
) -> list[Coordinate3D]:
    """Propogates a vector through 3D space for a given number of iterations, returning the coordinates at each iteration. This is useful for detecting collisions between two objects with known initial coordinates and vectors."""
    positions = []

    for i in range(iterations + 1):
        displacement = vector_multiplication_3d(vector, Scalar(i))

        positions.append(
            Coordinate3D(
                float(initial.x) + float(displacement.x),
                float(initial.y) + float(displacement.y),
                float(initial.z) + float(displacement.z),
            )
        )

    return positions


# endregion

# region Collission


def detect_collision(
    object_a_coordinates: Coordinate2D,
    object_b_coordinates: Coordinate2D,
    object_a_vector: Vector2D,
    object_b_vector: Vector2D,
    margin: int = 1,
) -> tuple[bool, Coordinate2D]:
    """Detects if two objects will collide given their initial coordinates and vectors. Returns a tuple of (collision_detected, collision_coordinates)"""
    a_positions = propagate_vector(object_a_coordinates, object_a_vector)
    b_positions = propagate_vector(object_b_coordinates, object_b_vector)

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
    a_positions = propagate_vector_3d(object_a_coordinates, object_a_vector)
    b_positions = propagate_vector_3d(object_b_coordinates, object_b_vector)

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


# endregion
