from __future__ import annotations

import datetime

import plotly.graph_objects as go

from afmaths.constants import EARTH_RADIUS
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import EARTH_MU
from afmaths.physics.space.celestial_mechanics.orbital_elements import state_vector_at_time
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    general_orbital_characteristics,
)
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.physics.space.transformations import itrf_positions_from_gcrs_position
from afmaths.visualisations.base import OrbitPlotSettings, build_3d_itrf_orbit_figure
from astronomy_types import OrbitalElements, Scalar, Second

from orbit_source import Orbit, orbit_from_elements, orbit_from_tle

DISTANCE_SCALE = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 50



def _orbital_characteristics_title(orbit: Orbit) -> str:
    if orbit.tle is None:
        return ""

    return f"<br>{general_orbital_characteristics(orbit.tle)}"

def visualisation_3d_itrf(
    orbits: list[Orbit],
    track_for_orbits: float = 3,
) -> go.Figure:
    if not orbits:
        raise ValueError("At least one orbit is required.")

    itrf_positions = []

    for orbit in orbits:
        track_for_seconds = (
            orbital_period(orbit.elements.semi_major_axis) * track_for_orbits
        )

        gcrs_positions = [
            state_vector_at_time(
                orbit.elements,
                Second(Scalar(second)),
                EARTH_MU,
            ).position
            for second in range(0, int(track_for_seconds), 60)
        ]

        itrf_positions.append(
            itrf_positions_from_gcrs_position(
                gcrs_positions,
                orbit.epoch,
            )
        )

    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_MU,
        distance_scale=DISTANCE_SCALE,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=1),
        add_prediction_to_orbit=False,
    )

    return build_3d_itrf_orbit_figure(
        settings=settings,
        itrf_positions=itrf_positions,
        title=(
            f"{orbits[0].name} ITRF orbit | "
            f"Source: {orbits[0].source.value} | "
            f"Orbits: {track_for_orbits}"
            f"{_orbital_characteristics_title(orbits[0])}"
        ),
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbit_name=[orbit.name for orbit in orbits],
    )


# Backwards-compatible wrappers.


def visualisation_3d_itrf_from_tles(
    tles: list[str],
    track_for_orbits: float = 3,
) -> go.Figure:
    return visualisation_3d_itrf(
        [orbit_from_tle(tle) for tle in tles],
        track_for_orbits=track_for_orbits,
    )


def visualisation_3d_itrf_orbital_elements(
    elements: list[OrbitalElements],
    track_for_orbits: float = 3,
) -> go.Figure:
    return visualisation_3d_itrf(
        [
            orbit_from_elements(element, name=f"Satellite {index + 1}")
            for index, element in enumerate(elements)
        ],
        track_for_orbits=track_for_orbits,
    )
