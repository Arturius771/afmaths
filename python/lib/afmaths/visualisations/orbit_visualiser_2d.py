from __future__ import annotations

import math
from dataclasses import replace

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
    Second,
    SemiMajorAxis,
    TrueAnomaly,
    Vector2D,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.geometry.geometry import circle_bounding_box, semi_minor_axis
from afmaths.geometry.transformations import translate_ellipse
from afmaths.physics.space.celestial_mechanics.nodes import (
    perifocal_position_at_ascending_node,
    perifocal_position_at_descending_node,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    apoapsis_true_anomaly,
    periapsis_true_anomaly,
)
from afmaths.physics.space.celestial_mechanics.state_vector import (
    perifocal_position_vector,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.type_conversion_helpers import make_eccentric_anomaly
from afmaths.visualisations.visualisation_types import (
    OrbitingBody2D,
    PlotNode,
    PlotOrbital2DSettings,
    PlotPerifocalOrbitLine,
)


def plot_min(settings: PlotOrbital2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_min_x, y=settings.plot_min_y)


def plot_max(settings: PlotOrbital2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_max_x, y=settings.plot_max_y)


def figure_circle(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance,
    fill_colour: str | None = "blue",
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


def rotate_relative_coordinate(
    coordinate: Coordinate2D,
    angle: float,
) -> Coordinate2D:
    return Coordinate2D(
        coordinate.x * math.cos(angle) - coordinate.y * math.sin(angle),
        coordinate.x * math.sin(angle) + coordinate.y * math.cos(angle),
    )


def primary_focus_local_coordinate_for_elements(
    elements: OrbitalElements,
) -> Coordinate2D:
    return Coordinate2D(
        Scalar(elements.semi_major_axis * elements.eccentricity),
        Scalar(0),
    )


def translate_coordinate(
    origin: Coordinate2D,
    coordinate: Coordinate2D,
) -> Coordinate2D:
    return Coordinate2D(
        origin.x + coordinate.x,
        origin.y + coordinate.y,
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


def secondary_focus_local_coordinate_for_elements(
    elements: OrbitalElements,
) -> Coordinate2D:
    return Coordinate2D(
        Scalar(-elements.semi_major_axis * elements.eccentricity),
        Scalar(0),
    )


def secondary_focus_coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        secondary_focus_local_coordinate_for_elements(elements),
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
            line={"color": colour},
            showlegend=False,
        )
    )


def add_perifocal_orbit_line(
    fig: go.Figure,
    primary_focus_plot_coordinate: Coordinate2D,
    orbit_line: PlotPerifocalOrbitLine,
    steps: int = 200,
) -> go.Figure:
    if steps < 2:
        raise ValueError("steps must be at least 2")

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


def central_body_radius_plot(
    central_body_radius: float,
    distance_scale: float,
) -> Distance:
    return Distance(Scalar(central_body_radius / distance_scale))


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


def add_plot_node(fig: go.Figure, node: PlotNode) -> go.Figure:
    text = node.text or node.name

    fig.add_trace(
        go.Scatter(
            x=[node.coordinate.x],
            y=[node.coordinate.y],
            mode="markers+text" if not node.marker_only else "markers",
            name=node.name,
            text=[text],
            textposition="top center",
            marker={
                "size": node.size,
                "color": node.colour,
                "symbol": node.symbol,
                "line": {"color": node.colour, "width": 2},
            },
            hovertext=[text],
            hoverinfo="text",
        )
    )

    return fig


def add_plot_nodes(fig: go.Figure, nodes: list[PlotNode]) -> go.Figure:
    for node in nodes:
        fig = add_plot_node(fig, node)

    return fig


def scale_distance_to_distance(
    distance: Distance,
    distance_scale: float,
) -> Distance:
    """Both distance and scale must be in the same unit."""
    return Distance(Scalar(distance * distance_scale))


def plot_origin() -> Coordinate2D:
    return Coordinate2D(Scalar(0), Scalar(0))


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
                marker={
                    "size": radius + 5,
                    "color": fill_colour,
                    "line": {"color": line_colour, "width": 2},
                },
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
        font={"color": text_colour},
    )


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


