from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import datetime
import math

import plotly.graph_objects as go

from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Coordinate2D,
    Coordinate3D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    PositionVector,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    SemiMinorAxis,
    StateVectors,
    TrueAnomaly,
    Vector2D,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.constants import DeltaV, Mass
from afmaths.geometry import (
    calculate_distance,
    calculate_foci,
    circle_bounding_box,
    semi_minor_axis,
    translate_ellipse_coordinate,
)
from afmaths.operation import interval
from afmaths.physics.kinematics import position_vector_from_coordinates
from afmaths.physics.space.astrodynamics import (
    anti_normal,
    anti_radial,
    normal,
    prograde,
    radial,
    retrograde,
    transfer_eccentricity,
    transfer_semi_major_axis,
)
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    apoapsis_radius,
    gravitational_parameter,
    kepler_equation,
    orbital_elements_from_state_vectors,
    orbital_period,
    periapsis_radius,
    time_since_periapsis,
    true_anomaly_from_eccentric_anomaly,
    vis_viva,
)
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    python_datetime_to_fulldate,
    python_timedelta_to_seconds,
    vector3d,
)
from afmaths.physics.space.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)
from afmaths.physics.space.orbit_propagation import (
    eccentric_anomaly_at_time,
    generate_all_orbit_positions,
    generate_angles_on_circle,
    orbit_state_vector_prediction_from_orbital_elements,
)


class TransferApsis(Enum):
    PERIAPSIS = "periapsis"
    APOAPSIS = "apoapsis"


class BurnDirection(Enum):
    PROGRADE = "prograde"
    RETROGRADE = "retrograde"


@dataclass(frozen=True)
class PerifocalOrbitLine:
    name: str
    orbital_elements: OrbitalElements
    colour: str = "grey"
    start_eccentric_anomaly: float = 0.0
    end_eccentric_anomaly: float = 2 * math.pi
    show_secondary_focus: bool = False


@dataclass(frozen=True)
class PlotNode:
    name: str
    coordinate: Coordinate2D
    text: str | None = None
    colour: str = "red"
    size: int = 12
    symbol: str = "x"


@dataclass(frozen=True)
class OrbitPlot2DSettings:
    distance_scale_km: float
    plot_width: int = 800
    plot_height: int = 800
    plot_min_x: float = 0
    plot_min_y: float = 0
    plot_max_x: float = 70
    plot_max_y: float = 70
    slider_steps: int = 51


@dataclass(frozen=True)
class BodyPlotConfig:
    name: str
    target: HorizonsCommandTarget | OrbitalElements
    radius_km: float
    radius_scale: float


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
        return Second(Scalar(python_timedelta_to_seconds(self.time_offset)))


def plot_min(settings: OrbitPlot2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_min_x, y=settings.plot_min_y)


def plot_max(settings: OrbitPlot2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_max_x, y=settings.plot_max_y)


def plot_centre(settings: OrbitPlot2DSettings) -> Coordinate2D:
    min_point = plot_min(settings)
    max_point = plot_max(settings)

    return Coordinate2D(
        min_point.x + (max_point.x - min_point.x) / 2,
        min_point.y + (max_point.y - min_point.y) / 2,
    )


def rotate_around_point(
    point: Coordinate2D,
    centre: Coordinate2D,
    angle: float,
) -> Coordinate2D:
    dx = point.x - centre.x
    dy = point.y - centre.y

    return Coordinate2D(
        centre.x + dx * math.cos(angle) - dy * math.sin(angle),
        centre.y + dx * math.sin(angle) + dy * math.cos(angle),
    )


def rotate_relative_coordinate(
    coordinate: Coordinate2D,
    angle: float,
) -> Coordinate2D:
    return Coordinate2D(
        coordinate.x * math.cos(angle) - coordinate.y * math.sin(angle),
        coordinate.x * math.sin(angle) + coordinate.y * math.cos(angle),
    )


def translate_coordinate(
    origin: Coordinate2D,
    coordinate: Coordinate2D,
) -> Coordinate2D:
    return Coordinate2D(
        origin.x + coordinate.x,
        origin.y + coordinate.y,
    )


def local_primary_focus_for_elements(elements: OrbitalElements) -> Coordinate2D:
    primary_focus, _ = calculate_foci(
        elements.semi_major_axis,
        elements.eccentricity,
    )

    return primary_focus


def local_secondary_focus_for_elements(elements: OrbitalElements) -> Coordinate2D:
    _, secondary_focus = calculate_foci(
        elements.semi_major_axis,
        elements.eccentricity,
    )

    return secondary_focus


