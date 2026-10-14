from __future__ import annotations

import datetime
import math
from dataclasses import replace
from pathlib import Path

import plotly.graph_objects as go
from astronomy_types import (
    Distance,
    Epoch,
    GravitationalParameter,
    OrbitalElements,
    PositionVector,
    Scalar,
    Second,
    Vector3D,
)
from plotly.basedatatypes import BaseTraceType

from afmaths.constants import EARTH_MU, EARTH_RADIUS, TWO_PI
from afmaths.operation import interval_points
from afmaths.physics.space.astronomy.time_functions import (
    julian_date_delta,
    julian_date_now,
    seconds_from_julian_date_delta,
)
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import EARTH_MU
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    orbital_elements_from_state_vectors,
)
from afmaths.physics.space.celestial_mechanics.state_vector import state_vector_at_time
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.celestial_mechanics.utils import generate_all_orbit_positions
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
)
from afmaths.physics.space.external.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)
from afmaths.physics.space.type_conversion_helpers import (
    fulldate_from_python_datetime,
    make_vector3d,
)
from afmaths.visualisations.visualisation_types import (
    BodyPlotConfig,
    Orbit,
    OrbitPlotSettings,
    PlotCoordinateSystem,
    PlotOriginConfig,
    ReferenceFrame,
)


def orbit_elements(orbit: Orbit) -> OrbitalElements:
    if isinstance(orbit.description, OrbitalElements):
        return orbit.description

    return orbital_elements_from_tle(orbit.description)


def orbit_at_current_epoch(
    orbit: Orbit,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> Orbit:
    return replace(
        orbit,
        epoch=Epoch(julian_date_now()),
        description=orbital_elements_from_state_vectors(
            state_vector_at_time(
                orbit_elements(orbit),
                seconds_from_julian_date_delta(julian_date_delta(orbit.epoch)),
                gravitational_parameter,
            ),
            mu=gravitational_parameter,
        ),
    )


def make_3d_orbit_figure(
    traces: list,
    title: str,
    distance_scale: float,
) -> go.Figure:
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=title,
        scene={
            "xaxis_title": f"X ({distance_scale:,} m units)",
            "yaxis_title": f"Y ({distance_scale:,} m units)",
            "zaxis_title": f"Z ({distance_scale:,} m units)",
            "aspectmode": "data",
        },
    )

    return fig


def plot_sphere_surface(
    radius: Distance,
    centre: PositionVector | None = None,
    resolution: int = 50,
) -> Vector3D:
    u = interval_points(0, TWO_PI, resolution)
    v = interval_points(0, math.pi, resolution)

    centre_x = 0 if centre is None else centre.x
    centre_y = 0 if centre is None else centre.y
    centre_z = 0 if centre is None else centre.z

    sphere_x = [
        [centre_x + radius * math.cos(u_i) * math.sin(v_j) for v_j in v] for u_i in u
    ]

    sphere_y = [
        [centre_y + radius * math.sin(u_i) * math.sin(v_j) for v_j in v] for u_i in u
    ]

    sphere_z = [[centre_z + radius * math.cos(v_j) for v_j in v] for _ in u]

    return make_vector3d(sphere_x, sphere_y, sphere_z)


def scaled_radius(
    radius: Distance,
    radius_scale: float,
    distance_scale: float,
) -> Distance:
    return Distance(Scalar((radius * radius_scale) / distance_scale))


def add_body_surface(
    name: str,
    radius: Distance,
    radius_scale: float,
    distance_scale: float,
    position: PositionVector | None = None,
    opacity: float = 0.9,
) -> go.Surface:
    surface = plot_sphere_surface(
        scaled_radius(radius, radius_scale, distance_scale),
        position,
    )

    return go.Surface(
        x=surface.x,
        y=surface.y,
        z=surface.z,
        name=name,
        opacity=opacity,
        showscale=False,
    )


def distance_to_scale_distance(
    distance: Distance,
    distance_scale: float,
) -> Distance:
    """Both distance and scale must be in the same unit."""
    return Distance(Scalar(distance / distance_scale))


def scale_position(position: PositionVector, distance_scale: float) -> Vector3D:
    return make_vector3d(
        distance_to_scale_distance(Distance(position.x), distance_scale),
        distance_to_scale_distance(Distance(position.y), distance_scale),
        distance_to_scale_distance(Distance(position.z), distance_scale),
    )


def add_itrf_orbit_trace(
    name: str,
    itrf_positions: list[PositionVector],
    distance_scale: float,
) -> go.Scatter3d:
    x = []
    y = []
    z = []

    for position in itrf_positions:
        scaled = scale_position(position, distance_scale)
        x.append(scaled.x)
        y.append(scaled.y)
        z.append(scaled.z)

    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=name,
    )


