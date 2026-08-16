from afmaths.afmath_types import OrbitalDirection
from afmaths.constants import EARTH_MU
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    orbital_direction_from_inclination,
)
from astronomy_types import OrbitalElements

from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.westward_drift import (
    westward_drift_from_angular_velocity_and_period,
)


def general_orbital_characteristics_from_elements(elements: OrbitalElements) -> str:
    """Extracts general orbital characteristics from OrbitalElements and returns them as a formatted string."""
    direction = orbital_direction_from_inclination(elements.inclination)
    period = orbital_period(elements.semi_major_axis, EARTH_MU)

    return f"Drift: { westward_drift_from_angular_velocity_and_period(period):.2f}° | {"Prograde" if direction == OrbitalDirection.PROGRADE else "Retrograde"} | Period: {period:.0f}s<br>a: {elements.semi_major_axis:.0f}m | e: {elements.eccentricity:.6f} | i: {elements.inclination:.2f}° | raan(Ω): {elements.right_ascension_of_ascending_node:.2f}° | aop(ω): {elements.argument_of_periapsis:.2f}° | ta(ν): {elements.true_anomaly:.2f}°"
