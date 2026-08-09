from __future__ import annotations

from pathlib import Path

from astronomy_types import Degrees, GeographicCoordinates, Scalar

from afmaths.afmath_types import GroundStation
from afmaths.constants import KILCUMMIN_GROUND_STATION
from dashboard import show_visualisation_dashboard
from eci_orbit_3d import visualisation_3d_satellite_earth
from ground_track import (
    visualisation_2d_ground_track,
    visualisation_2d_ground_track_current_position,
)
from itrf_orbit_3d import visualisation_3d_itrf
from orbit_source import Orbit


def build_control_room_figures(
    orbits: list[Orbit],
    total_orbits: float,
    total_current_orbits: float,
    ground_station: GroundStation = KILCUMMIN_GROUND_STATION,
) -> list:
    """Build the four independent figures used by the control-room dashboard."""
    if not orbits:
        raise ValueError("At least one orbit is required.")

    selected_orbit = orbits[0]

    return [
        visualisation_2d_ground_track(
            orbit=selected_orbit,
            orbit_count=total_orbits,
            show_orbit_markers=True,
        ),
        visualisation_3d_itrf(
            orbits,
            track_for_orbits=total_orbits,
        ),
        visualisation_2d_ground_track_current_position(
            orbit=selected_orbit,
            ground_station=ground_station,
            orbit_count=total_current_orbits,
        ),
        visualisation_3d_satellite_earth(orbits),
    ]


def launch_control_room(
    orbits: list[Orbit],
    total_orbits: float,
    total_current_orbits: float,
    output_path: Path | None = None,
) -> Path:
    """Open the four control-room figures in one browser dashboard."""
    if not orbits:
        raise ValueError("At least one orbit is required.")

    figures = build_control_room_figures(
        orbits=orbits,
        total_orbits=total_orbits,
        total_current_orbits=total_current_orbits,
    )

    return show_visualisation_dashboard(
        figures,
        title=(
            f"AFMaths Control Room - {orbits[0].name} " f"({orbits[0].source.value})"
        ),
        columns=1,
        output_path=output_path,
    )