def local_to_plot_coordinate_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    local_coordinate: Coordinate2D,
) -> Coordinate2D:
    local_primary_focus = local_primary_focus_for_elements(elements)

    local_relative_to_primary_focus = Coordinate2D(
        local_coordinate.x - local_primary_focus.x,
        local_coordinate.y - local_primary_focus.y,
    )

    rotated = rotate_relative_coordinate(
        local_relative_to_primary_focus,
        elements.argument_of_periapsis,
    )

    return translate_coordinate(
        primary_focus_plot_coordinate,
        rotated,
    )


def primary_focus_coordinates_for_elements(
    settings: OrbitPlot2DSettings,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        plot_centre(settings),
        elements,
        local_primary_focus_for_elements(elements),
    )


def secondary_focus_coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        local_secondary_focus_for_elements(elements),
    )


def ellipse_centre_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        Coordinate2D(Scalar(0), Scalar(0)),
    )


def coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    eccentric_anomaly: EccentricAnomaly,
) -> Coordinate2D:
    local_coordinate = translate_ellipse_coordinate(
        Coordinate2D(Scalar(0), Scalar(0)),
        elements.semi_major_axis,
        semi_minor_axis(elements.semi_major_axis, elements.eccentricity),
        eccentric_anomaly,
    )

    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        local_coordinate,
    )


def central_body_radius_plot(
    central_body_radius_km: float,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar(central_body_radius_km / distance_scale_km))


def figure_layout(
    figure: go.Figure,
    width_px: float,
    height_px: float,
    plot_start: Vector2D,
    plot_end: Vector2D,
    zeroline: bool = False,
) -> go.Figure:
    return (
        figure.update_layout(width=width_px, height=height_px)
        .update_xaxes(range=[plot_start.x, plot_end.x], zeroline=zeroline)
        .update_yaxes(
            range=[plot_start.y, plot_end.y],
            scaleanchor="x",
            scaleratio=1,
        )
    )


def figure_circle(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance,
    fill_colour: str = "blue",
    line_colour: str = "blue",
) -> go.Figure:
    bounding_box = circle_bounding_box(coordinates, radius)

    return figure.add_shape(
        type="circle",
        x0=bounding_box[0].x,
        y0=bounding_box[0].y,
        x1=bounding_box[1].x,
        y1=bounding_box[1].y,
        fillcolor=fill_colour,
        line_color=line_colour,
    )


def add_plot_centre(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance = Distance(Scalar(1)),
    fill_colour: str = "red",
    line_colour: str = "red",
) -> go.Figure:
    return figure_circle(
        figure,
        coordinates,
        radius,
        fill_colour,
        line_colour,
    )


def figure_planetary_body(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance,
    text: str = "Planet",
    text_colour: str = "Black",
    fill_colour: str = "blue",
    line_colour: str = "blue",
    moveable: bool = False,
) -> go.Figure:
    if moveable:
        return figure.add_trace(
            go.Scatter(
                x=[coordinates.x],
                y=[coordinates.y],
                mode="markers+text",
                text=[text],
                textposition="top center",
                marker=dict(
                    size=radius + 5,
                    color=fill_colour,
                    line=dict(color=line_colour, width=2),
                ),
                hovertext=[text],
                hoverinfo="text",
            )
        )

    return figure_circle(
        figure,
        coordinates,
        radius,
        fill_colour,
        line_colour,
    ).add_annotation(
        x=coordinates.x,
        y=coordinates.y - radius - 1,
        text=text,
        showarrow=False,
        font=dict(color=text_colour),
    )


def figure_orbit_line(
    figure: go.Figure,
    coordinates: list[Coordinate2D],
    name: str = "orbit",
    colour: str = "grey",
) -> go.Figure:
    return figure.add_trace(
        go.Scatter(
            x=[coordinate.x for coordinate in coordinates],
            y=[coordinate.y for coordinate in coordinates],
            mode="lines",
            name=name,
            line=dict(color=colour),
            showlegend=False,
        )
    )


def figure_slider(figure: go.Figure, slider_steps: list[dict]) -> go.Figure:
    return figure.update_layout(sliders=[dict(steps=slider_steps)])


def add_plot_node(
    fig: go.Figure,
    node: PlotNode,
) -> go.Figure:
    text = node.text or node.name

    fig.add_trace(
        go.Scatter(
            x=[node.coordinate.x],
            y=[node.coordinate.y],
            mode="markers+text",
            name=node.name,
            text=[text],
            textposition="top center",
            marker=dict(
                size=node.size,
                color=node.colour,
                symbol=node.symbol,
                line=dict(color=node.colour, width=2),
            ),
            hovertext=[text],
            hoverinfo="text",
        )
    )

    return fig


