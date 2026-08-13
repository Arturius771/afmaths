from astronomy_types import Degrees, Radians, Second
from afmaths.constants import EARTH_ANGULAR_VELOCITY
from afmaths.operation import multiply
from afmaths.physics.space.type_conversion_helpers import degrees_from_radians


def westward_drift_from_angular_velocity_and_period(
    orbital_period: Second,
    body_angular_velocity: Radians = EARTH_ANGULAR_VELOCITY,
) -> Degrees:
    """Calculate westward drift from the orbital period and body rotation rate."""
    return degrees_from_radians(multiply(body_angular_velocity)(orbital_period))
