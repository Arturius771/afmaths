from __future__ import annotations

from pathlib import Path

from afmaths.physics.space.external.space_track_api import (
    get_tle_from_norad_id,
    refresh_tle_cache,
)
from astronomy_types import Degrees, GeographicCoordinates, Scalar, Second

from dashboard import show_visualisation_dashboard
from eci_orbit_3d import visualisation_3d_satellite_earth
from ground_track import (
    visualisation_2d_ground_track_current_position_propogation,
    visualisation_2d_ground_track_tle_propagation,
)
from itrf_orbit_3d import visualisation_3d_itrf


def build_control_room_figures(
    norad_ids: list[int],
    total_tle_orbits: int,
    total_current_orbits: int,
    ground_station: GeographicCoordinates = GeographicCoordinates(
        Degrees(Scalar(53)),
        Degrees(Scalar(-6)),
    ),
    ground_station_name: str = "Dublin, Ireland",
    ground_station_longitude_range: Degrees = Degrees(Scalar(5)),
):
    """Build the four independent figures used by the control-room dashboard."""
    if not norad_ids:
        raise ValueError("At least one NORAD ID is required.")

    refresh_tle_cache()
    tles = [get_tle_from_norad_id(norad_id) for norad_id in norad_ids]
    selected_tle = tles[0]

    return [
        visualisation_2d_ground_track_tle_propagation(
            tle=selected_tle,
            orbit_count=total_tle_orbits,
            show_orbit_markers=True,
        ),
        visualisation_2d_ground_track_current_position_propogation(
            tle=selected_tle,
            ground_station=ground_station,
            ground_station_name=ground_station_name,
            ground_station_longitude_range=ground_station_longitude_range,
            orbit_count=total_current_orbits,
        ),
        visualisation_3d_satellite_earth(tles),
        visualisation_3d_itrf(selected_tle, total_tle_orbits),
    ]


def launch_control_room(
    norad_ids: list[int],
    total_tle_orbits: int,
    total_current_orbits: int,
    output_path: Path | None = None,
) -> Path:
    """Open the four control-room figures in one 2x2 browser dashboard."""
    figures = build_control_room_figures(
        norad_ids=norad_ids,
        total_tle_orbits=total_tle_orbits,
        total_current_orbits=total_current_orbits,
    )
    return show_visualisation_dashboard(
        figures,
        title=f"AFMaths Control Room — NORAD {norad_ids[0]}",
        columns=1,
        output_path=output_path,
    )