def add_perifocal_orbit_line(
    fig: go.Figure,
    primary_focus_plot_coordinate: Coordinate2D,
    orbit_line: PerifocalOrbitLine,
    steps: int = 200,
) -> go.Figure:
    angles = [
        orbit_line.start_eccentric_anomaly
        + (orbit_line.end_eccentric_anomaly - orbit_line.start_eccentric_anomaly)
        * i
        / (steps - 1)
        for i in range(steps)
    ]

    coordinates = [
        coordinates_for_elements(
            primary_focus_plot_coordinate,
            orbit_line.orbital_elements,
            EccentricAnomaly(Anomaly(Radians(Scalar(angle)))),
        )
        for angle in angles
    ]

    figure_orbit_line(
        fig,
        coordinates,
        orbit_line.name,
        orbit_line.colour,
    )

    if orbit_line.show_secondary_focus:
        figure_circle(
            fig,
            secondary_focus_coordinates_for_elements(
                primary_focus_plot_coordinate,
                orbit_line.orbital_elements,
            ),
            Distance(Scalar(0.1)),
            "red",
            "red",
        )

    return fig


def direction_vector_length(settings: OrbitPlot2DSettings) -> float:
    p_min = plot_min(settings)
    p_max = plot_max(settings)

    plot_range_x = p_max.x - p_min.x
    plot_range_y = p_max.y - p_min.y

    return min(plot_range_x, plot_range_y) * 0.06


def vector_line(
    start: Coordinate2D,
    direction: Vector3D,
    settings: OrbitPlot2DSettings,
) -> tuple[list[float], list[float]]:
    length = direction_vector_length(settings)

    return (
        [start.x, start.x + direction.x * length],
        [start.y, start.y + direction.y * length],
    )


def scaled_elements_for_plot(
    elements: OrbitalElements,
    distance_scale_km: float,
) -> OrbitalElements:
    return replace(
        elements,
        semi_major_axis=SemiMajorAxis(
            Distance(Scalar(elements.semi_major_axis * distance_scale_km))
        ),
    )


def semi_major_axis_metres(
    elements: OrbitalElements,
    distance_scale_km: float,
) -> SemiMajorAxis:
    return SemiMajorAxis(
        Distance(Scalar(elements.semi_major_axis * distance_scale_km * 1000))
    )


def orbiting_body_coordinates(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    eccentric_anomaly: EccentricAnomaly,
) -> Coordinate2D:
    return coordinates_for_elements(
        primary_focus_plot_coordinate,
        elements,
        eccentric_anomaly,
    )


def velocity_vector_at_time(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    elapsed_time: float,
    distance_scale_km: float,
    mu: GravitationalParameter,
) -> VelocityVector:
    period = orbital_period(
        semi_major_axis_metres(elements, distance_scale_km),
        mu,
    )

    delta_time = period / 10000
    scaled_elements = scaled_elements_for_plot(elements, distance_scale_km)

    current_coordinates = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        elements,
        eccentric_anomaly_at_time(
            scaled_elements,
            Second(Scalar(elapsed_time)),
        ),
    )

    next_coordinates = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        elements,
        eccentric_anomaly_at_time(
            scaled_elements,
            Second(Scalar(elapsed_time + delta_time)),
        ),
    )

    return VelocityVector(
        Velocity(Scalar((next_coordinates.x - current_coordinates.x) / delta_time)),
        Velocity(Scalar((next_coordinates.y - current_coordinates.y) / delta_time)),
        Velocity(Scalar(0)),
    )


def add_satellite_direction_traces(
    fig: go.Figure,
    body_name: str,
    coordinates: Coordinate2D,
) -> list[int]:
    trace_indices = []

    for direction_name in [
        "Radial",
        "Anti-radial",
        "Prograde",
        "Retrograde",
        "Normal",
        "Anti-normal",
    ]:
        trace_indices.append(len(tuple(fig.data)))

        fig.add_trace(
            go.Scatter(
                x=[coordinates.x, coordinates.x],
                y=[coordinates.y, coordinates.y],
                mode="lines+markers",
                name=f"{body_name} {direction_name}",
                hoverinfo="name",
            )
        )

    return trace_indices


def add_orbiting_body_2d(
    fig: go.Figure,
    primary_focus_plot_coordinate: Coordinate2D,
    settings: OrbitPlot2DSettings,
    body_name: str,
    body_radius_km: float,
    elements: OrbitalElements,
    is_satellite: bool = False,
) -> tuple[go.Figure, int, int, list[int]]:
    body_trace_index = len(tuple(fig.data))

    coordinates = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        elements,
        EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    body_colour = "orange" if is_satellite else "grey"

    fig.add_trace(
        go.Scatter(
            x=[coordinates.x],
            y=[coordinates.y],
            mode="markers",
            name=body_name,
            marker=dict(
                size=body_radius_km / settings.distance_scale_km + 5,
                color=body_colour,
                line=dict(color=body_colour, width=2),
            ),
            hovertext=[body_name],
            hoverinfo="text",
        )
    )

    label_trace_index = len(tuple(fig.data))

    fig.add_trace(
        go.Scatter(
            x=[coordinates.x],
            y=[coordinates.y],
            mode="markers+text",
            name=f"{body_name} label",
            text=[body_name],
            textposition="top center",
            marker=dict(
                size=1,
                color="rgba(0,0,0,0)",
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            hoverinfo="skip",
            showlegend=True,
        )
    )

    add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name=f"{body_name} orbit",
            orbital_elements=elements,
            colour=body_colour,
        ),
    )

    figure_circle(
        fig,
        secondary_focus_coordinates_for_elements(
            primary_focus_plot_coordinate,
            elements,
        ),
        Distance(Scalar(0.1)),
        "red",
        "red",
    )

    vector_trace_indices = (
        add_satellite_direction_traces(fig, body_name, coordinates)
        if is_satellite
        else []
    )

    return fig, body_trace_index, label_trace_index, vector_trace_indices