def build_3d_itrf_orbit_figure(
    settings: OrbitPlotSettings,
    itrf_positions: list[list[PositionVector]],
    title: str = "ITRS orbit view",
    central_body_name: str = "Earth",
    central_body_radius: Distance = EARTH_RADIUS,
    central_body_radius_scale: float = 5.0,
    orbit_name: list[str] | None = None,
    central_body_opacity: float = 0.7,
) -> go.Figure:
    orbit_names = orbit_name or ["orbit"] * len(itrf_positions)
    if len(orbit_names) != len(itrf_positions):
        raise ValueError("orbit_name must contain one name per ITRF position set.")

    traces: list[BaseTraceType] = [
        add_body_surface(
            central_body_name,
            central_body_radius,
            central_body_radius_scale,
            settings.distance_scale,
            opacity=central_body_opacity,
        ),
    ]

    for index, positions in enumerate(itrf_positions):
        traces.append(
            add_itrf_orbit_trace(
                f"SAT: {orbit_names[index]} ITRS track",
                positions,
                settings.distance_scale,
            )
        )

    return make_3d_orbit_figure(
        traces,
        title,
        settings.distance_scale,
    )


def add_orbit_line_trace(
    name: str,
    orbital_elements: OrbitalElements,
    distance_scale: float,
    orbit_points: int,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> go.Scatter3d:
    x = []
    y = []
    z = []

    for position in generate_all_orbit_positions(
        orbital_elements,
        orbit_points,
        gravitational_parameter,
    ):
        scaled = scale_position(position, distance_scale)

        x.append(scaled.x)
        y.append(scaled.y)
        z.append(scaled.z)

    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=f"{name} orbit",
    )


def add_orbiting_body_to_traces(
    traces: list,
    body: BodyPlotConfig,
    settings: OrbitPlotSettings,
    opacity: float = 0.9,
) -> None:

    if isinstance(body.target_object, HorizonsCommandTarget):

        if settings.centre is None:
            raise ValueError("Horizons bodies require a Horizons-backed origin.")
        horizon_state_vectors = get_object_state_vectors_from_horizon(
            target=HorizonsCommandTarget(body.target_object),
            centre=settings.centre,
            start_time=fulldate_from_python_datetime(settings.start_time),
            stop_time=fulldate_from_python_datetime(settings.stop_time),
        )

        if len(horizon_state_vectors) < 1:
            raise ValueError(f"No Horizons state vectors returned for {body.name}")

        orbital_elements = orbital_elements_from_state_vectors(
            horizon_state_vectors[0],
            mu=settings.gravitational_parameter,
        )
    elif isinstance(body.target_object, OrbitalElements):
        orbital_elements = body.target_object
    else:
        print(body.target_object)
        raise TypeError("Orbital elements ain't right")

    model_current_state = state_vector_at_time(
        orbital_elements,
        Second(Scalar(0)),
        settings.gravitational_parameter,
    )

    traces.append(
        add_orbit_line_trace(
            body.name,
            orbital_elements,
            settings.distance_scale,
            settings.orbit_points,
            settings.gravitational_parameter,
        )
    )

    traces.append(
        add_body_surface(
            body.name,
            body.radius,
            body.radius_scale,
            settings.distance_scale,
            position=scale_position(
                model_current_state.position,
                settings.distance_scale,
            ),
            opacity=opacity,
        )
    )

    if not settings.add_prediction_to_orbit:
        return

    model_prediction_state = state_vector_at_time(
        orbital_elements,
        settings.time_offset_seconds,
        settings.gravitational_parameter,
    )

    traces.append(
        add_body_surface(
            body.name + " prediction",
            body.radius,
            body.radius_scale,
            settings.distance_scale,
            position=scale_position(
                model_prediction_state.position,
                settings.distance_scale,
            ),
            opacity=opacity,
        )
    )


def build_3d_orbit_figure(
    settings: OrbitPlotSettings,
    title: str,
    central_body_name: str,
    central_body_radius: Distance,
    central_body_radius_scale: float,
    orbiting_bodies: list[BodyPlotConfig],
    central_body_opacity: float = 0.7,
) -> go.Figure:

    traces = [
        add_body_surface(
            central_body_name,
            central_body_radius,
            central_body_radius_scale,
            settings.distance_scale,
            opacity=central_body_opacity,
        )
    ]

    for body in orbiting_bodies:
        add_orbiting_body_to_traces(traces, body, settings)

    return make_3d_orbit_figure(
        traces,
        title,
        settings.distance_scale,
    )


from typing import cast

from PIL import Image

