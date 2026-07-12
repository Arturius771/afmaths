from __future__ import annotations

from dataclasses import dataclass, replace
import datetime
import math

import plotly.graph_objects as go

from astronomy_types import (
    Anomaly,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    PositionVector,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
    Velocity,
    VelocityVector,
)

from afmaths.geometry.geometry import semi_minor_axis
from afmaths.geometry.transformations import translate_ellipse
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    apoapsis_true_anomaly,
    generate_all_orbit_positions,
    orbital_elements_from_state_vectors,
    perifocal_position_at_ascending_node,
    perifocal_position_at_descending_node,
    perifocal_position_vector,
    periapsis_true_anomaly,
    state_vector_at_time,
)
from afmaths.physics.space.external.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)
from afmaths.physics.space.type_conversion_helpers import (
    make_true_anomaly,
    fulldate_from_python_datetime,
    seconds_from_python_timedelta,
)
from afmaths.visualisations.helpers import (
    PlotNode,
    PlotOrbital2DSettings,
    add_plot_nodes,
    figure_layout,
    figure_orbit_line,
    plot_origin,
    plot_max,
    plot_min,
    scale_position,
    distance_to_scale_distance,
)


# Subject: visualisation configuration, with astronomy-specific target metadata.
# Stores display inputs for a body: label, Horizons target/orbital elements,
# physical radius, and visual radius scale.
@dataclass(frozen=True)
class BodyPlotConfig:
    name: str
    target: HorizonsCommandTarget | OrbitalElements
    radius_km: float
    radius_scale: float


# Subject: visualisation configuration, with time/orbit-propagation settings.
# Stores the 3D orbit plot setup and exposes unit/time adapters needed by
# propagation code.
@dataclass(frozen=True)
class OrbitPlotSettings:
    centre: HorizonsCommandTarget
    gravitational_parameter: GravitationalParameter
    distance_scale_km: float
    orbit_points: int
    start_time: datetime.datetime
    time_offset: datetime.timedelta
    add_prediction_to_orbit: bool = True

    @property
    def stop_time(self) -> datetime.datetime:
        return self.start_time + self.time_offset

    @property
    def time_offset_seconds(self) -> Second:
        return Second(Scalar(seconds_from_python_timedelta(self.time_offset)))


# Subject: angle construction.
# Lightweight adapter from plain radians into the project anomaly wrapper type.
def eccentric_anomaly(value: float) -> EccentricAnomaly:
    return EccentricAnomaly(Anomaly(Radians(Scalar(value))))


# Subject: angle construction.
# Lightweight adapter from plain radians into the project anomaly wrapper type.
def true_anomaly(value: float) -> TrueAnomaly:
    return TrueAnomaly(Anomaly(Radians(Scalar(value))))


# Subject: angle normalisation.
# Generic radian normalisation for visualisation logic that compares orbit angles.
def normalise_angle_rad(angle: float) -> float:
    return angle % (2 * math.pi)


# Subject: anomaly conversion.
# Converts true anomaly to eccentric anomaly for elliptical orbit visualisations.
def eccentric_anomaly_from_true_anomaly(
    eccentricity: float,
    true_anomaly_value: TrueAnomaly,
) -> EccentricAnomaly:
    E = 2 * math.atan2(
        math.sqrt(1 - eccentricity) * math.sin(true_anomaly_value / 2),
        math.sqrt(1 + eccentricity) * math.cos(true_anomaly_value / 2),
    )

    return eccentric_anomaly(normalise_angle_rad(E))


# Subject: plot-unit adapter for orbital elements.
# Scales only the distance component of orbital elements for 2D visualisations.
def scale_orbital_elements_for_plot(
    orbital_elements: OrbitalElements,
    distance_scale: Distance,
) -> OrbitalElements:
    return replace(
        orbital_elements,
        semi_major_axis=SemiMajorAxis(
            distance_to_scale_distance(
                orbital_elements.semi_major_axis,
                distance_scale,
            )
        ),
    )