def generate_combined_orbital_slider_data(
    settings: OrbitPlot2DSettings,
    primary_focus_plot_coordinate: Coordinate2D,
    central_body_mass_kg: float,
    orbiting_body_names: list[str],
    orbiting_body_mass_kg: list[float],
    orbital_elements: list[OrbitalElements],
    orbiting_body_is_satellite: list[bool],
    body_trace_indices: list[int],
    label_trace_indices: list[int],
    vector_trace_indices: list[list[int]],
) -> list[dict]:
    steps = []

    reference_period = orbital_period(
        semi_major_axis_metres(orbital_elements[0], settings.distance_scale_km),
        gravitational_parameter(
            Mass(central_body_mass_kg),
            Mass(orbiting_body_mass_kg[0]),
        ),
    )

    for step_index in range(settings.slider_steps):
        fraction = step_index / (settings.slider_steps - 1)
        elapsed_time = reference_period * fraction

        body_x_updates = []
        body_y_updates = []
        label_x_updates = []
        label_y_updates = []
        label_text_updates = []
        vector_x_updates = []
        vector_y_updates = []
        vector_update_indices = []

        for index, elements in enumerate(orbital_elements):
            mu = gravitational_parameter(
                Mass(central_body_mass_kg),
                Mass(orbiting_body_mass_kg[index]),
            )

            eccentric_anomaly_obj = eccentric_anomaly_at_time(
                scaled_elements_for_plot(elements, settings.distance_scale_km),
                Second(Scalar(elapsed_time)),
            )

            true_anomaly = true_anomaly_from_eccentric_anomaly(
                eccentric_anomaly_obj,
                elements.eccentricity,
            )

            coordinates = orbiting_body_coordinates(
                primary_focus_plot_coordinate,
                elements,
                eccentric_anomaly_obj,
            )

            distance_km = (
                calculate_distance(
                    Coordinate2D(coordinates.x, coordinates.y),
                    primary_focus_plot_coordinate,
                )
                * settings.distance_scale_km
            )

            velocity_m_s = vis_viva(
                gravitational_parameter=mu,
                orbit_radius=Distance(Scalar(distance_km * 1000)),
                semi_major_axis=semi_major_axis_metres(
                    elements,
                    settings.distance_scale_km,
                ),
            )

            velocity_km_s = velocity_m_s / 1000

            body_x_updates.append([coordinates.x])
            body_y_updates.append([coordinates.y])

            label_x_updates.append([coordinates.x])
            label_y_updates.append([coordinates.y])
            label_text_updates.append(
                [
                    f"{orbiting_body_names[index]}<br>"
                    f"r = {distance_km:.2f} km <br>"
                    f"v = {velocity_km_s:.2f} km/s <br>"
                    f"ta = {true_anomaly:.2f} rad <br>"
                    f"t = {elapsed_time:.2f} s"
                ]
            )

            if orbiting_body_is_satellite[index]:
                position_vector = position_vector_from_coordinates(
                    Coordinate3D(coordinates.x, coordinates.y, Scalar(0)),
                    Coordinate3D(
                        primary_focus_plot_coordinate.x,
                        primary_focus_plot_coordinate.y,
                        Scalar(0),
                    ),
                )

                velocity_vector = velocity_vector_at_time(
                    primary_focus_plot_coordinate,
                    elements,
                    elapsed_time,
                    settings.distance_scale_km,
                    mu,
                )

                direction_vectors = [
                    radial(position_vector),
                    anti_radial(position_vector),
                    prograde(velocity_vector),
                    retrograde(velocity_vector),
                    normal(StateVectors(position_vector, velocity_vector)),
                    anti_normal(StateVectors(position_vector, velocity_vector)),
                ]

                for direction_vector, trace_index in zip(
                    direction_vectors,
                    vector_trace_indices[index],
                ):
                    xs, ys = vector_line(
                        coordinates,
                        direction_vector,
                        settings,
                    )

                    vector_x_updates.append(xs)
                    vector_y_updates.append(ys)
                    vector_update_indices.append(trace_index)

        update = {
            "x": body_x_updates + label_x_updates + vector_x_updates,
            "y": body_y_updates + label_y_updates + vector_y_updates,
            "text": [[] for _ in body_trace_indices] + label_text_updates,
        }

        steps.append(
            dict(
                method="restyle",
                args=[
                    update,
                    body_trace_indices + label_trace_indices + vector_update_indices,
                ],
                label=f"{fraction:.2f}",
            )
        )

    return steps


