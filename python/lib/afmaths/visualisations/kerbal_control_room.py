"""Kerbin dashboard assembled from existing AFMaths visualisations.

Orbits are supplied by the caller; this module does not acquire or propagate them.
"""

from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go
from astronomy_types import Distance, GravitationalParameter, Scalar

from afmaths.visualisations.dashboard import show_visualisation_dashboard
from afmaths.visualisations.orbit_source import orbit_elements
from afmaths.visualisations.orbit_system_3d import build_3d_orbit_system_figure
from afmaths.visualisations.orbit_visualiser_2d import (
    DEFAULT_PLOT_SETTINGS as ORBIT_2D_PLOT_SETTINGS,
)
from afmaths.visualisations.orbit_visualiser_2d import (
    build_default_orbit_visualiser_2d_figure,
    satellite_orbiting_body,
)
from afmaths.visualisations.state_vectors import (
    build_position_vector_figure,
    build_velocity_vector_figure,
)
from afmaths.visualisations.visualisation_types import Orbit, PlotOriginConfig

KERBIN = PlotOriginConfig(
    name="Kerbin",
    target=None,
    radius=Distance(Scalar(600_000)),
    gravitational_parameter=GravitationalParameter(Scalar(3.5316e12)),
    radius_scale=1.0,
    distance_scale=100_000.0,
)


def build_kerbal_control_room_figures(
    orbits: list[Orbit],
    total_orbits: float = 1.0,
    *,
    distance_scale: float | None = None,
    plot_points: int | None = None,
) -> list[go.Figure]:
    """Build plots from the existing AFMaths visualisation functions."""
    if not orbits:
        raise ValueError("At least one supplied orbit is required.")

    selected_elements = orbit_elements(orbits[0])
    satellites = [
        satellite_orbiting_body(name=orbit.name, elements=orbit_elements(orbit))
        for orbit in orbits
    ]
    orbit_3d_options = {
        **({"distance_scale": distance_scale} if distance_scale is not None else {}),
        **({"orbit_points": plot_points} if plot_points is not None else {}),
    }

    return [
        build_3d_orbit_system_figure(
            origin_body=KERBIN,
            horizons_bodies=[],
            satellite_orbits=orbits,
            reference_frame="ICRF",
            track_for_orbits=total_orbits,
            **orbit_3d_options,
        ),
        build_default_orbit_visualiser_2d_figure(
            satellites=satellites,
            settings=ORBIT_2D_PLOT_SETTINGS,
            propagation_orbits=total_orbits,
        ),
        build_position_vector_figure(selected_elements, int(total_orbits)),
        build_velocity_vector_figure(selected_elements, int(total_orbits)),
    ]


def launch_kerbal_control_room(
    orbits: list[Orbit],
    total_orbits: float = 1.0,
    output_path: Path | None = None,
    *,
    columns: int = 2,
    distance_scale: float | None = None,
    plot_points: int | None = None,
) -> Path:
    figures = build_kerbal_control_room_figures(
        orbits,
        total_orbits,
        distance_scale=distance_scale,
        plot_points=plot_points,
    )
    return show_visualisation_dashboard(
        figures,
        title=f"AFMaths Kerbal Control Room — {orbits[0].name}",
        columns=columns,
        output_path=output_path,
    )
