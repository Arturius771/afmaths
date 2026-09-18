from __future__ import annotations

import datetime
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

import plotly.graph_objects as go
from PIL import Image

from afmaths.constants import EARTH_MU, EARTH_RADIUS, TWO_PI
from afmaths.physics.space.celestial_mechanics.state_vector import (
    position_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.utils import (
    orbit_description_from_elements,
)
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.physics.space.transformations import itrf_positions_from_gcrf_position
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_itrf_orbit_figure,
    build_3d_orbit_figure,
)
from astronomy_types import Distance, GravitationalParameter, Scalar, Second
from orbit_source import Orbit, orbit_at_current_epoch

ReferenceFrame = Literal["ICRF", "GCRF", "ITRF"]

EARTH_DISTANCE_SCALE = 1_000.0
SOLAR_DISTANCE_SCALE = 1_000_000_000.0
EARTH_BODY_RADIUS_SCALE = 1.0
PLANET_RADIUS_SCALE = 2_000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 100
SATELLITE_DISPLAY_RADIUS = Distance(Scalar(200_000.0))
EARTH_IMAGE_PATH = Path(__file__).with_name("Earth-hires.jpg")


def _add_textured_earth(
    figure: go.Figure,
    *,
    distance_scale: float,
    body_radius_scale: float,
    image_path: Path = EARTH_IMAGE_PATH,
) -> go.Figure:
    """Replace the generic Earth surface with the existing Earth texture."""
    figure.data = tuple(
        trace for trace in figure.data if getattr(trace, "name", None) != "Earth"
    )
    image = (
        Image.open(image_path)
        .convert("RGB")
        .resize((360, 181), Image.Resampling.LANCZOS)
    )
    quantised = image.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    surface_colour = [
        [cast(int, quantised.getpixel((x, y))) for x in range(360)] for y in range(181)
    ]
    palette = quantised.getpalette()
    if palette is None:
        raise ValueError(f"Could not create colour palette from {image_path}")

    colour_count = int(max(max(row) for row in surface_colour)) + 1
    colourscale = [
        [
            index / max(colour_count - 1, 1),
            f"rgb({palette[index * 3]},{palette[index * 3 + 1]},{palette[index * 3 + 2]})",
        ]
        for index in range(colour_count)
    ]
    earth_radius = float(EARTH_RADIUS) * body_radius_scale / distance_scale
    longitudes = [-math.pi + TWO_PI * index / 359 for index in range(360)]
    latitudes = [math.pi / 2 - math.pi * index / 180 for index in range(181)]
    x, y, z = [], [], []
    for latitude in latitudes:
        x_row, y_row, z_row = [], [], []
        for longitude in longitudes:
            x_row.append(earth_radius * math.cos(latitude) * math.cos(longitude))
            y_row.append(earth_radius * math.cos(latitude) * math.sin(longitude))
            z_row.append(earth_radius * math.sin(latitude))
        x.append(x_row)
        y.append(y_row)
        z.append(z_row)
    figure.add_trace(
        go.Surface(
            x=x,
            y=y,
            z=z,
            surfacecolor=surface_colour,
            colorscale=colourscale,
            cmin=0,
            cmax=max(colour_count - 1, 1),
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
            lightposition={"x": 100_000, "y": 100_000, "z": 100_000},
        )
    )
    return figure


@dataclass(frozen=True)
class CentralBody3DConfig:
    name: str
    target: HorizonsCommandTarget
    radius: Distance
    gravitational_parameter: GravitationalParameter
    radius_scale: float
    distance_scale: float
    opacity: float = 0.7


SUN_RADIUS = Distance(Scalar(696_340.0 * 1_000.0))
SUN_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(1.32712440018e20))

