import math

from astronomy_types import (
    Coordinate2D,
    Degrees,
    Distance,
    Scalar,
    Second,
    Acceleration,
    Velocity,
)

from afmaths.constants import STANDARD_GRAVITY
from afmaths.operation import DOUBLE, HALF, SQUARE, add, divide_by, square_root
from afmaths.physics.kinematics import displacement, velocity_after_duration


def height_from_acceleration(
    acceleration: Acceleration,
    duration: Second,
    initial_height: Distance = Distance(Scalar(0)),
) -> Distance:
    """Calculates the height of an object after a given duration of constant acceleration, starting from an initial height."""
    return add(displacement(acceleration, duration))(initial_height)


def max_velocity(
    acceleration: Acceleration,
    duration: Second,
    initial_velocity: Velocity = Velocity(Scalar(0)),
) -> Velocity:
    """Calculates the maximum velocity of an object after a given duration of constant acceleration, starting from an initial velocity."""
    return velocity_after_duration(acceleration, initial_velocity, duration)


def duration_to_max_height(
    acceleration_duration: Second,
    acceleration: Acceleration,
    gravitational_acceleration: Acceleration = STANDARD_GRAVITY,
) -> Second:
    """Calculates the total duration of a motion given the duration of constant acceleration, the acceleration, and the gravitational acceleration."""
    return add(acceleration_duration)(
        divide_by(gravitational_acceleration)(
            max_velocity(acceleration, acceleration_duration)
        )
    )


def ballistic_vacuum_initial_velocity(
    target_coordinates: Coordinate2D,
    launch_angle: Degrees,
    initial_coordinates: Coordinate2D = Coordinate2D(0, 0),
    g: Acceleration = STANDARD_GRAVITY,
) -> Velocity:
    """Calculates the initial velocity of a projectile given its launch coordinates and launch angle."""
    actual_target_coordinates = Coordinate2D(
        target_coordinates.x - initial_coordinates.x,
        target_coordinates.y - initial_coordinates.y,
    )
    return Velocity(
        Scalar(
            square_root(
                divide_by(
                    actual_target_coordinates.x
                    * math.sin(DOUBLE(math.radians(launch_angle)))
                    - DOUBLE(actual_target_coordinates.y)
                    * SQUARE(math.cos(math.radians(launch_angle)))
                )(SQUARE(actual_target_coordinates.x) * g)
            )
        )
    )


def ballistic_vacuum_displacement_at_time(
    initial_velocity: Velocity,
    launch_angle: Degrees,
    time: Second,
    g: Acceleration = STANDARD_GRAVITY,
) -> Coordinate2D:
    """Calculates the displacement of a projectile at a given time after launch."""
    x_displacement = initial_velocity * math.cos(math.radians(launch_angle)) * time
    y_displacement = initial_velocity * math.sin(
        math.radians(launch_angle)
    ) * time - HALF(g * SQUARE(time))
    return Coordinate2D(x_displacement, y_displacement)


def ballistic_vacuum_angle_to_target(
    target_coordinates: Coordinate2D,
    initial_velocity: Velocity,
    initial_coordinates: Coordinate2D = Coordinate2D(0, 0),
    g: Acceleration = STANDARD_GRAVITY,
) -> tuple[Degrees, Degrees]:
    """Calculates the launch angle required to hit a target at given coordinates with a specified initial velocity."""
    x = target_coordinates.x - initial_coordinates.x
    y = target_coordinates.y - initial_coordinates.y
    v = initial_velocity
    discriminant = SQUARE(SQUARE(v)) - g * (g * SQUARE(x) + DOUBLE(y) * SQUARE(v))

    angle1 = math.atan((SQUARE(v) + square_root(discriminant)) / (g * x))
    angle2 = math.atan((SQUARE(v) - square_root(discriminant)) / (g * x))

    return Degrees(Scalar(math.degrees(angle1))), Degrees(Scalar(math.degrees(angle2)))


def basllistic_vacuum_time_to_target(
    target_coordinates: Coordinate2D,
    initial_velocity: Velocity,
    launch_angle: Degrees,
    initial_coordinates: Coordinate2D = Coordinate2D(0, 0),
    g: Acceleration = STANDARD_GRAVITY,
) -> Second:
    """Calculates the time it takes for a projectile to reach a target at given coordinates with a specified initial velocity and launch angle."""
    x = target_coordinates.x - initial_coordinates.x
    y = target_coordinates.y - initial_coordinates.y

    # Calculate the time to reach the target using the quadratic formula
    a = -HALF(g)
    b = initial_velocity * math.sin(math.radians(launch_angle))
    c = -y

    discriminant = SQUARE(b) - 4 * (a * c)
    if discriminant < 0:
        raise ValueError("No real solution for time to target.")

    t1 = (-b + square_root(discriminant)) / (2 * a)
    t2 = (-b - square_root(discriminant)) / (2 * a)

    # Return the positive time value
    return Second(Scalar(max(t1, t2)))
