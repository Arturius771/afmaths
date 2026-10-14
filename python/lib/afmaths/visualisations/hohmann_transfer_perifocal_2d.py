from __future__ import annotations

import math
from dataclasses import replace

import plotly.graph_objects as go
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
    Vector2D,
    Velocity,
)

from afmaths.constants import EARTH_MU, EARTH_RADIUS, TWO_PI
from afmaths.geometry.geometry import circle_bounding_box, semi_minor_axis
from afmaths.geometry.transformations import translate_ellipse
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    EARTH_MU,
    periapsis_radius,
)
from afmaths.physics.space.type_conversion_helpers import make_eccentric_anomaly
from afmaths.visualisations.visualisation_types import (
    PlotNode,
    PlotOrbital2DSettings,
    PlotPerifocalOrbitLine,
)


def plot_min(settings: PlotOrbital2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_min_x, y=settings.plot_min_y)


def plot_max(settings: PlotOrbital2DSettings) -> Vector2D:
    return Vector2D(x=settings.plot_max_x, y=settings.plot_max_y)


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


def central_body_radius_plot(
    central_body_radius: float,
    distance_scale: float,
) -> Distance:
    return Distance(Scalar(central_body_radius / distance_scale))


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


def transfer_arc_angles(
    start_eccentric_anomaly: EccentricAnomaly,
    arrival_eccentric_anomaly: EccentricAnomaly,
) -> tuple[float, float]:
    start = float(start_eccentric_anomaly)
    end = float(arrival_eccentric_anomaly)

    if end <= start:
        return start, end + TWO_PI

    return start, end


def plotted_radius_from_primary_focus(
    primary_focus_plot_coordinate: Coordinate2D,
    coordinate: Coordinate2D,
) -> float:
    return math.hypot(
        coordinate.x - primary_focus_plot_coordinate.x,
        coordinate.y - primary_focus_plot_coordinate.y,
    )


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


from astronomy_types import (
    Distance,
    Eccentricity,
    Inclination,
    Ratio,
    RightAscension,
    Scalar,
)

from afmaths.afmath_types import OrbitalDirection
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    orbit_altitude,
    orbit_radius,
)
from afmaths.physics.space.engineering.astrodynamics.hohmann_transfer import (
    hohmann_transfer_parameters,
)
from afmaths.physics.space.engineering.astrodynamics.maneuvers import (
    transfer_eccentricity,
    transfer_semi_major_axis,
)


def transfer_burn_plot_node(
    name: str,
    label: str,
    primary_focus_plot_coordinate: Coordinate2D,
    transfer_orbit: OrbitalElements,
    E: EccentricAnomaly,
    delta_v: Velocity,
    direction: OrbitalDirection,
    time: Second,
) -> PlotNode:
    return PlotNode(
        name=name,
        coordinate=coordinates_for_elements(
            primary_focus_plot_coordinate,
            transfer_orbit,
            E,
        ),
        text=(
            f"{label}<br>"
            f"Direction = {direction}<br>"
            f"Δv = {delta_v:.4f} m/s<br>"
            f"t = {time:.2f} s"
        ),
        colour="red",
        symbol="x",
    )


