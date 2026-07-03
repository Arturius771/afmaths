from __future__ import annotations

from dataclasses import dataclass, replace
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
    SemiMajorAxis,
    Vector2D,
    Vector3D,
)

from afmaths.geometry.geometry import circle_bounding_box
from afmaths.operation import interval
from afmaths.physics.space.type_conversion_helpers import make_vector3d


@dataclass(frozen=True)
class PlotPerifocalOrbitLine:
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
class PlotOrbital2DSettings:
    distance_scale: float
    plot_width: int = 800
    plot_height: int = 800
    plot_min_x: float = -35
    plot_min_y: float = -35
    plot_max_x: float = 35
    plot_max_y: float = 35
    slider_steps: int = 51


# Subject: unit/scale conversion.
# Converts a plot-scaled distance back into physical distance units by multiplying
# by the distance scale. This is a visualisation/physics unit adapter.
def scale_distance_to_distance(
    distance: Distance,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar(distance * distance_scale_km))


# Subject: unit/scale conversion.
# Converts a physical distance into plot units by dividing by the distance scale.
def distance_to_scale_distance(distance_km: Distance, scale: float) -> Distance:
    return Distance(Scalar(distance_km / scale))


# Subject: visualisation scale conversion for 3D vectors.
# Divides x/y/z position components by distance_scale_km and rebuilds a Vector3D.
# This is a render-time coordinate scaling helper, not celestial mechanics.
def scale_position(position: PositionVector, distance_scale_km: float) -> Vector3D:
    return make_vector3d(
        distance_to_scale_distance(Distance(position.x), distance_scale_km),
        distance_to_scale_distance(Distance(position.y), distance_scale_km),
        distance_to_scale_distance(Distance(position.z), distance_scale_km),
    )


# Subject: unit/scale conversion for orbital elements.
# Converts the semi-major axis of OrbitalElements into plot units.
def elements_scaled_to_plot(
    elements: OrbitalElements,
    scale: float,
) -> OrbitalElements:
    return replace(
        elements,
        semi_major_axis=SemiMajorAxis(
            distance_to_scale_distance(elements.semi_major_axis, scale)
        ),
    )


# Subject: unit/scale conversion.
# Backwards-compatible alias for distance_to_scale_distance.
def value_to_scale(
    distance_km: Distance,
    scale: float,
) -> Distance:
    return distance_to_scale_distance(distance_km, scale)


# Subject: plot bounds.
def plot_min(settings: PlotOrbital2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_min_x, y=settings.plot_min_y)


# Subject: plot bounds.
def plot_max(settings: PlotOrbital2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_max_x, y=settings.plot_max_y)


# Subject: plot bounds.
def plot_centre(settings: PlotOrbital2DSettings) -> Coordinate2D:
    min_point = plot_min(settings)
    max_point = plot_max(settings)

    return Coordinate2D(
        min_point.x + (max_point.x - min_point.x) / 2,
        min_point.y + (max_point.y - min_point.y) / 2,
    )


# Subject: plot origin.
# The physical origin of 2D orbital-plane plots. For Keplerian orbits this is
# the primary focus, i.e. the central body position.
def plot_origin() -> Coordinate2D:
    return Coordinate2D(Scalar(0), Scalar(0))


# Subject: visualisation scale conversion.
def central_body_radius_plot(
    central_body_radius_km: float,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar(central_body_radius_km / distance_scale_km))


# Subject: Plotly 2D layout.
def figure_layout(
    figure: go.Figure,
    width_px: float,
    height_px: float,
    plot_start: Vector2D,
    plot_end: Vector2D,
    title: str,
    zeroline: bool = False,
) -> go.Figure:
    return (
        figure.update_layout(width=width_px, height=height_px, title=title)
        .update_xaxes(range=[plot_start.x, plot_end.x], zeroline=zeroline)
        .update_yaxes(
            range=[plot_start.y, plot_end.y],
            scaleanchor="x",
            scaleratio=1,
        )
    )


# Subject: Plotly 2D primitive.
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


# Subject: Plotly 2D primitive.
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


# Subject: Plotly 2D primitive.
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


# Subject: Plotly 2D line trace.
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


# Subject: Plotly slider composition.
def figure_slider(figure: go.Figure, slider_steps: list[dict]) -> go.Figure:
    return figure.update_layout(sliders=[dict(steps=slider_steps)])


# Subject: Plotly 2D marker/text trace.
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


# Subject: Plotly 2D marker/text composition.
def add_plot_nodes(fig: go.Figure, nodes: list[PlotNode]) -> go.Figure:
    for node in nodes:
        fig = add_plot_node(fig, node)

    return fig


# Subject: orbit visualisation adapter.
# Samples a perifocal ellipse by eccentric anomaly and draws it in the plot frame.
def add_perifocal_orbit_line(
    fig: go.Figure,
    primary_focus_plot_coordinate: Coordinate2D,
    orbit_line: PlotPerifocalOrbitLine,
    steps: int = 200,
) -> go.Figure:
    if steps < 2:
        raise ValueError("steps must be at least 2")

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


# Subject: vector visualisation.
def direction_vector_length(settings: PlotOrbital2DSettings) -> float:
    p_min = plot_min(settings)
    p_max = plot_max(settings)

    plot_range_x = p_max.x - p_min.x
    plot_range_y = p_max.y - p_min.y

    return min(plot_range_x, plot_range_y) * 0.06


# Subject: vector visualisation.
def vector_line(
    start: Coordinate2D,
    direction: Vector3D,
    settings: PlotOrbital2DSettings,
) -> tuple[list[float], list[float]]:
    length = direction_vector_length(settings)

    return (
        [start.x, start.x + direction.x * length],
        [start.y, start.y + direction.y * length],
    )


# Subject: 3D surface geometry for visualisation.
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

    return make_vector3d(sphere_x, sphere_y, sphere_z)


# Subject: visualisation scale conversion.
def scaled_radius(
    radius_km: float,
    radius_scale: float,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar((radius_km * radius_scale) / distance_scale_km))


# Subject: Plotly 3D surface trace.
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


# Subject: Plotly 3D layout composition.
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
