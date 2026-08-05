from dataclasses import replace
import math

from afmaths.operation import negate, subtract
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    perifocal_position_vector,
)
from astronomy_types import (
    ArgumentOfPeriapsis,
    OrbitalElements,
    PositionVector,
    TrueAnomaly,
)

from afmaths.physics.space.type_conversion_helpers import make_true_anomaly


def true_anomaly_at_ascending_node(
    argument_of_periapsis: ArgumentOfPeriapsis,
) -> TrueAnomaly:
    return make_true_anomaly(negate(argument_of_periapsis))


def true_anomaly_at_descending_node(
    argument_of_periapsis: ArgumentOfPeriapsis,
) -> TrueAnomaly:
    return make_true_anomaly(subtract(argument_of_periapsis)(math.pi))


def perifocal_position_at_ascending_node(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    return perifocal_position_vector(
        replace(
            orbital_elements,
            true_anomaly=true_anomaly_at_ascending_node(
                orbital_elements.argument_of_periapsis
            ),
        )
    )


def perifocal_position_at_descending_node(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    return perifocal_position_vector(
        replace(
            orbital_elements,
            true_anomaly=true_anomaly_at_descending_node(
                orbital_elements.argument_of_periapsis
            ),
        )
    )
