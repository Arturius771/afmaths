from astronomy_types import Distance, Scalar, Second, Acceleration, Velocity

from afmaths.constants import STANDARD_GRAVITY
from afmaths.operation import add, divide_by
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
