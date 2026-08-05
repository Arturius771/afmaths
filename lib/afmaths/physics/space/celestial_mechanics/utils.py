from dataclasses import replace
from afmaths.geometry.geometry import generate_angles_on_circle
from afmaths.operation import interval_points
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    state_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import EARTH_MU

from astronomy_types import (
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    Ratio,
    Scalar,
    Second,
    PositionVector,
)


def generate_all_orbit_positions(
    orbital_elements: OrbitalElements,
    resolution: int = 50,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> list[PositionVector]:
    if resolution < 5:
        raise ValueError("Resolution must be greater than 5.")
    position_list = []
    for true_anomaly in generate_angles_on_circle(resolution):
        position_list.append(
            state_vector_at_time(
                replace(
                    orbital_elements,
                    true_anomaly=true_anomaly,
                ),
                mu=gravitational_parameter,
            ).position
        )
    return position_list


def second_intervals_for_orbits(
    start: Second,
    total_duration: Second,
    number_of_intervals: int,
    step: Second | None = None,
) -> list[Second]:
    """Generates a list of time intervals in seconds for a given number of orbits based on the orbital period and a specified interval."""
    return [
        Second(Scalar(second))
        for second in interval_points(
            float(start), float(total_duration + start), number_of_intervals, step
        )
    ]