def figure_slider(figure: go.Figure, slider_steps: list[dict]) -> go.Figure:
    return figure.update_layout(sliders=[{"steps": slider_steps}])


def direction_vector_length(settings: PlotOrbital2DSettings) -> float:
    p_min = plot_min(settings)
    p_max = plot_max(settings)

    plot_range_x = p_max.x - p_min.x
    plot_range_y = p_max.y - p_min.y

    return min(plot_range_x, plot_range_y) * 0.06


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


def distance_to_scale_distance(
    distance: Distance,
    distance_scale: float,
) -> Distance:
    """Both distance and scale must be in the same unit."""
    return Distance(Scalar(distance / distance_scale))


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


def scale_orbital_elements_for_plot(
    orbital_elements: OrbitalElements,
    distance_scale: Distance,
) -> OrbitalElements:
    return elements_scaled_to_plot(orbital_elements, float(distance_scale))


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


def periapsis_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return plot_coordinate_for_true_anomaly(
        primary_focus_plot_coordinate,
        elements,
        periapsis_true_anomaly(),
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
        make_eccentric_anomaly(float(E) + delta),
    )

    return VelocityVector(
        Velocity(Scalar(next_point.x - current.x)),
        Velocity(Scalar(next_point.y - current.y)),
        Velocity(Scalar(0)),
    )


def ascending_node_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return position_to_plot_coordinate(
        primary_focus_plot_coordinate,
        elements,
        perifocal_position_at_ascending_node(elements),
    )


def descending_node_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return position_to_plot_coordinate(
        primary_focus_plot_coordinate,
        elements,
        perifocal_position_at_descending_node(elements),
    )


def apoapsis_plot_coordinate(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return plot_coordinate_for_true_anomaly(
        primary_focus_plot_coordinate,
        elements,
        apoapsis_true_anomaly(),
    )


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


from itertools import cycle

from astronomy_types import (
    Coordinate3D,
    Distance,
    Scalar,
    StateVector,
)

from afmaths.afmath_types import Mass
from afmaths.constants import MOON_ELEMENTS
from afmaths.geometry.geometry import euclidian_distance, generate_angles_on_circle
from afmaths.physics.kinematics import position_displacement
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    vis_viva,
)
from afmaths.physics.space.celestial_mechanics.gravitation import (
    gravitational_parameter,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    eccentric_anomaly_at_time,
    true_anomaly_from_eccentric_anomaly,
)
from afmaths.physics.space.engineering.astrodynamics.orbital_directions import (
    anti_normal,
    anti_radial,
    normal,
    prograde,
    radial,
    retrograde,
)

EARTH_RADIUS_M = 6_371.0 * 1000
EARTH_MASS_KG = 5.9722e24

MOON_RADIUS_M = 1_737.4 * 1000
MOON_MASS_KG = 7.346e22

DEFAULT_SATELLITE_RADIUS_M = 5.0
DEFAULT_SATELLITE_MASS_KG = 1000.0

DISTANCE_SCALE = 17_000.0 * 1000
DEFAULT_PLOT_SETTINGS = PlotOrbital2DSettings(
    distance_scale=DISTANCE_SCALE,
)

SATELLITE_COLOURS = (
    "#636EFA",
    "#EF553B",
    "#00CC96",
    "#AB63FA",
    "#FFA15A",
    "#19D3F3",
    "#FF6692",
    "#B6E880",
    "#FF97FF",
    "#FECB52",
)


def satellite_orbiting_body(
    name: str,
    elements: OrbitalElements,
    *,
    radius_m: float = DEFAULT_SATELLITE_RADIUS_M,
    mass_kg: float = DEFAULT_SATELLITE_MASS_KG,
    colour: str | None = None,
) -> OrbitingBody2D:
    return OrbitingBody2D(
        name=name,
        radius_m=radius_m,
        mass_kg=mass_kg,
        elements=elements,
        is_satellite=True,
        colour=colour,
    )


def moon_orbiting_body() -> OrbitingBody2D:
    return OrbitingBody2D(
        name="Moon",
        radius_m=MOON_RADIUS_M,
        mass_kg=MOON_MASS_KG,
        elements=MOON_ELEMENTS,
        colour="grey",
    )