def build_2d_orbit_visualiser_figure(
    settings: OrbitPlot2DSettings,
    central_body_name: str,
    central_body_radius_km: float,
    central_body_mass_kg: float,
    orbiting_body_names: list[str],
    orbiting_body_radius_km: list[float],
    orbiting_body_mass_kg: list[float],
    orbital_elements: list[OrbitalElements],
    orbiting_body_is_satellite: list[bool] | None = None,
    title: str = "2D orbit visualiser",
) -> go.Figure:
    if orbiting_body_is_satellite is None:
        orbiting_body_is_satellite = [False for _ in orbiting_body_names]

    if not (
        len(orbiting_body_names)
        == len(orbiting_body_radius_km)
        == len(orbiting_body_mass_kg)
        == len(orbital_elements)
        == len(orbiting_body_is_satellite)
    ):
        raise ValueError(
            "orbiting_body_names, orbiting_body_radius_km, orbiting_body_mass_kg, "
            "orbital_elements, and orbiting_body_is_satellite must have the same length"
        )

    primary_focus_plot_coordinate = plot_centre(settings)

    fig = go.Figure()

    body_trace_indices: list[int] = []
    label_trace_indices: list[int] = []
    vector_trace_indices: list[list[int]] = []

    for index, elements in enumerate(orbital_elements):
        fig, body_trace_index, label_trace_index, body_vector_trace_indices = (
            add_orbiting_body_2d(
                fig,
                primary_focus_plot_coordinate,
                settings,
                orbiting_body_names[index],
                orbiting_body_radius_km[index],
                elements,
                orbiting_body_is_satellite[index],
            )
        )

        body_trace_indices.append(body_trace_index)
        label_trace_indices.append(label_trace_index)
        vector_trace_indices.append(body_vector_trace_indices)

    fig = figure_planetary_body(
        fig,
        primary_focus_plot_coordinate,
        central_body_radius_plot(
            central_body_radius_km,
            settings.distance_scale_km,
        ),
        central_body_name,
        "Black",
        "blue",
        "green",
    )

    fig = figure_layout(
        fig,
        settings.plot_width,
        settings.plot_height,
        plot_min(settings),
        plot_max(settings),
    )

    fig = figure_slider(
        fig,
        generate_combined_orbital_slider_data(
            settings,
            primary_focus_plot_coordinate,
            central_body_mass_kg,
            orbiting_body_names,
            orbiting_body_mass_kg,
            orbital_elements,
            orbiting_body_is_satellite,
            body_trace_indices,
            label_trace_indices,
            vector_trace_indices,
        ),
    )

    fig = add_plot_centre(
        fig,
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )

    fig.update_layout(title=title)

    return fig


def opposite_apsis(apsis: TransferApsis) -> TransferApsis:
    if apsis == TransferApsis.PERIAPSIS:
        return TransferApsis.APOAPSIS

    return TransferApsis.PERIAPSIS


def apsis_radius(
    orbit: OrbitalElements,
    apsis: TransferApsis,
) -> Distance:
    if apsis == TransferApsis.PERIAPSIS:
        return periapsis_radius(
            orbit.semi_major_axis,
            orbit.eccentricity,
        )

    return apoapsis_radius(
        orbit.semi_major_axis,
        orbit.eccentricity,
    )


def apsis_angle(
    orbit: OrbitalElements,
    apsis: TransferApsis,
) -> float:
    if apsis == TransferApsis.PERIAPSIS:
        return orbit.argument_of_periapsis

    return orbit.argument_of_periapsis + math.pi


def eccentric_anomaly_for_transfer_radius(
    radius: Distance,
    transfer_periapsis_radius: Distance,
    transfer_apoapsis_radius: Distance,
) -> EccentricAnomaly:
    if radius == transfer_periapsis_radius:
        return EccentricAnomaly(Anomaly(Radians(Scalar(0))))

    if radius == transfer_apoapsis_radius:
        return EccentricAnomaly(Anomaly(Radians(Scalar(math.pi))))

    raise ValueError(
        "Transfer burn radius must be either transfer periapsis or apoapsis."
    )