from afmaths.constants import EARTH_MU, EARTH_RADIUS
from afmaths.physics.space.celestial_mechanics.state_vector import (
    position_vector_at_time,
)
from afmaths.physics.space.engineering.astrodynamics.utils import (
    orbit_description_from_elements,
)
from afmaths.physics.space.transformations import itrf_positions_from_gcrf_position

EARTH_DISTANCE_SCALE = 1_000.0
SOLAR_DISTANCE_SCALE = 1_000_000_000.0
EARTH_BODY_RADIUS_SCALE = 1.0
PLANET_RADIUS_SCALE = 2_000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 100
SATELLITE_DISPLAY_RADIUS = Distance(Scalar(200_000.0))
EARTH_IMAGE_PATH = Path(__file__).with_name("Earth-hires.jpg")


def _add_textured_body(
    figure: go.Figure,
    *,
    name: str,
    radius: Distance,
    distance_scale: float,
    body_radius_scale: float,
    image_path: Path,
) -> go.Figure:
    """Replace the named sphere with an equirectangular texture."""
    figure.data = tuple(
        trace for trace in figure.data if getattr(trace, "name", None) != name
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
    body_radius = float(radius) * body_radius_scale / distance_scale
    longitudes = [-math.pi + TWO_PI * index / 359 for index in range(360)]
    latitudes = [math.pi / 2 - math.pi * index / 180 for index in range(181)]
    x, y, z = [], [], []
    for latitude in latitudes:
        x_row, y_row, z_row = [], [], []
        for longitude in longitudes:
            x_row.append(body_radius * math.cos(latitude) * math.cos(longitude))
            y_row.append(body_radius * math.cos(latitude) * math.sin(longitude))
            z_row.append(body_radius * math.sin(latitude))
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
            name=name,
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


ICRF_COORDINATE_SYSTEM = PlotCoordinateSystem(
    name="ICRF",
    axes="ICRF-aligned",
    is_inertial=True,
)
ITRF_COORDINATE_SYSTEM = PlotCoordinateSystem(
    name="ITRF",
    axes="Earth-fixed ITRF",
    is_inertial=False,
)


def _coordinate_system_for(
    *,
    reference_frame: ReferenceFrame,
    origin: HorizonsCommandTarget | None,
) -> PlotCoordinateSystem:
    """Return the implemented coordinate system for a frame/origin combination.
    The current inertial Horizons path uses ICRF-aligned axes. Translating its
    origin to Earth or Sun does not turn it into GCRF; a GCRF transformation is
    intentionally rejected until that transformation is implemented.
    """
    if reference_frame == "ICRF":
        return ICRF_COORDINATE_SYSTEM
    if reference_frame == "GCRF":
        raise ValueError(
            "GCRF is not implemented: the current inertial path uses "
            "ICRF-aligned axes and does not apply an ICRF-to-GCRF "
            "transformation. Use reference_frame='ICRF' with "
            "origin_body=EARTH for an Earth-centred inertial plot."
        )
    if origin is not HorizonsCommandTarget.EARTH:
        raise ValueError("ITRF is currently supported only for Earth-centred plots.")
    return ITRF_COORDINATE_SYSTEM


def _orbit_system_title(
    *,
    origin: PlotOriginConfig,
    coordinate_system: PlotCoordinateSystem,
) -> str:
    motion = (
        "inertial" if coordinate_system.is_inertial else "Earth-fixed (non-inertial)"
    )
    return (
        f"Origin: {origin.name} centre | Axes: {coordinate_system.axes} | "
        f"Motion: {motion}"
    )


SUN_RADIUS = Distance(Scalar(696_340.0 * 1_000.0))
SUN_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(1.32712440018e20))
PLOT_ORIGINS = {
    HorizonsCommandTarget.EARTH: PlotOriginConfig(
        name="Earth",
        target=HorizonsCommandTarget.EARTH,
        radius=EARTH_RADIUS,
        gravitational_parameter=EARTH_MU,
        radius_scale=EARTH_BODY_RADIUS_SCALE,
        distance_scale=EARTH_DISTANCE_SCALE,
    ),
    HorizonsCommandTarget.SUN: PlotOriginConfig(
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
    HorizonsCommandTarget.MOON,
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
            target_object=orbit_elements(orbit),
            radius=radius,
            radius_scale=radius_scale,
        )
        for orbit in orbits
    ]


def _itrf_positions(orbits: list[Orbit], track_for_orbits: float) -> list[list]:
    positions = []
    for orbit in orbits:
        elements = orbit_elements(orbit)
        track_for_seconds = orbital_period(elements.semi_major_axis) * track_for_orbits
        gcrf_positions = [
            position_vector_at_time(elements, Second(Scalar(second)), EARTH_MU)
            for second in range(0, int(track_for_seconds), 60)
        ]
        positions.append(itrf_positions_from_gcrf_position(gcrf_positions, orbit.epoch))
    return positions