# Subject: planar geometry / coordinate transform.
# Rotates a 2D vector/relative coordinate about the origin by angle radians.
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
def translate_coordinate(
    origin: Coordinate2D,
    coordinate: Coordinate2D,
) -> Coordinate2D:
    return Coordinate2D(
        origin.x + coordinate.x,
        origin.y + coordinate.y,
    )


# Subject: ellipse-centre local coordinate -> focus-origin plot transform.
# Input local_coordinate is expressed in the local ellipse-centred coordinate system
# used by translate_ellipse. It is shifted so that the periapsis-side focus is
# the origin, rotated by argument of periapsis, then translated to the plotted
# primary focus. This keeps ω aligned with periapsis rather than apoapsis.
def primary_focus_local_coordinate_for_elements(
    elements: OrbitalElements,
) -> Coordinate2D:
    return Coordinate2D(
        Scalar(elements.semi_major_axis * elements.eccentricity),
        Scalar(0),
    )


# Subject: orbital geometry.
# Returns the opposite focus in the same ellipse-centred local coordinate system.
def secondary_focus_local_coordinate_for_elements(
    elements: OrbitalElements,
) -> Coordinate2D:
    return Coordinate2D(
        Scalar(-elements.semi_major_axis * elements.eccentricity),
        Scalar(0),
    )


def local_to_plot_coordinate_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    local_coordinate: Coordinate2D,
) -> Coordinate2D:
    primary_focus = primary_focus_local_coordinate_for_elements(elements)

    local_relative_to_primary_focus = Coordinate2D(
        local_coordinate.x - primary_focus.x,
        local_coordinate.y - primary_focus.y,
    )

    return translate_coordinate(
        primary_focus_plot_coordinate,
        rotate_relative_coordinate(
            local_relative_to_primary_focus,
            elements.argument_of_periapsis,
        ),
    )


# Subject: focus-origin perifocal position vector -> plot coordinate transform.
def position_to_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    position: PositionVector,
) -> Coordinate2D:
    return translate_coordinate(
        primary_focus_plot_coordinate,
        rotate_relative_coordinate(
            Coordinate2D(Scalar(position.x), Scalar(position.y)),
            elements.argument_of_periapsis,
        ),
    )


# Subject: orbital geometry projected into plot coordinates.
# Compatibility helper for ellipse-centre based plotting functions.
def secondary_focus_coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        secondary_focus_local_coordinate_for_elements(elements),
    )


# Subject: focus-origin orbital geometry projected into plot coordinates.
# Computes the secondary focus using the focus-to-focus distance, then applies the
# same focus-origin transform as the nodes/apsides/current position.
def secondary_focus_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    distance_between_foci = 2 * elements.semi_major_axis * elements.eccentricity

    return translate_coordinate(
        primary_focus_plot_coordinate,
        rotate_relative_coordinate(
            Coordinate2D(Scalar(-distance_between_foci), Scalar(0)),
            elements.argument_of_periapsis,
        ),
    )


# Subject: orbital geometry / eccentric-anomaly plotting.
# Converts an eccentric anomaly into a local ellipse coordinate and maps it into
# the plot frame. This follows the ellipse-centre convention used by transfer arc
# visualisations.
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


# Subject: orbital geometry / true-anomaly plotting.
# Uses the focus-origin perifocal position vector and the same plot transform used
# by nodes and apsides.
def plot_coordinate_for_true_anomaly(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    true_anomaly_value: TrueAnomaly,
) -> Coordinate2D:
    return position_to_plot_coordinate(
        primary_focus_plot_coordinate,
        elements,
        perifocal_position_vector(replace(elements, true_anomaly=true_anomaly_value)),
    )


# Subject: orbital geometry / apsides projected into plot coordinates.
def periapsis_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return plot_coordinate_for_true_anomaly(
        primary_focus_plot_coordinate,
        elements,
        periapsis_true_anomaly(),
    )


# Subject: orbital geometry / apsides projected into plot coordinates.
def apoapsis_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return plot_coordinate_for_true_anomaly(
        primary_focus_plot_coordinate,
        elements,
        apoapsis_true_anomaly(),
    )