def _reference_body_index(
    orbiting_bodies: list[OrbitingBody2D],
) -> int:
    """
    Use the first satellite as the propagation-duration reference when one
    exists. Otherwise use the first orbiting body, normally the Moon.
    """
    return next(
        (index for index, body in enumerate(orbiting_bodies) if body.is_satellite),
        0,
    )


def _reference_period(
    central_body_mass_kg: float,
    orbiting_bodies: list[OrbitingBody2D],
) -> float:
    if not orbiting_bodies:
        raise ValueError("At least one orbiting body is required.")

    body = orbiting_bodies[_reference_body_index(orbiting_bodies)]

    return float(
        orbital_period(
            body.elements.semi_major_axis,
            gravitational_parameter(
                Mass(central_body_mass_kg),
                Mass(body.mass_kg),
            ),
        )
    )


def _initial_body_coordinates(
    primary_focus_plot_coordinate: Coordinate2D,
    central_body_mass_kg: float,
    body: OrbitingBody2D,
    plot_elements: OrbitalElements,
) -> Coordinate2D:
    mu = gravitational_parameter(
        Mass(central_body_mass_kg),
        Mass(body.mass_kg),
    )

    eccentric_anomaly = eccentric_anomaly_at_time(
        body.elements,
        Second(Scalar(0)),
        mu,
    )

    return coordinates_for_elements(
        primary_focus_plot_coordinate,
        plot_elements,
        eccentric_anomaly,
    )


def add_satellite_direction_traces(
    fig: go.Figure,
    body_name: str,
    coordinates: Coordinate2D,
    colour: str,
) -> list[int]:
    trace_indices: list[int] = []

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
                legendgroup=f"{body_name}-vectors",
                line={"color": colour},
                marker={"color": colour},
                hoverinfo="name",
                visible="legendonly",
            )
        )

    return trace_indices


def add_kepler_geometry_traces(
    fig: go.Figure,
    body_name: str,
    primary_focus_plot_coordinate: Coordinate2D,
    plot_elements: OrbitalElements,
    colour: str,
) -> list[int]:
    """
    Add the fixed Keplerian geometry belonging to one orbit.

    The moving body marker itself represents the propagated true-anomaly
    position, so there is deliberately no second static "true anomaly" node.
    """
    secondary_focus = secondary_focus_plot_coordinate(
        primary_focus_plot_coordinate,
        plot_elements,
    )
    periapsis = periapsis_plot_coordinate(
        primary_focus_plot_coordinate,
        plot_elements,
    )
    apoapsis = apoapsis_plot_coordinate(
        primary_focus_plot_coordinate,
        plot_elements,
    )
    ascending_node = ascending_node_plot_coordinate(
        primary_focus_plot_coordinate,
        plot_elements,
    )
    descending_node = descending_node_plot_coordinate(
        primary_focus_plot_coordinate,
        plot_elements,
    )

    start_index = len(tuple(fig.data))

    fig.add_trace(
        go.Scatter(
            x=[descending_node.x, ascending_node.x],
            y=[descending_node.y, ascending_node.y],
            mode="lines",
            name=f"{body_name} line of nodes",
            legendgroup=f"{body_name}-kepler",
            line={
                "color": colour,
                "width": 1,
                "dash": "dash",
            },
            visible="legendonly",
        )
    )

    ellipse_centre = Coordinate2D(
        Scalar((float(periapsis.x) + float(apoapsis.x)) / 2),
        Scalar((float(periapsis.y) + float(apoapsis.y)) / 2),
    )

    add_auxiliary_circle(
        fig,
        ellipse_centre,
        float(plot_elements.semi_major_axis),
        periapsis,
        apoapsis,
        generate_angles_on_circle(100),
        name=body_name,
        colour=colour,
    )

    fig.add_trace(
        go.Scatter(
            x=[apoapsis.x, periapsis.x],
            y=[apoapsis.y, periapsis.y],
            mode="lines",
            name=f"{body_name} apsis line",
            legendgroup=f"{body_name}-kepler",
            line={
                "color": colour,
                "width": 1,
                "dash": "dot",
            },
            visible="legendonly",
        )
    )

    nodes = [
        PlotNode(
            f"{body_name} secondary focus",
            secondary_focus,
        ),
        PlotNode(
            f"{body_name} periapsis",
            periapsis,
        ),
        PlotNode(
            f"{body_name} apoapsis",
            apoapsis,
        ),
        PlotNode(
            f"{body_name} ascending node",
            ascending_node,
        ),
        PlotNode(
            f"{body_name} descending node",
            descending_node,
        ),
    ]

    add_plot_nodes(fig, nodes)

    trace_indices = list(range(start_index, len(tuple(fig.data))))

    for trace_index in trace_indices:
        fig.data[trace_index].legendgroup = f"{body_name}-kepler"
        fig.data[trace_index].visible = "legendonly"

    return trace_indices