CENTRAL_BODIES = {
    HorizonsCommandTarget.EARTH: CentralBody3DConfig(
        name="Earth",
        target=HorizonsCommandTarget.EARTH,
        radius=EARTH_RADIUS,
        gravitational_parameter=EARTH_MU,
        radius_scale=EARTH_BODY_RADIUS_SCALE,
        distance_scale=EARTH_DISTANCE_SCALE,
    ),
    HorizonsCommandTarget.SUN: CentralBody3DConfig(
        name="Sun",
        target=HorizonsCommandTarget.SUN,
        radius=SUN_RADIUS,
        gravitational_parameter=SUN_GRAVITATIONAL_PARAMETER,
        radius_scale=SUN_RADIUS_SCALE,
        distance_scale=SOLAR_DISTANCE_SCALE,
        opacity=0.6,
    ),
}

BODY_RADII_METRES = {
    HorizonsCommandTarget.MOON: 1_737.4 * 1_000.0,
    HorizonsCommandTarget.MERCURY: 2_439.7 * 1_000.0,
    HorizonsCommandTarget.VENUS: 6_051.8 * 1_000.0,
    HorizonsCommandTarget.EARTH: 6_371.0 * 1_000.0,
    HorizonsCommandTarget.MARS: 3_389.5 * 1_000.0,
    HorizonsCommandTarget.JUPITER: 69_911.0 * 1_000.0,
    HorizonsCommandTarget.SATURN: 58_232.0 * 1_000.0,
    HorizonsCommandTarget.URANUS: 25_362.0 * 1_000.0,
    HorizonsCommandTarget.NEPTUNE: 24_622.0 * 1_000.0,
}

DEFAULT_SOLAR_SYSTEM_BODIES = [
    HorizonsCommandTarget.MERCURY,
    HorizonsCommandTarget.VENUS,
    HorizonsCommandTarget.EARTH,
    HorizonsCommandTarget.MARS,
    HorizonsCommandTarget.JUPITER,
    HorizonsCommandTarget.SATURN,
    HorizonsCommandTarget.URANUS,
    HorizonsCommandTarget.NEPTUNE,
]


def orbiting_body_from_horizons_target(
    target: HorizonsCommandTarget,
    *,
    radius_scale: float,
) -> BodyPlotConfig:
    try:
        radius_metres = BODY_RADII_METRES[target]
    except KeyError as error:
        raise ValueError(
            f"No display radius is configured for {target.name}."
        ) from error

    return BodyPlotConfig(
        name=target.name.title(),
        target_object=target,
        radius=Distance(Scalar(radius_metres)),
        radius_scale=radius_scale,
    )


def _satellite_bodies(
    orbits: list[Orbit], radius: Distance, radius_scale: float
) -> list[BodyPlotConfig]:
    return [
        BodyPlotConfig(
            name=orbit.name,
            target_object=orbit.elements,
            radius=radius,
            radius_scale=radius_scale,
        )
        for orbit in orbits
    ]


def _itrf_positions(orbits: list[Orbit], track_for_orbits: float) -> list[list]:
    positions = []
    for orbit in orbits:
        track_for_seconds = (
            orbital_period(orbit.elements.semi_major_axis) * track_for_orbits
        )
        gcrf_positions = [
            position_vector_at_time(orbit.elements, Second(Scalar(second)), EARTH_MU)
            for second in range(0, int(track_for_seconds), 60)
        ]
        positions.append(itrf_positions_from_gcrf_position(gcrf_positions, orbit.epoch))
    return positions


