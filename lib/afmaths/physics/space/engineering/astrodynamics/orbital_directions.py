from astronomy_types import (
    Distance,
    PositionVector,
    StateVector,
    Vector3D,
    VelocityVector,
)
from afmaths.types import OrbitalDirection
from afmaths.physics.space.celestial_mechanics import (
    angular_momentum,
    nadir_vector,
    zenith_vector,
)
from afmaths.tensors import (
    vector_negate,
    vector_normalise,
)


def radial(position: PositionVector) -> tuple[Vector3D, OrbitalDirection]:
    """Calculates the radial direction vector from a given position vector."""
    return (zenith_vector(position), OrbitalDirection.RADIAL)


def anti_radial(position: PositionVector) -> tuple[Vector3D, OrbitalDirection]:
    """Calculates the anti-radial direction vector from a given position vector."""
    return (nadir_vector(position), OrbitalDirection.ANTIRADIAL)


def prograde(velocity: VelocityVector) -> tuple[Vector3D, OrbitalDirection]:
    """Calculates the prograde direction vector from a given velocity vector."""
    return (vector_normalise(velocity), OrbitalDirection.PROGRADE)


def retrograde(velocity: VelocityVector) -> tuple[Vector3D, OrbitalDirection]:
    """Calculates the retrograde direction vector from a given velocity vector."""
    return (vector_negate(prograde(velocity)[0]), OrbitalDirection.RETROGRADE)


def normal(state: StateVector) -> tuple[Vector3D, OrbitalDirection]:
    """Calculates the normal direction vector from a given state vector."""
    return (vector_normalise(angular_momentum(state)), OrbitalDirection.NORMAL)


def anti_normal(state: StateVector) -> tuple[Vector3D, OrbitalDirection]:
    """Calculates the anti-normal direction vector from a given state vector."""
    return (vector_negate(normal(state)[0]), OrbitalDirection.ANTINORMAL)


def burn_direction_at_apsis(initial: Distance, target: Distance) -> OrbitalDirection:
    """Calculates if the burn should be prograde or retrograde (relative to the orbital direction) to adjust the height of the oribt."""
    if initial > target:
        return OrbitalDirection.RETROGRADE
    return OrbitalDirection.PROGRADE
