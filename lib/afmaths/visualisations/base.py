from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import datetime
import math

import plotly.graph_objects as go

from astronomy_types import (
    Anomaly,
    Coordinate2D,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Scalar,
    Second,
    Velocity,
    VelocityVector,
)

from afmaths.constants import DeltaV, Mass
from afmaths.geometry.geometry import (
    calculate_foci,
    semi_minor_axis,
)
from afmaths.geometry.transformations import translate_ellipse
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    generate_all_orbit_positions,
    orbit_state_vector_prediction,
    orbital_elements_from_state_vectors,
)
from afmaths.physics.space.type_conversion_helpers import (
    python_datetime_to_fulldate,
    python_timedelta_to_seconds,
)
from afmaths.physics.space.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)

from afmaths.visualisations.helpers import (
    PlotOrbital2DSettings,
    plot_centre,
    scale_position,
)


# Subject: visualisation configuration, with astronomy-specific target metadata.
# Stores the plotting/display inputs for a body: label, Horizons target or elements, physical radius, and visual radius scale.
# This is mostly visualisation config, but it depends on Horizons/orbital concepts.
@dataclass(frozen=True)
class BodyPlotConfig:
    name: str
    target: HorizonsCommandTarget | OrbitalElements
    radius_km: float
    radius_scale: float


# Subject: visualisation configuration, with time/orbit-propagation settings.
# Stores the 3D orbit plot setup: centre body, gravitational parameter, scale, orbit sample count, and time interval.
# The time_offset_seconds property is a unit conversion for propagation, so the class straddles plotting config and orbital simulation config.
@dataclass(frozen=True)
class OrbitPlotSettings:
    centre: HorizonsCommandTarget
    gravitational_parameter: GravitationalParameter
    distance_scale_km: float
    orbit_points: int
    start_time: datetime.datetime
    time_offset: datetime.timedelta
    add_prediction_to_orbit: bool = True

    # Subject: time interval convenience for ephemeris/orbit propagation.
    # Computes the stop datetime by adding the configured time offset to the start time.
    # Not visualisation-specific.
    @property
    def stop_time(self) -> datetime.datetime:
        return self.start_time + self.time_offset

    # Subject: unit conversion for propagation.
    # Converts the configured datetime.timedelta into the astronomy_types Second wrapper.
    # This is a unit adapter for physics/orbit-propagation calls.
    @property
    def time_offset_seconds(self) -> Second:
        return Second(Scalar(python_timedelta_to_seconds(self.time_offset)))


# Subject: planar geometry / coordinate transform.
# Rotates a 2D vector/relative coordinate about the origin by angle radians using the standard 2D rotation matrix.
# Generic coordinate transform; not specifically visualisation or orbital mechanics.
def rotate_relative_coordinate(
    coordinate: Coordinate2D,
    angle: float,
) -> Coordinate2D:
    return Coordinate2D(
        coordinate.x * math.cos(angle) - coordinate.y * math.sin(angle),
        coordinate.x * math.sin(angle) + coordinate.y * math.cos(angle),
    )


# Subject: planar geometry / coordinate transform.
# Translates a local 2D coordinate by adding an origin offset.
# Generic geometry helper; not celestial mechanics and not Plotly-specific.
def translate_coordinate(
    origin: Coordinate2D,
    coordinate: Coordinate2D,
) -> Coordinate2D:
    return Coordinate2D(
        origin.x + coordinate.x,
        origin.y + coordinate.y,
    )


# Subject: coordinate transform between orbital/perifocal coordinates and plot coordinates.
# Converts a local ellipse coordinate into the plot frame by: shifting it relative to the primary focus, rotating by argument of periapsis, then translating to the plotted primary focus.
# This mixes orbital frame semantics with generic 2D transforms; likely belongs in an orbit-coordinate-transform helper rather than visualisation helpers.
def local_to_plot_coordinate_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    local_coordinate: Coordinate2D,
) -> Coordinate2D:
    primary_focus, _ = calculate_foci(
        elements.semi_major_axis,
        elements.eccentricity,
    )

    local_relative_to_primary_focus = Coordinate2D(
        local_coordinate.x - primary_focus.x,
        local_coordinate.y - primary_focus.y,
    )

    rotated = rotate_relative_coordinate(
        local_relative_to_primary_focus,
        elements.argument_of_periapsis,
    )

    return translate_coordinate(
        primary_focus_plot_coordinate,
        rotated,
    )


# Subject: orbital geometry projected into plot coordinates.
# Computes where the primary focus of an orbit should appear on the plot by mapping the local primary focus to the plot centre.
# This is mostly a visualisation adapter around orbital geometry.
def primary_focus_coordinates_for_elements(
    settings: PlotOrbital2DSettings,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        plot_centre(settings),
        elements,
        calculate_foci(
            elements.semi_major_axis,
            elements.eccentricity,
        )[0],
    )


# Subject: orbital geometry projected into plot coordinates.
# Computes the plotted location of the secondary focus by transforming the local secondary focus into the plot frame.
# This is visualisation-adapter logic over celestial/conic geometry.
def secondary_focus_coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        calculate_foci(
            elements.semi_major_axis,
            elements.eccentricity,
        )[1],
    )


