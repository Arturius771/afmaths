from __future__ import annotations

from pathlib import Path

from afmaths.afmath_types import GroundStation
from afmaths.constants import KILCUMMIN_GROUND_STATION
from dashboard import show_visualisation_dashboard
from eci_orbit_3d import visualisation_3d_satellite_earth
from afmaths.visualisations.helpers import defined_kwargs
from ground_track import (
    GROUND_TRACK_POINTS,
    visualisation_2d_ground_track,
    visualisation_2d_ground_track_current_position,
)
from itrf_orbit_3d import visualisation_3d_itrf
from orbit_source import Orbit
from state_vectors import build_position_vector_figure, build_velocity_vector_figure


def build_control_room_figures(
    orbits: list[Orbit],
    total_orbits: float,
    total_current_orbits: float,
    ground_station: GroundStation = KILCUMMIN_GROUND_STATION,
    *,
    distance_scale: float | None = None,
    plot_points: int | None = None,
    lines: bool = False,
    show_orbit_markers: bool = True,
) -> list:
    """Build the independent figures used by the control-room dashboard."""
    if not orbits:
        raise ValueError("At least one orbit is required.")

    selected_orbit = orbits[0]
    ground_track_points = (
        plot_points if plot_points is not None else GROUND_TRACK_POINTS
    )
    orbit_plot_kwargs = defined_kwargs(
        distance_scale=distance_scale,
        orbit_points=plot_points,
    )

    return [
        visualisation_2d_ground_track_current_position(
            orbit=selected_orbit,
            ground_station=ground_station,
            orbit_count=total_current_orbits,
            number_of_points=ground_track_points,
            lines=lines,
        ),
        visualisation_3d_satellite_earth(orbits, **orbit_plot_kwargs),
        visualisation_3d_itrf(
            orbits,
            track_for_orbits=total_orbits,
            **orbit_plot_kwargs,
        ),
        visualisation_2d_ground_track(
            orbit=selected_orbit,
            orbit_count=total_orbits,
            show_orbit_markers=show_orbit_markers,
            number_of_points=ground_track_points,
            lines=lines,
        ),
        build_position_vector_figure(selected_orbit.elements, int(total_orbits)),
        build_velocity_vector_figure(selected_orbit.elements, int(total_orbits)),
    ]


def launch_control_room(
    orbits: list[Orbit],
    total_orbits: float,
    total_current_orbits: float,
    output_path: Path | None = None,
    *,
    columns: int = 2,
    distance_scale: float | None = None,
    plot_points: int | None = None,
    lines: bool = False,
    show_orbit_markers: bool = True,
) -> Path:
    """Open the control-room figures in one browser dashboard."""
    figures = build_control_room_figures(
        orbits=orbits,
        total_orbits=total_orbits,
        total_current_orbits=total_current_orbits,
        distance_scale=distance_scale,
        plot_points=plot_points,
        lines=lines,
        show_orbit_markers=show_orbit_markers,
    )

    return show_visualisation_dashboard(
        figures,
        title=(
            f"AFMaths Control Room - {orbits[0].name} " f"({orbits[0].source.value})"
        ),
        columns=columns,
        output_path=output_path,
    )
