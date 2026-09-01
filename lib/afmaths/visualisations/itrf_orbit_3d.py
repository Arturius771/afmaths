from __future__ import annotations

import datetime
import math
from pathlib import Path

import plotly.graph_objects as go
from PIL import Image

from afmaths.constants import EARTH_RADIUS, TWO_PI
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import EARTH_MU
from afmaths.physics.space.celestial_mechanics.state_vector import (
    position_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.utils import (
    orbit_description_from_elements,
)
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.physics.space.transformations import itrf_positions_from_gcrf_position
from afmaths.visualisations.base import OrbitPlotSettings, build_3d_itrf_orbit_figure
from astronomy_types import OrbitalElements, Scalar, Second
from orbit_source import Orbit, orbit_from_elements, orbit_from_tle

from typing import cast

DISTANCE_SCALE = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 50

EARTH_IMAGE_PATH = Path(__file__).with_name("Earth-hires.jpg")

EARTH_TEXTURE_WIDTH = 360
EARTH_TEXTURE_HEIGHT = 181
EARTH_TEXTURE_COLOURS = 256


def _add_textured_earth(
    figure: go.Figure,
    image_path: Path = EARTH_IMAGE_PATH,
) -> go.Figure:
    figure.data = tuple(
        trace for trace in figure.data if getattr(trace, "name", None) != "Earth"
    )

    image = (
        Image.open(image_path)
        .convert("RGB")
        .resize(
            (EARTH_TEXTURE_WIDTH, EARTH_TEXTURE_HEIGHT),
            Image.Resampling.LANCZOS,
        )
    )

    quantised = image.quantize(
        colors=EARTH_TEXTURE_COLOURS,
        method=Image.Quantize.MEDIANCUT,
    )

    surface_colour = [
        [cast(int, quantised.getpixel((x, y))) for x in range(EARTH_TEXTURE_WIDTH)]
        for y in range(EARTH_TEXTURE_HEIGHT)
    ]

    palette = quantised.getpalette()

    if palette is None:
        raise ValueError(f"Could not create colour palette from {image_path}")

    number_of_colours = int(max(max(row) for row in surface_colour)) + 1

    colourscale = []

    for index in range(number_of_colours):
        offset = index * 3

        red = palette[offset]
        green = palette[offset + 1]
        blue = palette[offset + 2]

        colourscale.append(
            [
                index / max(number_of_colours - 1, 1),
                f"rgb({red},{green},{blue})",
            ]
        )

    earth_radius = float(EARTH_RADIUS) * BODY_RADIUS_SCALE / DISTANCE_SCALE

    longitude_values = [
        -math.pi + (TWO_PI * longitude_index / (EARTH_TEXTURE_WIDTH - 1))
        for longitude_index in range(EARTH_TEXTURE_WIDTH)
    ]

    latitude_values = [
        math.pi / 2 - (math.pi * latitude_index / (EARTH_TEXTURE_HEIGHT - 1))
        for latitude_index in range(EARTH_TEXTURE_HEIGHT)
    ]

    x_coordinates = []
    y_coordinates = []
    z_coordinates = []

    for latitude in latitude_values:
        x_row = []
        y_row = []
        z_row = []

        cos_latitude = math.cos(latitude)
        sin_latitude = math.sin(latitude)

        for longitude in longitude_values:
            x_row.append(earth_radius * cos_latitude * math.cos(longitude))

            y_row.append(earth_radius * cos_latitude * math.sin(longitude))

            z_row.append(earth_radius * sin_latitude)

        x_coordinates.append(x_row)
        y_coordinates.append(y_row)
        z_coordinates.append(z_row)

    figure.add_trace(
        go.Surface(
            x=x_coordinates,
            y=y_coordinates,
            z=z_coordinates,
            surfacecolor=surface_colour,
            colorscale=colourscale,
            cmin=0,
            cmax=max(number_of_colours - 1, 1),
            showscale=False,
            name="Earth",
            showlegend=False,
            hoverinfo="skip",
            lighting={
                "ambient": 0.8,
                "diffuse": 0.8,
                "specular": 0.1,
                "roughness": 0.9,
                "fresnel": 0.05,
            },
            lightposition={
                "x": 100_000,
                "y": 100_000,
                "z": 100_000,
            },
        )
    )

    return figure


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

        gcrf_positions = [
            position_vector_at_time(
                orbit.elements,
                Second(Scalar(second)),
                EARTH_MU,
            )
            for second in range(
                0,
                int(track_for_seconds),
                60,
            )
        ]

        itrf_positions.append(
            itrf_positions_from_gcrf_position(
                gcrf_positions,
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

    figure = build_3d_itrf_orbit_figure(
        settings=settings,
        itrf_positions=itrf_positions,
        title=(
            f"{orbits[0].name} ITRF orbit | "
            f"Source: {orbits[0].source.value} | "
            f"Orbits: {track_for_orbits}"
            f"<br>{orbit_description_from_elements(orbits[0].elements)} @ Epoch"
        ),
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbit_name=[orbit.name for orbit in orbits],
    )

    return _add_textured_earth(figure)


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
            orbit_from_elements(
                element,
                name=f"Satellite {index + 1}",
            )
            for index, element in enumerate(elements)
        ],
        track_for_orbits=track_for_orbits,
    )