# Subject: orbital geometry / perifocal coordinate conversion.
# Converts an eccentric anomaly into a local ellipse coordinate using semi-major/minor axes, then maps that coordinate into the plot frame.
# This is a core orbital-coordinate helper; the underlying calculation should probably reuse a celestial-mechanics/orbit-position helper if one exists.
def coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    E: EccentricAnomaly,
) -> Coordinate2D:
    local_coordinate = translate_ellipse(
        Coordinate2D(Scalar(0), Scalar(0)),
        elements.semi_major_axis,
        semi_minor_axis(elements.semi_major_axis, elements.eccentricity),
        E,
    )

    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        local_coordinate,
    )


def tangent_vector_for_plot(
    primary_focus_plot_coordinate: Coordinate2D,
    plot_elements: OrbitalElements,
    E: EccentricAnomaly,
) -> VelocityVector:
    delta = 0.001

    current = coordinates_for_elements(
        primary_focus_plot_coordinate,
        plot_elements,
        E,
    )

    next_point = coordinates_for_elements(
        primary_focus_plot_coordinate,
        plot_elements,
        EccentricAnomaly(Anomaly(Radians(Scalar(float(E) + delta)))),
    )

    return VelocityVector(
        Velocity(Scalar(next_point.x - current.x)),
        Velocity(Scalar(next_point.y - current.y)),
        Velocity(Scalar(0)),
    )


# Subject: plotting adapter for transfer arcs.
# Normalises start/end eccentric anomaly values so Plotly draws the intended arc across the 2π wrap boundary.
# This is visualisation-specific handling of orbital angle data.
def transfer_arc_angles(
    start_eccentric_anomaly: EccentricAnomaly,
    arrival_eccentric_anomaly: EccentricAnomaly,
) -> tuple[float, float]:
    start = float(start_eccentric_anomaly)
    end = float(arrival_eccentric_anomaly)

    if end <= start:
        return start, end + 2 * math.pi

    return start, end


# Subject: visualisation plus orbit propagation.
# Generates orbit positions from OrbitalElements, scales them to plot units, and returns a Plotly 3D line trace.
# This mixes orbital propagation with Plotly rendering; ideally propagation happens outside and this function only receives coordinates.
def add_orbit_line_trace(
    name: str,
    orbital_elements: OrbitalElements,
    distance_scale_km: float,
    orbit_points: int,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> go.Scatter3d:
    x = []
    y = []
    z = []

    for position in generate_all_orbit_positions(
        orbital_elements,
        orbit_points,
        gravitational_parameter,
    ):
        scaled = scale_position(position, distance_scale_km)

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


# Subject: high-level 3D orbit visualisation orchestration.
# Fetches Horizons state vectors, converts them to orbital elements, propagates current/predicted states, and appends orbit/body Plotly traces.
# This heavily mixes ephemeris IO, celestial mechanics, propagation, scaling, and rendering. It is not a base helper.
def add_orbiting_body_to_traces(
    traces: list,
    body: BodyPlotConfig,
    settings: OrbitPlotSettings,
    opacity: float = 0.9,
) -> None:
    from afmaths.visualisations.helpers import add_body_surface

    horizon_state_vectors = get_object_state_vectors_from_horizon(
        target=HorizonsCommandTarget(body.target),
        centre=settings.centre,
        start_time=python_datetime_to_fulldate(settings.start_time),
        stop_time=python_datetime_to_fulldate(settings.stop_time),
    )

    if len(horizon_state_vectors) < 1:
        raise ValueError(f"No Horizons state vectors returned for {body.name}")

    orbital_elements = orbital_elements_from_state_vectors(
        horizon_state_vectors[0],
        mu=settings.gravitational_parameter,
    )

    model_current_state = orbit_state_vector_prediction(
        orbital_elements,
        Second(Scalar(0)),
        settings.gravitational_parameter,
    )

    traces.append(
        add_orbit_line_trace(
            body.name,
            orbital_elements,
            settings.distance_scale_km,
            settings.orbit_points,
            settings.gravitational_parameter,
        )
    )

    traces.append(
        add_body_surface(
            body.name,
            body.radius_km,
            body.radius_scale,
            settings.distance_scale_km,
            position=scale_position(
                model_current_state.position,
                settings.distance_scale_km,
            ),
            opacity=opacity,
        )
    )

    if not settings.add_prediction_to_orbit:
        return

    model_prediction_state = orbit_state_vector_prediction(
        orbital_elements,
        settings.time_offset_seconds,
        settings.gravitational_parameter,
    )

    traces.append(
        add_body_surface(
            body.name + " prediction",
            body.radius_km,
            body.radius_scale,
            settings.distance_scale_km,
            position=scale_position(
                model_prediction_state.position,
                settings.distance_scale_km,
            ),
            opacity=opacity,
        )
    )


# Subject: high-level visualisation composition.
# Builds a complete 3D orbit figure by creating the central body trace, adding each orbiting body, and applying the final 3D layout.
# This is a demo/figure-builder function, not core physics; it could stay in a specific 3D visualiser module.
def build_3d_orbit_figure(
    settings: OrbitPlotSettings,
    title: str,
    central_body_name: str,
    central_body_radius_km: float,
    central_body_radius_scale: float,
    orbiting_bodies: list[BodyPlotConfig],
    central_body_opacity: float = 0.7,
) -> go.Figure:
    from afmaths.visualisations.helpers import add_body_surface, make_3d_orbit_figure

    traces = [
        add_body_surface(
            central_body_name,
            central_body_radius_km,
            central_body_radius_scale,
            settings.distance_scale_km,
            opacity=central_body_opacity,
        )
    ]

    for body in orbiting_bodies:
        add_orbiting_body_to_traces(traces, body, settings)

    return make_3d_orbit_figure(
        traces,
        title,
        settings.distance_scale_km,
    )