def add_orbiting_body_2d(
    fig: go.Figure,
    primary_focus_plot_coordinate: Coordinate2D,
    settings: PlotOrbital2DSettings,
    central_body_mass_kg: float,
    body: OrbitingBody2D,
    colour: str,
) -> tuple[go.Figure, int, int, list[int]]:
    plot_elements = scale_orbital_elements_for_plot(
        body.elements,
        Distance(Scalar(settings.distance_scale)),
    )

    coordinates = _initial_body_coordinates(
        primary_focus_plot_coordinate,
        central_body_mass_kg,
        body,
        plot_elements,
    )

    body_trace_index = len(tuple(fig.data))

    fig.add_trace(
        go.Scatter(
            x=[coordinates.x],
            y=[coordinates.y],
            mode="markers",
            name=body.name,
            legendgroup=body.name,
            marker={
                "size": body.radius_m / settings.distance_scale + 5,
                "color": colour,
                "line": {
                    "color": colour,
                    "width": 2,
                },
            },
            hovertext=[body.name],
            hoverinfo="text",
        )
    )

    label_trace_index = len(tuple(fig.data))

    fig.add_trace(
        go.Scatter(
            x=[coordinates.x],
            y=[coordinates.y],
            mode="markers+text",
            name=f"{body.name} label",
            legendgroup=body.name,
            text=[body.name],
            textposition="top center",
            marker={
                "size": 1,
                "color": "rgba(0,0,0,0)",
                "line": {
                    "color": "rgba(0,0,0,0)",
                    "width": 0,
                },
            },
            hoverinfo="skip",
            showlegend=False,
        )
    )

    add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PlotPerifocalOrbitLine(
            name=f"{body.name} orbit",
            orbital_elements=plot_elements,
            colour=colour,
        ),
        steps=settings.orbit_points,
    )

    if body.is_satellite:
        add_kepler_geometry_traces(
            fig,
            body.name,
            primary_focus_plot_coordinate,
            plot_elements,
            colour,
        )

        vector_trace_indices = add_satellite_direction_traces(
            fig,
            body.name,
            coordinates,
            colour,
        )
    else:
        vector_trace_indices = []

    return (
        fig,
        body_trace_index,
        label_trace_index,
        vector_trace_indices,
    )


