from __future__ import annotations

import datetime

import plotly.graph_objects as go

from afmaths.constants import EARTH_MU, EARTH_RADIUS
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)
from astronomy_types import Distance, Scalar

from helpers import orbital_characteristics_title
from orbit_source import Orbit, orbit_at_current_epoch, orbit_from_tle

DISTANCE_SCALE = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 100

SATELLITE_DISPLAY_RADIUS = Distance(Scalar(200_000))


def visualisation_3d_satellite_earth(
    orbits: list[Orbit],
) -> go.Figure:
    if not orbits:
        raise ValueError("At least one orbit is required.")

    current_orbits = [orbit_at_current_epoch(orbit) for orbit in orbits]

    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_MU,
        distance_scale=DISTANCE_SCALE,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        add_prediction_to_orbit=False,
    )

    return build_3d_orbit_figure(
        settings=settings,
        title=(
            f"{current_orbits[0].name} orbit | "
            f"Source: {current_orbits[0].source.value}"
            f"{orbital_characteristics_title(current_orbits[0])}"
        ),
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbiting_bodies=[
            BodyPlotConfig(
                name=orbit.name,
                target_object=orbit.elements,
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            )
            for orbit in current_orbits
        ],
    )


# Backwards-compatible wrapper.


def visualisation_3d_satellite_earth_from_tles(
    tles: list[str],
) -> go.Figure:
    return visualisation_3d_satellite_earth([orbit_from_tle(tle) for tle in tles])