def transfer_orbit_from_apsides(
    initial_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    start_apsis: TransferApsis,
    final_apsis: TransferApsis,
) -> OrbitalElements:
    start_radius = apsis_radius(initial_orbit, start_apsis)
    final_radius = apsis_radius(final_orbit, final_apsis)

    transfer_periapsis_radius = min(start_radius, final_radius)
    transfer_apoapsis_radius = max(start_radius, final_radius)

    start_angle = apsis_angle(initial_orbit, start_apsis)
    transfer_starts_at_periapsis = start_radius == transfer_periapsis_radius

    transfer_argument_of_periapsis = (
        start_angle if transfer_starts_at_periapsis else start_angle + math.pi
    )

    return OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        ArgumentOfPerigee(Radians(Scalar(transfer_argument_of_periapsis))),
        SemiMajorAxis(
            transfer_semi_major_axis(
                transfer_periapsis_radius,
                transfer_apoapsis_radius,
            )
        ),
        transfer_eccentricity(
            transfer_periapsis_radius,
            transfer_apoapsis_radius,
        ),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )


def scaled_distance_km(
    distance: Distance,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar(distance * distance_scale_km))


def scaled_semi_major_axis_km(
    orbit: OrbitalElements,
    distance_scale_km: float,
) -> SemiMajorAxis:
    return SemiMajorAxis(Distance(Scalar(orbit.semi_major_axis * distance_scale_km)))


def velocity_at_radius_km_s(
    orbit: OrbitalElements,
    radius: Distance,
    distance_scale_km: float,
    mu: GravitationalParameter,
) -> Velocity:
    return vis_viva(
        gravitational_parameter=mu,
        orbit_radius=scaled_distance_km(radius, distance_scale_km),
        semi_major_axis=scaled_semi_major_axis_km(
            orbit,
            distance_scale_km,
        ),
    )


def burn_direction(
    current_speed: Velocity,
    target_speed: Velocity,
) -> BurnDirection:
    if target_speed >= current_speed:
        return BurnDirection.PROGRADE

    return BurnDirection.RETROGRADE


def delta_v_between_speeds(
    first_speed: Velocity,
    second_speed: Velocity,
) -> DeltaV:
    return DeltaV(Velocity(Scalar(abs(second_speed - first_speed))))


def transfer_arc_angles(
    start_eccentric_anomaly: EccentricAnomaly,
    arrival_eccentric_anomaly: EccentricAnomaly,
) -> tuple[float, float]:
    start = float(start_eccentric_anomaly)
    end = float(arrival_eccentric_anomaly)

    if end <= start:
        return start, end + 2 * math.pi

    return start, end


