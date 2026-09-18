from __future__ import annotations

from pathlib import Path
from typing import Literal

from afmaths.afmath_types import GroundStation
from afmaths.constants import KILCUMMIN_GROUND_STATION
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.helpers import defined_kwargs, with_plot_settings_overrides

from dashboard import show_visualisation_dashboard
from ground_track import (
    GROUND_TRACK_POINTS,
    visualisation_2d_ground_track,
    visualisation_2d_ground_track_current_position,
)
from orbit_source import Orbit
from orbit_system_3d import (
    DEFAULT_SOLAR_SYSTEM_BODIES,
    build_3d_orbit_system_figure,
)
from orbit_visualiser_2d import (
    DEFAULT_PLOT_SETTINGS as ORBIT_2D_PLOT_SETTINGS,
    build_default_orbit_visualiser_2d_figure,
    satellite_orbiting_body,
)
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
    central_body: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    horizons_bodies: list[HorizonsCommandTarget] | None = None,
    include_default_system_bodies: bool = True,
    inertial_reference_frame: Literal["ICRF", "GCRF"] = "GCRF",
) -> list:
    """Build the independent figures used by the control-room dashboard."""
    if not orbits:
        raise ValueError("At least one orbit is required.")

    selected_orbit = orbits[0]
    ground_track_points = (
        plot_points if plot_points is not None else GROUND_TRACK_POINTS
    )
    orbit_2d_settings = with_plot_settings_overrides(
        ORBIT_2D_PLOT_SETTINGS, distance_scale=distance_scale, orbit_points=plot_points
    )
    satellites = [
        satellite_orbiting_body(name=orbit.name, elements=orbit.elements)
        for orbit in orbits
    ]
    orbit_plot_kwargs = defined_kwargs(
        distance_scale=distance_scale, orbit_points=plot_points
    )
    inertial_bodies = horizons_bodies
    if inertial_bodies is None and include_default_system_bodies:
        inertial_bodies = (
            DEFAULT_SOLAR_SYSTEM_BODIES
            if central_body is HorizonsCommandTarget.SUN
            else [HorizonsCommandTarget.MOON]
        )
    inertial_satellites = orbits if central_body is HorizonsCommandTarget.EARTH else []

    return [
        visualisation_2d_ground_track_current_position(
            orbit=selected_orbit,
            ground_station=ground_station,
            orbit_count=total_current_orbits,
            number_of_points=ground_track_points,
            lines=lines,
        ),
        build_3d_orbit_system_figure(
            central_body=central_body,
            horizons_bodies=inertial_bodies,
            satellite_orbits=inertial_satellites,
            reference_frame=inertial_reference_frame,
            **orbit_plot_kwargs,
        ),
        build_3d_orbit_system_figure(
            satellite_orbits=orbits,
            reference_frame="ITRF",
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
        build_default_orbit_visualiser_2d_figure(
            satellites=satellites,
            settings=orbit_2d_settings,
            propagation_orbits=total_orbits,
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
    columns: int = 1,
    distance_scale: float | None = None,
    plot_points: int | None = None,
    lines: bool = False,
    show_orbit_markers: bool = True,
    central_body: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    horizons_bodies: list[HorizonsCommandTarget] | None = None,
    include_default_system_bodies: bool = True,
    inertial_reference_frame: Literal["ICRF", "GCRF"] = "GCRF",
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
        central_body=central_body,
        horizons_bodies=horizons_bodies,
        include_default_system_bodies=include_default_system_bodies,
        inertial_reference_frame=inertial_reference_frame,
    )
    return show_visualisation_dashboard(
        figures,
        title=f"AFMaths Control Room - {orbits[0].name} ({orbits[0].source.value})",
        columns=columns,
        output_path=output_path,
    )