def generate_orbital_slider_data(
    settings: PlotOrbital2DSettings,
    primary_focus_plot_coordinate: Coordinate2D,
    central_body_mass_kg: float,
    orbiting_bodies: list[OrbitingBody2D],
    body_trace_indices: list[int],
    label_trace_indices: list[int],
    vector_trace_indices: list[list[int]],
    propagation_orbits: float,
) -> list[dict]:
    if propagation_orbits <= 0:
        raise ValueError("propagation_orbits must be greater than 0.")

    reference_period = _reference_period(
        central_body_mass_kg,
        orbiting_bodies,
    )
    total_elapsed_time = reference_period * propagation_orbits

    steps: list[dict] = []

    for step_index in range(settings.slider_steps):
        fraction = step_index / (settings.slider_steps - 1)
        elapsed_time = total_elapsed_time * fraction

        body_x_updates: list[list[float]] = []
        body_y_updates: list[list[float]] = []

        label_x_updates: list[list[float]] = []
        label_y_updates: list[list[float]] = []
        label_text_updates: list[list[str]] = []

        vector_x_updates: list[list[float]] = []
        vector_y_updates: list[list[float]] = []
        vector_update_indices: list[int] = []

        for index, body in enumerate(orbiting_bodies):
            plot_elements = scale_orbital_elements_for_plot(
                body.elements,
                Distance(Scalar(settings.distance_scale)),
            )

            mu = gravitational_parameter(
                Mass(central_body_mass_kg),
                Mass(body.mass_kg),
            )

            eccentric_anomaly = eccentric_anomaly_at_time(
                body.elements,
                Second(Scalar(elapsed_time)),
                mu,
            )

            true_anomaly = true_anomaly_from_eccentric_anomaly(
                eccentric_anomaly,
                plot_elements.eccentricity,
            )

            coordinates = coordinates_for_elements(
                primary_focus_plot_coordinate,
                plot_elements,
                eccentric_anomaly,
            )

            distance_metres = scale_distance_to_distance(
                euclidian_distance(
                    Coordinate2D(
                        coordinates.x,
                        coordinates.y,
                    ),
                    primary_focus_plot_coordinate,
                ),
                settings.distance_scale,
            )

            velocity_m_s = vis_viva(
                mu=mu,
                radius=distance_metres,
                a=SemiMajorAxis(
                    scale_distance_to_distance(
                        plot_elements.semi_major_axis,
                        settings.distance_scale,
                    )
                ),
            )

            body_x_updates.append([coordinates.x])
            body_y_updates.append([coordinates.y])

            label_x_updates.append([coordinates.x])
            label_y_updates.append([coordinates.y])
            label_text_updates.append(
                [
                    f"{body.name}<br>"
                    f"r = {distance_metres:.2f} m<br>"
                    f"v = {velocity_m_s:.2f} m/s<br>"
                    f"θ = {float(true_anomaly):.3f} rad<br>"
                    f"t = {elapsed_time:.2f} s"
                ]
            )

            if not body.is_satellite:
                continue

            position_vector = position_displacement(
                Coordinate3D(
                    coordinates.x,
                    coordinates.y,
                    Scalar(0),
                ),
                Coordinate3D(
                    primary_focus_plot_coordinate.x,
                    primary_focus_plot_coordinate.y,
                    Scalar(0),
                ),
            )

            velocity_vector = tangent_vector_for_plot(
                primary_focus_plot_coordinate,
                plot_elements,
                eccentric_anomaly,
            )

            direction_vectors = [
                radial(position_vector),
                anti_radial(position_vector),
                prograde(velocity_vector),
                retrograde(velocity_vector),
                normal(StateVector(position_vector, velocity_vector)),
                anti_normal(StateVector(position_vector, velocity_vector)),
            ]

            for direction_vector, trace_index in zip(
                direction_vectors,
                vector_trace_indices[index],
            ):
                xs, ys = vector_line(
                    coordinates,
                    direction_vector[0],
                    settings,
                )

                vector_x_updates.append(xs)
                vector_y_updates.append(ys)
                vector_update_indices.append(trace_index)

        update = {
            "x": (body_x_updates + label_x_updates + vector_x_updates),
            "y": (body_y_updates + label_y_updates + vector_y_updates),
            "text": (
                [[] for _ in body_trace_indices]
                + label_text_updates
                + [[] for _ in vector_update_indices]
            ),
        }

        steps.append(
            {
                "method": "restyle",
                "args": [
                    update,
                    (body_trace_indices + label_trace_indices + vector_update_indices),
                ],
                "label": f"{fraction * propagation_orbits:.2f}",
            }
        )

    return steps