def build_3d_orbit_system_figure(
    *,
    origin_body: HorizonsCommandTarget | PlotOriginConfig = HorizonsCommandTarget.EARTH,
    horizons_bodies: list[HorizonsCommandTarget] | None = None,
    satellite_orbits: list[Orbit] | None = None,
    reference_frame: ReferenceFrame = "ICRF",
    distance_scale: float | None = None,
    body_radius_scale: float | None = None,
    orbit_points: int = ORBIT_POINTS,
    satellite_display_radius: Distance | None = None,
    track_for_orbits: float = 3.0,
) -> go.Figure:
    """Build a 3D plot with an explicit origin, axis system, and motion type.
    ICRF uses ICRF-aligned axes and an inertial display path, translated to
    the requested origin. ITRF uses Earth-fixed, non-inertial axes and is
    limited to supplied Earth-satellite tracks. GCRF is rejected until an
    ICRF-to-GCRF transformation is implemented.
    """
    if reference_frame not in {"ICRF", "GCRF", "ITRF"}:
        raise ValueError("reference_frame must be ICRF, GCRF, or ITRF.")
    if isinstance(origin_body, PlotOriginConfig):
        central = origin_body
    else:
        try:
            central = PLOT_ORIGINS[origin_body]
        except KeyError as error:
            raise ValueError(
                f"{origin_body.name} is not a supported plot origin. Supported "
                f"origins: {', '.join(target.name for target in PLOT_ORIGINS)}."
            ) from error
    coordinate_system = _coordinate_system_for(
        reference_frame=reference_frame,
        origin=central.target,
    )
    selected_bodies = horizons_bodies or []
    if central.target is None and selected_bodies:
        raise ValueError(
            "Horizons bodies require an origin with a Horizons target; "
            "a custom sphere has no Horizons ephemeris reference."
        )
    # Custom simulation epochs (e.g. KSP UT) are not wall-clock Julian dates.
    current_satellites = [
        (
            orbit_at_current_epoch(orbit, central.gravitational_parameter)
            if central.target is not None
            else orbit
        )
        for orbit in satellite_orbits or []
    ]
    if coordinate_system.name == "ITRF":
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
                f"{_orbit_system_title(origin=central, coordinate_system=coordinate_system)} | "
                f"Target: {current_satellites[0].name} | "
                f"Orbits: {track_for_orbits}"
                f"<br>{orbit_description_from_elements(orbit_elements(current_satellites[0]))} @ Epoch"
            ),
            central_body_name=central.name,
            central_body_radius=central.radius,
            central_body_radius_scale=body_radius_scale or central.radius_scale,
            orbit_name=[orbit.name for orbit in current_satellites],
            central_body_opacity=central.opacity,
        )
        return _add_textured_body(
            figure,
            name=central.name,
            radius=central.radius,
            distance_scale=settings.distance_scale,
            body_radius_scale=body_radius_scale or central.radius_scale,
            image_path=central.texture_path or EARTH_IMAGE_PATH,
        )
    # Horizons state vectors and supplied orbital elements use the implemented
    # ICRF-aligned inertial path, translated to the selected origin.
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
        if origin_body is HorizonsCommandTarget.SUN
        else central.radius_scale
    )
    bodies = [
        orbiting_body_from_horizons_target(target, radius_scale=radius_scale)
        for target in selected_bodies
    ]
    bodies.extend(
        _satellite_bodies(
            current_satellites,
            satellite_display_radius or Distance(Scalar(float(central.radius) * 0.01)),
            radius_scale,
        )
    )
    # A standalone sphere is also a useful visualisation.
    title = _orbit_system_title(
        origin=central,
        coordinate_system=coordinate_system,
    )
    if current_satellites:
        title += (
            f" | Target: {current_satellites[0].name}"
            f"<br>{orbit_description_from_elements(orbit_elements(current_satellites[0]))}"
        )
    figure = build_3d_orbit_figure(
        settings=settings,
        title=title,
        central_body_name=central.name,
        central_body_radius=central.radius,
        central_body_radius_scale=body_radius_scale or central.radius_scale,
        central_body_opacity=central.opacity,
        orbiting_bodies=bodies,
    )
    if central.texture_path is not None and central.texture_path.is_file():
        return _add_textured_body(
            figure,
            name=central.name,
            radius=central.radius,
            distance_scale=settings.distance_scale,
            body_radius_scale=body_radius_scale or central.radius_scale,
            image_path=central.texture_path,
        )
    return figure