# Subject: orbital geometry / nodes projected into plot coordinates.
def ascending_node_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return position_to_plot_coordinate(
        primary_focus_plot_coordinate,
        elements,
        perifocal_position_at_ascending_node(elements),
    )


# Subject: orbital geometry / nodes projected into plot coordinates.
def descending_node_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return position_to_plot_coordinate(
        primary_focus_plot_coordinate,
        elements,
        perifocal_position_at_descending_node(elements),
    )


# Subject: orbital geometry / current spacecraft position projected into plot coordinates.
def current_position_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return position_to_plot_coordinate(
        primary_focus_plot_coordinate,
        elements,
        perifocal_position_vector(elements),
    )


# Subject: orbital geometry / focus-origin orbit sampling.
# Generates a 2D orbital-plane line using true anomaly and the same transform as
# the marker points. This avoids mixing ellipse-centre and focus-origin pipelines.
def orbit_plot_coordinates(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    resolution: int,
) -> list[Coordinate2D]:
    if resolution < 3:
        raise ValueError("resolution must be at least 3")

    return [
        plot_coordinate_for_true_anomaly(
            primary_focus_plot_coordinate,
            elements,
            make_true_anomaly(2 * math.pi * index / resolution),
        )
        for index in range(resolution + 1)
    ]