def build_orbital_system_2d_figure(
    settings: PlotOrbital2DSettings,
    central_body_name: str,
    central_body_radius_m: float,
    central_body_mass_kg: float,
    orbiting_bodies: list[OrbitingBody2D],
    *,
    propagation_orbits: float = 1.0,
    title: str = "2D orbital system",
) -> go.Figure:
    """
    Build a planar orbital-system visualisation.

    Every orbiting body is propagated independently with a two-body model
    relative to the central body. This is not an N-body simulation.
    """
    if not orbiting_bodies:
        raise ValueError("At least one orbiting body is required.")

    if propagation_orbits <= 0:
        raise ValueError("propagation_orbits must be greater than 0.")

    primary_focus_plot_coordinate = plot_origin()
    fig = go.Figure()

    body_trace_indices: list[int] = []
    label_trace_indices: list[int] = []
    vector_trace_indices: list[list[int]] = []

    satellite_colour_cycle = cycle(SATELLITE_COLOURS)

    for body in orbiting_bodies:
        if body.colour is not None:
            colour = body.colour
        elif body.is_satellite:
            colour = next(satellite_colour_cycle)
        else:
            colour = "grey"

        (
            fig,
            body_trace_index,
            label_trace_index,
            body_vector_trace_indices,
        ) = add_orbiting_body_2d(
            fig,
            primary_focus_plot_coordinate,
            settings,
            central_body_mass_kg,
            body,
            colour,
        )

        body_trace_indices.append(body_trace_index)
        label_trace_indices.append(label_trace_index)
        vector_trace_indices.append(body_vector_trace_indices)

    fig = figure_planetary_body(
        fig,
        primary_focus_plot_coordinate,
        central_body_radius_plot(
            central_body_radius_m,
            settings.distance_scale,
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
        title=title,
    )

    fig = figure_slider(
        fig,
        generate_orbital_slider_data(
            settings,
            primary_focus_plot_coordinate,
            central_body_mass_kg,
            orbiting_bodies,
            body_trace_indices,
            label_trace_indices,
            vector_trace_indices,
            propagation_orbits,
        ),
    )

    fig = add_plot_centre(
        fig,
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )

    for slider in fig.layout.sliders:
        slider.currentvalue.prefix = "Reference-body orbits: "

    return fig


def add_auxiliary_circle(
    fig: go.Figure,
    ellipse_centre: Coordinate2D,
    semi_major_axis: float,
    periapsis: Coordinate2D,
    apoapsis: Coordinate2D,
    eccentric_anomalies: list[Radians],
    *,
    name: str,
    colour: str,
) -> None:
    """Add the auxiliary circle centred on the orbital ellipse centre.

    Eccentric anomaly is measured on this circle from the periapsis direction.
    The periapsis/apoapsis coordinates keep the circle aligned with an orbit
    whose argument of periapsis rotates it in the plot plane.
    """
    major_axis_direction_x = (float(periapsis.x) - float(apoapsis.x)) / (
        2 * semi_major_axis
    )
    major_axis_direction_y = (float(periapsis.y) - float(apoapsis.y)) / (
        2 * semi_major_axis
    )

    fig.add_trace(
        go.Scatter(
            x=[
                float(ellipse_centre.x)
                + semi_major_axis
                * (
                    math.cos(float(eccentric_anomaly)) * major_axis_direction_x
                    - math.sin(float(eccentric_anomaly)) * major_axis_direction_y
                )
                for eccentric_anomaly in eccentric_anomalies
            ],
            y=[
                float(ellipse_centre.y)
                + semi_major_axis
                * (
                    math.cos(float(eccentric_anomaly)) * major_axis_direction_y
                    + math.sin(float(eccentric_anomaly)) * major_axis_direction_x
                )
                for eccentric_anomaly in eccentric_anomalies
            ],
            mode="lines",
            name=f"{name} auxiliary circle",
            legendgroup=f"{name}-kepler",
            line={"color": colour, "dash": "dash"},
            visible="legendonly",
        )
    )


def build_default_orbit_visualiser_2d_figure(
    satellites: list[OrbitingBody2D] | None = None,
    settings: PlotOrbital2DSettings | None = None,
    propagation_orbits: float = 1.0,
) -> go.Figure:
    satellite_bodies = satellites or [
        moon_orbiting_body(),
    ]

    # TODO: Add default celestial bodies like the Moon here.
    bodies = [
        *satellite_bodies,
    ]

    title = "Earth-Moon-Satellite orbital system (@ epoch)"

    if satellite_bodies:
        satellite_names = ", ".join(satellite.name for satellite in satellite_bodies)
        title += f" + {satellite_names}"

    return build_orbital_system_2d_figure(
        settings=settings or DEFAULT_PLOT_SETTINGS,
        central_body_name="Earth",
        central_body_radius_m=EARTH_RADIUS_M,
        central_body_mass_kg=EARTH_MASS_KG,
        orbiting_bodies=bodies,
        propagation_orbits=propagation_orbits,
        title=title,
    )


def main() -> None:
    build_default_orbit_visualiser_2d_figure().show()


if __name__ == "__main__":
    main()