def transfer_burn_plot_nodes(
    settings: OrbitPlot2DSettings,
    primary_focus_plot_coordinate: Coordinate2D,
    initial_orbit: OrbitalElements,
    transfer_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    start_apsis: TransferApsis,
    final_apsis: TransferApsis,
    start_radius: Distance,
    final_radius: Distance,
    transfer_start_eccentric_anomaly: EccentricAnomaly,
    transfer_arrival_eccentric_anomaly: EccentricAnomaly,
    transfer_time: Second,
    mu: GravitationalParameter,
) -> list[PlotNode]:
    initial_speed = velocity_at_radius_km_s(
        initial_orbit,
        start_radius,
        settings.distance_scale_km,
        mu,
    )

    transfer_start_speed = velocity_at_radius_km_s(
        transfer_orbit,
        start_radius,
        settings.distance_scale_km,
        mu,
    )

    transfer_arrival_speed = velocity_at_radius_km_s(
        transfer_orbit,
        final_radius,
        settings.distance_scale_km,
        mu,
    )

    final_speed = velocity_at_radius_km_s(
        final_orbit,
        final_radius,
        settings.distance_scale_km,
        mu,
    )

    transfer_delta_v = delta_v_between_speeds(
        initial_speed,
        transfer_start_speed,
    )

    arrival_delta_v = delta_v_between_speeds(
        transfer_arrival_speed,
        final_speed,
    )

    transfer_direction = burn_direction(
        initial_speed,
        transfer_start_speed,
    )

    arrival_direction = burn_direction(
        transfer_arrival_speed,
        final_speed,
    )

    transfer_burn_coordinate = coordinates_for_elements(
        primary_focus_plot_coordinate,
        transfer_orbit,
        transfer_start_eccentric_anomaly,
    )

    arrival_burn_coordinate = coordinates_for_elements(
        primary_focus_plot_coordinate,
        transfer_orbit,
        transfer_arrival_eccentric_anomaly,
    )

    return [
        PlotNode(
            name=f"Transfer burn at initial {start_apsis.value}",
            coordinate=transfer_burn_coordinate,
            text=(
                f"Transfer burn at initial {start_apsis.value}<br>"
                f"Direction = {transfer_direction.value}<br>"
                f"Δv = {transfer_delta_v:.4f} km/s<br>"
                f"t = {Second(Scalar(0)):.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
        PlotNode(
            name=f"Arrival burn at final {final_apsis.value}",
            coordinate=arrival_burn_coordinate,
            text=(
                f"Arrival burn at final {final_apsis.value}<br>"
                f"Direction = {arrival_direction.value}<br>"
                f"Δv = {arrival_delta_v:.4f} km/s<br>"
                f"t = {transfer_time:.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
    ]


def build_hohmann_transfer_2d_perifocal_figure(
    settings: OrbitPlot2DSettings,
    initial_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    gravitational_parameter: GravitationalParameter,
    start_apsis: TransferApsis = TransferApsis.PERIAPSIS,
    final_apsis: TransferApsis | None = None,
    central_body_name: str = "Earth",
    central_body_radius_km: float = 6_371.0,
    title_prefix: str = "Hohmann transfer in the perifocal frame",
) -> go.Figure:
    final_apsis = final_apsis or opposite_apsis(start_apsis)
    primary_focus_plot_coordinate = plot_centre(settings)

    transfer_orbit = transfer_orbit_from_apsides(
        initial_orbit,
        final_orbit,
        start_apsis,
        final_apsis,
    )

    start_radius = apsis_radius(initial_orbit, start_apsis)
    final_radius = apsis_radius(final_orbit, final_apsis)

    transfer_periapsis_radius = min(start_radius, final_radius)
    transfer_apoapsis_radius = max(start_radius, final_radius)

    transfer_start_eccentric_anomaly = eccentric_anomaly_for_transfer_radius(
        start_radius,
        transfer_periapsis_radius,
        transfer_apoapsis_radius,
    )

    transfer_arrival_eccentric_anomaly = eccentric_anomaly_for_transfer_radius(
        final_radius,
        transfer_periapsis_radius,
        transfer_apoapsis_radius,
    )

    transfer_arc_start_angle, transfer_arc_end_angle = transfer_arc_angles(
        transfer_start_eccentric_anomaly,
        transfer_arrival_eccentric_anomaly,
    )

    transfer_period = orbital_period(
        scaled_semi_major_axis_km(
            transfer_orbit,
            settings.distance_scale_km,
        ),
        gravitational_parameter,
    )

    transfer_time = Second(Scalar(transfer_period / 2))

    burn_nodes = transfer_burn_plot_nodes(
        settings,
        primary_focus_plot_coordinate,
        initial_orbit,
        transfer_orbit,
        final_orbit,
        start_apsis,
        final_apsis,
        start_radius,
        final_radius,
        transfer_start_eccentric_anomaly,
        transfer_arrival_eccentric_anomaly,
        transfer_time,
        gravitational_parameter,
    )

    fig = go.Figure()

    fig = add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name="Initial orbit",
            orbital_elements=initial_orbit,
            colour="grey",
        ),
    )

    fig = add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name="Transfer arc",
            orbital_elements=transfer_orbit,
            colour="orange",
            start_eccentric_anomaly=transfer_arc_start_angle,
            end_eccentric_anomaly=transfer_arc_end_angle,
            show_secondary_focus=True,
        ),
    )

    fig = add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name="Final orbit",
            orbital_elements=final_orbit,
            colour="grey",
        ),
    )

    for node in burn_nodes:
        fig = add_plot_node(fig, node)

    fig = figure_planetary_body(
        fig,
        primary_focus_plot_coordinate,
        central_body_radius_plot(
            central_body_radius_km,
            settings.distance_scale_km,
        ),
        central_body_name,
        "Black",
        "blue",
        "green",
    )

    fig = figure_layout(
        fig,
        settings.plot_width,
        settings.plot_height,
        plot_min(settings),
        plot_max(settings),
    )

    fig = add_plot_centre(
        fig,
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )

    transfer_delta_v = delta_v_between_speeds(
        velocity_at_radius_km_s(
            initial_orbit,
            start_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
        velocity_at_radius_km_s(
            transfer_orbit,
            start_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
    )

    arrival_delta_v = delta_v_between_speeds(
        velocity_at_radius_km_s(
            transfer_orbit,
            final_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
        velocity_at_radius_km_s(
            final_orbit,
            final_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
    )

    total_delta_v = DeltaV(Velocity(Scalar(transfer_delta_v + arrival_delta_v)))

    fig.update_layout(
        title=(
            f"{title_prefix}<br>"
            f"Start = initial {start_apsis.value}, "
            f"arrival = final {final_apsis.value}<br>"
            f"Total Δv = {total_delta_v:.4f} km/s, "
            f"transfer time = {transfer_time:.2f} s"
        )
    )

    return fig


def generate_orbital_slider_data(
    step_n: int,
    plot_central_point: Coordinate2D,
    primary_body_coordinates: Coordinate2D,
    elements: OrbitalElements,
    b: SemiMinorAxis,
    plot_scale: float,
    g: GravitationalParameter,
) -> list[dict]:
    steps = []

    for eccentric_anomaly in generate_angles_on_circle(step_n):
        eccentric_anomaly_obj = EccentricAnomaly(
            Anomaly(Radians(Scalar(eccentric_anomaly)))
        )

        true_anomaly = true_anomaly_from_eccentric_anomaly(
            eccentric_anomaly_obj,
            elements.eccentricity,
        )

        coordinates = translate_ellipse_coordinate(
            plot_central_point,
            elements.semi_major_axis,
            b,
            eccentric_anomaly_obj,
        )

        distance_km = (
            calculate_distance(
                Coordinate2D(coordinates.x, coordinates.y),
                primary_body_coordinates,
            )
            * plot_scale
        )

        distance_m = distance_km * 1000
        semi_major_axis_km = elements.semi_major_axis * plot_scale
        semi_major_axis_m = semi_major_axis_km * 1000

        velocity_m_s = vis_viva(
            orbit_radius=Distance(Scalar(distance_m)),
            semi_major_axis=SemiMajorAxis(Distance(Scalar(semi_major_axis_m))),
            gravitational_parameter=g,
        )

        velocity_km_s = velocity_m_s / 1000

        time = time_since_periapsis(
            SemiMajorAxis(Distance(Scalar(semi_major_axis_m))),
            g,
            kepler_equation(
                eccentric_anomaly_obj,
                elements.eccentricity,
            ),
        )

        steps.append(
            dict(
                method="restyle",
                args=[
                    {
                        "x": [[coordinates.x]],
                        "y": [[coordinates.y]],
                        "text": [
                            [
                                f"r = {distance_km:.2f} km <br>"
                                f"v = {velocity_km_s:.2f} km/s <br>"
                                f"ta = {true_anomaly:.2f} rad <br>"
                                f"t = {time:.2f} s"
                            ]
                        ],
                    },
                    [0],
                ],
            )
        )

    return steps


def plot_sphere_surface(
    radius: Distance,
    centre: PositionVector | None = None,
    resolution: int = 50,
) -> Vector3D:
    u = interval(0, 2 * math.pi, resolution)
    v = interval(0, math.pi, resolution)

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

    return vector3d(sphere_x, sphere_y, sphere_z)


def scale_value(value: float | int, distance_scale_km: float) -> float:
    return float(value) / distance_scale_km


def scale_position(position, distance_scale_km: float) -> Vector3D:
    return vector3d(
        scale_value(position.x, distance_scale_km),
        scale_value(position.y, distance_scale_km),
        scale_value(position.z, distance_scale_km),
    )


def scaled_radius(
    radius_km: float,
    radius_scale: float,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar((radius_km * radius_scale) / distance_scale_km))


def add_body_surface(
    name: str,
    radius_km: float,
    radius_scale: float,
    distance_scale_km: float,
    position: PositionVector | None = None,
    opacity: float = 0.9,
) -> go.Surface:
    surface = plot_sphere_surface(
        scaled_radius(radius_km, radius_scale, distance_scale_km),
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


def make_3d_orbit_figure(
    traces: list,
    title: str,
    distance_scale_km: float,
) -> go.Figure:
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=f"X ({distance_scale_km:,} km units)",
            yaxis_title=f"Y ({distance_scale_km:,} km units)",
            zaxis_title=f"Z ({distance_scale_km:,} km units)",
            aspectmode="data",
        ),
    )

    return fig


def get_horizon_state_vectors(
    target: HorizonsCommandTarget,
    settings: OrbitPlotSettings,
) -> list[StateVectors]:
    return get_object_state_vectors_from_horizon(
        target=target,
        centre=settings.centre,
        start_time=python_datetime_to_fulldate(settings.start_time),
        stop_time=python_datetime_to_fulldate(settings.stop_time),
    )


def add_orbiting_body_to_traces(
    traces: list,
    body: BodyPlotConfig,
    settings: OrbitPlotSettings,
    opacity: float = 0.9,
) -> None:
    horizon_state_vectors = get_horizon_state_vectors(
        HorizonsCommandTarget(body.target),
        settings,
    )

    if len(horizon_state_vectors) < 1:
        raise ValueError(f"No Horizons state vectors returned for {body.name}")

    orbital_elements = orbital_elements_from_state_vectors(
        horizon_state_vectors[0],
        gravitational_parameter=settings.gravitational_parameter,
    )

    model_current_state = orbit_state_vector_prediction_from_orbital_elements(
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

    model_prediction_state = orbit_state_vector_prediction_from_orbital_elements(
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


def build_3d_orbit_figure(
    settings: OrbitPlotSettings,
    title: str,
    central_body_name: str,
    central_body_radius_km: float,
    central_body_radius_scale: float,
    orbiting_bodies: list[BodyPlotConfig],
    central_body_opacity: float = 0.7,
) -> go.Figure:
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