def build_hohmann_transfer_2d_perifocal_figure(
    settings: PlotOrbital2DSettings,
    initial_orbit: OrbitalElements,
    final_altitude: Distance,
    gravitational_parameter: GravitationalParameter,
    central_body_name: str = "Earth",
    central_body_radius: Distance = EARTH_RADIUS,
    title_prefix: str = "Hohmann transfer in the perifocal frame",
) -> go.Figure:
    """Build a Hohmann transfer plot from SI physical orbital elements."""
    primary_focus_plot_coordinate = plot_origin()

    final_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        ArgumentOfPeriapsis(Radians(Scalar(0))),
        SemiMajorAxis(
            orbit_radius(
                final_altitude,
                central_body_radius,
            )
        ),
        Eccentricity(Ratio(Scalar(0))),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    start_radius = periapsis_radius(
        initial_orbit.semi_major_axis,
        initial_orbit.eccentricity,
    )

    transfer_periapsis_radius = min(start_radius, final_orbit.semi_major_axis)
    transfer_apoapsis_radius = max(start_radius, final_orbit.semi_major_axis)

    transfer_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        (
            ArgumentOfPeriapsis(
                Radians(Scalar(initial_orbit.argument_of_periapsis + math.pi))
            )
            if final_orbit.semi_major_axis < start_radius
            else initial_orbit.argument_of_periapsis
        ),
        SemiMajorAxis(
            transfer_semi_major_axis(
                transfer_periapsis_radius,
                transfer_apoapsis_radius,
            )
        ),
        Eccentricity(
            Ratio(
                Scalar(
                    abs(
                        transfer_eccentricity(
                            transfer_periapsis_radius,
                            transfer_apoapsis_radius,
                        )
                    )
                )
            )
        ),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    distance_scale = Distance(Scalar(settings.distance_scale))
    initial_orbit_for_plot = scale_orbital_elements_for_plot(
        initial_orbit,
        distance_scale,
    )
    final_orbit_for_plot = scale_orbital_elements_for_plot(
        final_orbit,
        distance_scale,
    )
    transfer_orbit_for_plot = scale_orbital_elements_for_plot(
        transfer_orbit,
        distance_scale,
    )
    start_radius_for_plot = distance_to_scale_distance(
        start_radius,
        settings.distance_scale,
    )

    transfer_endpoint_a_eccentric_anomaly = make_eccentric_anomaly(0.0)
    transfer_endpoint_b_eccentric_anomaly = make_eccentric_anomaly(math.pi)

    transfer_endpoint_a_radius = plotted_radius_for_eccentric_anomaly(
        primary_focus_plot_coordinate,
        transfer_orbit_for_plot,
        transfer_endpoint_a_eccentric_anomaly,
    )
    transfer_endpoint_b_radius = plotted_radius_for_eccentric_anomaly(
        primary_focus_plot_coordinate,
        transfer_orbit_for_plot,
        transfer_endpoint_b_eccentric_anomaly,
    )

    endpoint_a_matches_start = abs(transfer_endpoint_a_radius - start_radius_for_plot)
    endpoint_b_matches_start = abs(transfer_endpoint_b_radius - start_radius_for_plot)

    if endpoint_a_matches_start <= endpoint_b_matches_start:
        transfer_burn_eccentric_anomaly = transfer_endpoint_a_eccentric_anomaly
        arrival_burn_eccentric_anomaly = transfer_endpoint_b_eccentric_anomaly
    else:
        transfer_burn_eccentric_anomaly = transfer_endpoint_b_eccentric_anomaly
        arrival_burn_eccentric_anomaly = transfer_endpoint_a_eccentric_anomaly

    delta_v, direction, transfer_time = hohmann_transfer_parameters(
        orbit_altitude(start_radius, central_body_radius),
        final_altitude,
        mu=gravitational_parameter,
    )

    fig = add_plot_node(
        go.Figure(),
        transfer_burn_plot_node(
            name="Transfer burn at initial orbit",
            label="Transfer burn at initial orbit",
            primary_focus_plot_coordinate=primary_focus_plot_coordinate,
            transfer_orbit=transfer_orbit_for_plot,
            E=transfer_burn_eccentric_anomaly,
            delta_v=delta_v[1],
            direction=direction,
            time=Second(Scalar(0)),
        ),
    )

    fig = add_plot_node(
        fig,
        transfer_burn_plot_node(
            name="Arrival burn at final circular orbit",
            label="Arrival burn at final circular orbit",
            primary_focus_plot_coordinate=primary_focus_plot_coordinate,
            transfer_orbit=transfer_orbit_for_plot,
            E=arrival_burn_eccentric_anomaly,
            delta_v=delta_v[2],
            direction=direction,
            time=transfer_time,
        ),
    )

    transfer_arc_start_angle, transfer_arc_end_angle = transfer_arc_angles(
        transfer_burn_eccentric_anomaly,
        arrival_burn_eccentric_anomaly,
    )

    return add_plot_centre(
        figure_layout(
            figure_planetary_body(
                add_perifocal_orbit_line(
                    add_perifocal_orbit_line(
                        add_perifocal_orbit_line(
                            fig,
                            primary_focus_plot_coordinate,
                            PlotPerifocalOrbitLine(
                                name="Initial orbit",
                                orbital_elements=initial_orbit_for_plot,
                                colour="grey",
                            ),
                            steps=settings.orbit_points,
                        ),
                        primary_focus_plot_coordinate,
                        PlotPerifocalOrbitLine(
                            name="Transfer arc",
                            orbital_elements=transfer_orbit_for_plot,
                            colour="orange",
                            start_eccentric_anomaly=transfer_arc_start_angle,
                            end_eccentric_anomaly=transfer_arc_end_angle,
                            show_secondary_focus=True,
                        ),
                        steps=settings.orbit_points,
                    ),
                    primary_focus_plot_coordinate,
                    PlotPerifocalOrbitLine(
                        name="Final circular orbit",
                        orbital_elements=final_orbit_for_plot,
                        colour="grey",
                    ),
                    steps=settings.orbit_points,
                ),
                primary_focus_plot_coordinate,
                central_body_radius_plot(
                    central_body_radius,
                    settings.distance_scale,
                ),
                central_body_name,
                "Black",
                "blue",
                "green",
            ),
            settings.plot_width,
            settings.plot_height,
            plot_min(settings),
            plot_max(settings),
            title=(
                f"{title_prefix}<br>"
                f"Start = initial circular orbit, "
                f"arrival = final circular orbit<br>"
                f"Total Δv = {delta_v[0]:.4f} m/s, "
                f"transfer time = {transfer_time:.2f} s"
            ),
        ),
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )


DISTANCE_SCALE = 12_824.9333333 * 1000
DEFAULT_PLOT_SETTINGS = PlotOrbital2DSettings(
    distance_scale=DISTANCE_SCALE,
    plot_width=1000,
    plot_height=1000,
)

INITIAL_ALTITUDE_M = Distance(Scalar(200_000_000))
TARGET_ALTITUDE_M = Distance(Scalar(140_000_000))


def build_default_hohmann_transfer_2d_perifocal_figure(
    settings: PlotOrbital2DSettings | None = None,
) -> go.Figure:
    return build_hohmann_transfer_2d_perifocal_figure(
        settings=settings or DEFAULT_PLOT_SETTINGS,
        initial_orbit=OrbitalElements(
            Inclination(Radians(Scalar(0))),
            RightAscension(Radians(Scalar(0))),
            ArgumentOfPeriapsis(Radians(Scalar(math.pi / 18))),
            SemiMajorAxis(orbit_radius(INITIAL_ALTITUDE_M, EARTH_RADIUS)),
            Eccentricity(Ratio(Scalar(0.0))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        final_altitude=TARGET_ALTITUDE_M,
        gravitational_parameter=EARTH_MU,
    )