def build_3d_orbit_system_figure(
    *,
    central_body: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    horizons_bodies: list[HorizonsCommandTarget] | None = None,
    satellite_orbits: list[Orbit] | None = None,
    reference_frame: ReferenceFrame = "GCRF",
    distance_scale: float | None = None,
    body_radius_scale: float | None = None,
    orbit_points: int = ORBIT_POINTS,
    satellite_display_radius: Distance = SATELLITE_DISPLAY_RADIUS,
    track_for_orbits: float = 3.0,
) -> go.Figure:
    """Build one 3D view for Horizons bodies and/or supplied satellite orbits.

    ICRF and GCRF currently use the same inertial propagation/display path. ITRF
    transforms satellite positions into Earth-fixed coordinates and is therefore
    currently limited to Earth-centred satellite plots.
    """
    if reference_frame not in {"ICRF", "GCRF", "ITRF"}:
        raise ValueError("reference_frame must be ICRF, GCRF, or ITRF.")

    try:
        central = CENTRAL_BODIES[central_body]
    except KeyError as error:
        raise ValueError(
            f"No central-body configuration for {central_body.name}."
        ) from error

    selected_bodies = horizons_bodies or []
    current_satellites = [
        orbit_at_current_epoch(orbit) for orbit in satellite_orbits or []
    ]

    if reference_frame == "ITRF":
        if central_body is not HorizonsCommandTarget.EARTH:
            raise ValueError(
                "ITRF is currently supported only for Earth-centred plots."
            )
        if selected_bodies:
            raise ValueError(
                "ITRF currently supports satellite tracks, not Horizons bodies."
            )
        if not current_satellites:
            raise ValueError("At least one satellite orbit is required for ITRF.")

        settings = OrbitPlotSettings(
            centre=central.target,
            gravitational_parameter=central.gravitational_parameter,
            distance_scale=distance_scale or central.distance_scale,
            orbit_points=orbit_points,
            start_time=datetime.datetime.now(),
            add_prediction_to_orbit=False,
        )
        figure = build_3d_itrf_orbit_figure(
            settings=settings,
            itrf_positions=_itrf_positions(current_satellites, track_for_orbits),
            title=(
                f"{current_satellites[0].name} ITRF orbit | "
                f"Source: {current_satellites[0].source.value} | "
                f"Orbits: {track_for_orbits}"
                f"<br>{orbit_description_from_elements(current_satellites[0].elements)} @ Epoch"
            ),
            central_body_name=central.name,
            central_body_radius=central.radius,
            central_body_radius_scale=body_radius_scale or central.radius_scale,
            orbit_name=[orbit.name for orbit in current_satellites],
            central_body_opacity=central.opacity,
        )
        return _add_textured_earth(
            figure,
            distance_scale=settings.distance_scale,
            body_radius_scale=body_radius_scale or central.radius_scale,
        )

    # Horizons state vectors and the supplied orbital elements share this inertial
    # path; the selected reference frame remains explicit in the title/API.
    settings = OrbitPlotSettings(
        centre=central.target,
        gravitational_parameter=central.gravitational_parameter,
        distance_scale=distance_scale or central.distance_scale,
        orbit_points=orbit_points,
        start_time=datetime.datetime.now(),
        time_offset=(
            datetime.timedelta(days=15) if selected_bodies else datetime.timedelta()
        ),
    )
    radius_scale = body_radius_scale or (
        PLANET_RADIUS_SCALE
        if central_body is HorizonsCommandTarget.SUN
        else central.radius_scale
    )
    bodies = [
        orbiting_body_from_horizons_target(target, radius_scale=radius_scale)
        for target in selected_bodies
    ]
    bodies.extend(
        _satellite_bodies(current_satellites, satellite_display_radius, radius_scale)
    )

    if not bodies:
        raise ValueError("Select at least one Horizons body or satellite orbit.")

    title = f"{central.name}-centred {reference_frame} orbit system"
    if current_satellites:
        title += (
            f" | {current_satellites[0].name} "
            f"({current_satellites[0].source.value})"
            f"<br>{orbit_description_from_elements(current_satellites[0].elements)}"
        )

    return build_3d_orbit_figure(
        settings=settings,
        title=title,
        central_body_name=central.name,
        central_body_radius=central.radius,
        central_body_radius_scale=body_radius_scale or central.radius_scale,
        central_body_opacity=central.opacity,
        orbiting_bodies=bodies,
    )
