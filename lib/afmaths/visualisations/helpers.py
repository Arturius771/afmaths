from __future__ import annotations

from dataclasses import dataclass
import math

import plotly.graph_objects as go

from astronomy_types import (
    Anomaly,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    OrbitalElements,
    PositionVector,
    Radians,
    Scalar,
    Vector2D,
    Vector3D,
)

from afmaths.geometry.geometry import circle_bounding_box
from afmaths.operation import interval
from afmaths.physics.space.type_conversion_helpers import vector3d


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
    from afmaths.visualisations.base import (
        coordinates_for_elements,
        secondary_focus_coordinates_for_elements,
    )

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
