from astronomy_types import Degrees, MeanMotion, Radians, Scalar, Second
from afmaths.constants import EARTH_ANGULAR_VELOCITY, MEAN_SOLAR_DAY
from afmaths.operation import divide_by, multiply
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    angular_velocity_from_period,
)
from afmaths.physics.space.type_conversion_helpers import degrees_from_radians


def westward_drift_from_angular_velocity_and_period(
    orbital_period: Second,
    body_angular_velocity: Radians = EARTH_ANGULAR_VELOCITY,
) -> Degrees:
    """Calculate westward drift from the orbital period and body rotation rate."""
    return degrees_from_radians(multiply(body_angular_velocity)(orbital_period))


def westward_drift_from_mean_motion(
    n: MeanMotion,
    body_angular_velocity: Radians = EARTH_ANGULAR_VELOCITY,
    reference_period: Second = MEAN_SOLAR_DAY,
) -> Degrees:
    """Calculate westward drift per orbit from reference-period mean motion."""
    rotations_per_reference_period = body_rotations_per_reference_period(
        body_angular_velocity=body_angular_velocity,
        reference_period=reference_period,
    )

    return Degrees(Scalar(multiply(360)(divide_by(n)(rotations_per_reference_period))))


def body_rotations_per_reference_period(
    body_angular_velocity: Radians = EARTH_ANGULAR_VELOCITY,
    reference_period: Second = MEAN_SOLAR_DAY,
) -> Scalar:
    """Calculate the body's number of rotations during a reference period."""
    reference_angular_velocity = angular_velocity_from_period(reference_period)

    return Scalar(divide_by(reference_angular_velocity)(body_angular_velocity))