# Subject: orbital geometry / derived plot markers.
def keplerian_element_plot_nodes(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> list[PlotNode]:
    return [
        PlotNode("primary focus", primary_focus_plot_coordinate),
        PlotNode(
            "secondary focus",
            secondary_focus_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
        PlotNode(
            "periapsis",
            periapsis_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
        PlotNode(
            "apoapsis",
            apoapsis_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
        PlotNode(
            "ascending node",
            ascending_node_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
        PlotNode(
            "descending node",
            descending_node_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
        PlotNode(
            "current position",
            current_position_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
    ]


# Subject: high-level 2D orbital-plane figure composition.
# Builds a single, internally consistent Keplerian-element ellipse plot using the
# focus-origin transform for the orbit line and all markers.
def build_keplerian_elements_2d_figure(
    settings: PlotOrbital2DSettings,
    elements: OrbitalElements,
    orbit_resolution: int = 720,
    title_prefix: str = "2D orbital-plane ellipse",
) -> go.Figure:
    primary_focus_plot_coordinate = plot_origin()
    coordinates = orbit_plot_coordinates(
        primary_focus_plot_coordinate,
        elements,
        orbit_resolution,
    )

    nodes = keplerian_element_plot_nodes(
        primary_focus_plot_coordinate,
        elements,
    )

    node_by_name = {node.name: node.coordinate for node in nodes}

    title = (
        f"{title_prefix}"
        f"<br>a={float(elements.semi_major_axis):.2f}, "
        f"e={float(elements.eccentricity):.4f}, "
        f"i={math.degrees(elements.inclination):.2f}°, "
        f"Ω={math.degrees(elements.right_ascension_of_ascending_node):.2f}°, "
        f"ω={math.degrees(elements.argument_of_periapsis):.2f}°, "
        f"ν={math.degrees(elements.true_anomaly):.2f}°"
    )

    fig = figure_layout(
        go.Figure(),
        settings.plot_width,
        settings.plot_height,
        plot_min(settings),
        plot_max(settings),
        title=title,
    )

    fig = figure_orbit_line(
        fig,
        coordinates,
        name="orbit",
        colour="grey",
    )

    fig.add_trace(
        go.Scatter(
            x=[node_by_name["descending node"].x, node_by_name["ascending node"].x],
            y=[node_by_name["descending node"].y, node_by_name["ascending node"].y],
            mode="lines",
            name="line of nodes",
            line={"color": "black", "width": 1, "dash": "dash"},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[node_by_name["apoapsis"].x, node_by_name["periapsis"].x],
            y=[node_by_name["apoapsis"].y, node_by_name["periapsis"].y],
            mode="lines",
            name="apsis line",
            line={"color": "grey", "width": 1, "dash": "dot"},
        )
    )

    return add_plot_nodes(fig, nodes)


# Subject: orbit-plot measurement.
def plotted_radius_from_primary_focus(
    primary_focus_plot_coordinate: Coordinate2D,
    coordinate: Coordinate2D,
) -> float:
    return math.hypot(
        coordinate.x - primary_focus_plot_coordinate.x,
        coordinate.y - primary_focus_plot_coordinate.y,
    )


# Subject: orbit-plot measurement.
def plotted_radius_for_eccentric_anomaly(
    primary_focus_plot_coordinate: Coordinate2D,
    orbital_elements: OrbitalElements,
    E: EccentricAnomaly,
) -> float:
    return plotted_radius_from_primary_focus(
        primary_focus_plot_coordinate,
        coordinates_for_elements(
            primary_focus_plot_coordinate,
            orbital_elements,
            E,
        ),
    )


# Subject: visualisation tangent approximation.
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
        eccentric_anomaly(float(E) + delta),
    )

    return VelocityVector(
        Velocity(Scalar(next_point.x - current.x)),
        Velocity(Scalar(next_point.y - current.y)),
        Velocity(Scalar(0)),
    )


# Subject: transfer-arc plotting.
# Normalises start/end eccentric anomaly values so Plotly draws the intended arc
# across a 2π wrap boundary.
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
# Generates orbit positions from OrbitalElements, scales them to plot units, and
# returns a Plotly 3D line trace.
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
# Fetches Horizons state vectors, derives orbital elements, propagates current and
# predicted states, and appends orbit/body traces.
def add_orbiting_body_to_traces(
    traces: list,
    body: BodyPlotConfig,
    settings: OrbitPlotSettings,
    opacity: float = 0.9,
) -> None:
    from afmaths.visualisations.helpers import add_body_surface

    if isinstance(body.target, HorizonsCommandTarget):

        horizon_state_vectors = get_object_state_vectors_from_horizon(
            target=HorizonsCommandTarget(body.target),
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
    elif isinstance(body.target, OrbitalElements):
        orbital_elements = body.target
    else:
        print(body.target)
        raise ValueError("Orbital elements ain't right")

    model_current_state = state_vector_at_time(
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

    model_prediction_state = state_vector_at_time(
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


# Subject: high-level 3D visualisation composition.
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


import plotly.graph_objects as go

from astronomy_types import PositionVector
from afmaths.visualisations.base import OrbitPlotSettings
from afmaths.visualisations.helpers import (
    add_body_surface,
    make_3d_orbit_figure,
    scale_position,
)


# Subject: 3D ITRS orbit trace construction.
# Scales a sequence of ITRS position vectors and returns a Plotly 3D line trace.
def add_itrs_orbit_trace(
    name: str,
    itrs_positions: list[PositionVector],
    distance_scale_km: float,
) -> go.Scatter3d:
    x = []
    y = []
    z = []

    for position in itrs_positions:
        scaled = scale_position(position, distance_scale_km)
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


# Subject: high-level 3D ITRS orbit visualisation composition.
# Builds a 3D figure with a central body at the origin and a supplied ITRS orbit trace.
def build_3d_itrs_orbit_figure(
    settings: OrbitPlotSettings,
    itrs_positions: list[PositionVector],
    title: str = "ITRS orbit view",
    central_body_name: str = "Earth",
    central_body_radius_km: float = 6_371.0,
    central_body_radius_scale: float = 5.0,
    orbit_name: str = "orbit",
    central_body_opacity: float = 0.7,
) -> go.Figure:
    traces = [
        add_body_surface(
            central_body_name,
            central_body_radius_km,
            central_body_radius_scale,
            settings.distance_scale_km,
            opacity=central_body_opacity,
        ),
        add_itrs_orbit_trace(
            orbit_name,
            itrs_positions,
            settings.distance_scale_km,
        ),
    ]

    return make_3d_orbit_figure(
        traces,
        title,
        settings.distance_scale_km,
    )
