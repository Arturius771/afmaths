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
    PositionVector,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
    Vector2D,
)

from afmaths.constants import EARTH_MU, EARTH_RADIUS
from afmaths.geometry.geometry import (
    circle_bounding_box,
    normalise_angle,
    semi_minor_axis,
)
from afmaths.geometry.transformations import translate_ellipse
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    EARTH_MU,
    apoapsis_radius,
    periapsis_radius,
)
from afmaths.physics.space.celestial_mechanics.state_vector import (
    perifocal_position_vector,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
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


def forward_true_anomaly_delta_rad(
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
) -> float:
    """Return the forward prograde true-anomaly separation in radians."""
    return normalise_angle(
        Radians(Scalar(float(desired_true_anomaly) - float(initial_true_anomaly)))
    )


def phase_is_higher_than_original(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
) -> bool:
    return phase_orbit_elements.semi_major_axis > original_orbit.semi_major_axis


def expected_shared_apsis_radius(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
) -> Distance:
    """Return the original-orbit apsis radius shared with the phase orbit."""
    radius_function = (
        periapsis_radius
        if phase_is_higher_than_original(phase_orbit_elements, original_orbit)
        else apoapsis_radius
    )
    return radius_function(
        original_orbit.semi_major_axis,
        original_orbit.eccentricity,
    )


AHEAD_BEHIND_CUTOFF_RAD = math.pi


def phase_direction_label(
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
) -> str:
    return (
        "ahead"
        if forward_true_anomaly_delta_rad(initial_true_anomaly, desired_true_anomaly)
        <= AHEAD_BEHIND_CUTOFF_RAD
        else "behind"
    )


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


def align_phase_poi_to_initial_true_anomaly(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
    initial_true_anomaly: TrueAnomaly,
) -> OrbitalElements:
    """Rotate the phase orbit so its shared apsis is at the selected POI."""
    phase_poi_true_anomaly = (
        0.0
        if phase_is_higher_than_original(phase_orbit_elements, original_orbit)
        else math.pi
    )
    poi_direction = original_orbit.argument_of_periapsis + initial_true_anomaly
    phase_argument_of_periapsis = normalise_angle(
        Radians(Scalar(poi_direction - phase_poi_true_anomaly))
    )

    return replace(
        phase_orbit_elements,
        argument_of_periapsis=ArgumentOfPeriapsis(
            Radians(Scalar(phase_argument_of_periapsis))
        ),
    )


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


import math

from astronomy_types import (
    Distance,
    Eccentricity,
    Inclination,
    Ratio,
    RightAscension,
    Scalar,
)

from afmaths.afmath_types import DeltaV
from afmaths.physics.space.engineering.astrodynamics.phase_orbit import (
    phase_orbit_apoapsis,
    phase_orbit_parameters,
    phase_orbit_periapsis,
)


def true_anomaly_plot_node(
    name: str,
    label: str,
    primary_focus_plot_coordinate: Coordinate2D,
    orbital_elements: OrbitalElements,
    true_anomaly_value: TrueAnomaly,
    colour: str,
    symbol: str,
) -> PlotNode:
    """Build a labelled marker at a true anomaly on the plotted orbit."""
    return PlotNode(
        name=name,
        coordinate=plot_coordinate_for_true_anomaly(
            primary_focus_plot_coordinate=primary_focus_plot_coordinate,
            elements=orbital_elements,
            true_anomaly_value=true_anomaly_value,
        ),
        text=f"{label}<br>ta = {true_anomaly_value:.3f} rad",
        colour=colour,
        symbol=symbol,
    )


def phase_poi_label(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
) -> tuple[str, str]:
    if phase_is_higher_than_original(phase_orbit_elements, original_orbit):
        return "shared periapsis", "higher phase orbit"

    return "shared apoapsis", "lower phase orbit"


def phase_poi_eccentric_anomaly_for_plot(
    primary_focus_plot_coordinate: Coordinate2D,
    phase_orbit_for_plot: OrbitalElements,
    expected_shared_apsis_radius_for_plot: Distance,
) -> EccentricAnomaly:
    """
    Pick the plotted phase-orbit endpoint that is actually the shared apsis.

    This avoids assuming that E=0 is visually the right endpoint. It chooses the
    endpoint whose plotted radius from the primary focus matches the expected
    shared original-orbit apsis radius.
    """
    endpoint_a = make_eccentric_anomaly(0.0)
    endpoint_b = make_eccentric_anomaly(math.pi)

    endpoint_a_radius = plotted_radius_for_eccentric_anomaly(
        primary_focus_plot_coordinate,
        phase_orbit_for_plot,
        endpoint_a,
    )

    endpoint_b_radius = plotted_radius_for_eccentric_anomaly(
        primary_focus_plot_coordinate,
        phase_orbit_for_plot,
        endpoint_b,
    )

    endpoint_a_error = abs(endpoint_a_radius - expected_shared_apsis_radius_for_plot)
    endpoint_b_error = abs(endpoint_b_radius - expected_shared_apsis_radius_for_plot)

    if endpoint_a_error <= endpoint_b_error:
        return endpoint_a

    return endpoint_b


def poi_plot_node(
    name: str,
    primary_focus_plot_coordinate: Coordinate2D,
    phase_orbit_for_plot: OrbitalElements,
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
    distance_scale: Distance,
    delta_v: DeltaV,
    phase_period: Second,
) -> PlotNode:
    shared_apsis_label, phase_orbit_label = phase_poi_label(
        phase_orbit_elements,
        original_orbit,
    )

    shared_apsis_radius_for_plot = distance_to_scale_distance(
        expected_shared_apsis_radius(
            phase_orbit_elements,
            original_orbit,
        ),
        distance_scale,
    )

    poi_E = phase_poi_eccentric_anomaly_for_plot(
        primary_focus_plot_coordinate,
        phase_orbit_for_plot,
        shared_apsis_radius_for_plot,
    )

    return PlotNode(
        name=name,
        coordinate=coordinates_for_elements(
            primary_focus_plot_coordinate,
            phase_orbit_for_plot,
            poi_E,
        ),
        text=(
            "POI<br>"
            f"{shared_apsis_label}<br>"
            f"{phase_orbit_label}<br>"
            f"Δv = {delta_v:.4f} m/s<br>"
            f"T₂ = {phase_period:.2f} s"
        ),
        colour="red",
        symbol="x",
    )


def build_phase_orbit_2d_perifocal_figure(
    settings: PlotOrbital2DSettings,
    original_orbit: OrbitalElements,
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
    gravitational_parameter: GravitationalParameter,
    central_body_name: str = "Earth",
    central_body_radius: Distance = EARTH_RADIUS,
    title_prefix: str = "Phasing orbit in the perifocal frame",
) -> go.Figure:
    """
    Build a phase-orbit visualisation.

    `original_orbit` must be supplied in SI physical units (metres), because
    the astrodynamics functions use it with μ in m³/s².

    The plotting copies of the orbits are scaled internally.
    """
    primary_focus_plot_coordinate = plot_origin()

    # signed_phase_delta = phase_true_anomaly_delta(
    #     initial_true_anomaly,
    #     desired_true_anomaly,
    # )

    delta_v, _, phase_orbit_elements = phase_orbit_parameters(
        original_orbit,
        desired_true_anomaly,
        gravitational_parameter,
    )
    phase_orbit_elements = align_phase_poi_to_initial_true_anomaly(
        phase_orbit_elements,
        original_orbit,
        initial_true_anomaly,
    )

    calculated_phase_period = orbital_period(
        phase_orbit_elements.semi_major_axis,
        gravitational_parameter,
    )

    original_orbit_for_plot = scale_orbital_elements_for_plot(
        original_orbit,
        Distance(Scalar(settings.distance_scale)),
    )

    phase_orbit_for_plot = scale_orbital_elements_for_plot(
        phase_orbit_elements,
        Distance(Scalar(settings.distance_scale)),
    )

    return add_plot_centre(
        figure_layout(
            figure_planetary_body(
                add_perifocal_orbit_line(
                    add_perifocal_orbit_line(
                        add_plot_node(
                            add_plot_node(
                                add_plot_node(
                                    go.Figure(),
                                    true_anomaly_plot_node(
                                        name="Initial reference anomaly",
                                        label="Initial reference",
                                        primary_focus_plot_coordinate=primary_focus_plot_coordinate,
                                        orbital_elements=original_orbit_for_plot,
                                        true_anomaly_value=initial_true_anomaly,
                                        colour="blue",
                                        symbol="circle",
                                    ),
                                ),
                                true_anomaly_plot_node(
                                    name="Desired reference anomaly",
                                    label="Desired reference",
                                    primary_focus_plot_coordinate=primary_focus_plot_coordinate,
                                    orbital_elements=original_orbit_for_plot,
                                    true_anomaly_value=desired_true_anomaly,
                                    colour="green",
                                    symbol="diamond",
                                ),
                            ),
                            poi_plot_node(
                                name="POI at shared apsis",
                                primary_focus_plot_coordinate=primary_focus_plot_coordinate,
                                phase_orbit_for_plot=phase_orbit_for_plot,
                                phase_orbit_elements=phase_orbit_elements,
                                original_orbit=original_orbit,
                                distance_scale=Distance(
                                    Scalar(settings.distance_scale)
                                ),
                                delta_v=delta_v,
                                phase_period=calculated_phase_period,
                            ),
                        ),
                        primary_focus_plot_coordinate,
                        PlotPerifocalOrbitLine(
                            name="Original orbit",
                            orbital_elements=original_orbit_for_plot,
                            colour="grey",
                        ),
                        steps=settings.orbit_points,
                    ),
                    primary_focus_plot_coordinate,
                    PlotPerifocalOrbitLine(
                        name="Phase orbit",
                        orbital_elements=phase_orbit_for_plot,
                        colour="orange",
                        show_secondary_focus=True,
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
                f"Initial ta = {initial_true_anomaly:.3f} rad, "
                f"desired ta = {desired_true_anomaly:.3f} rad, "
                f"forward Δta = {forward_true_anomaly_delta_rad(
                    initial_true_anomaly,
                    desired_true_anomaly,
                ):.3f} rad<br>"
                # f"Signed phase Δta = {signed_phase_delta:.3f} rad "
                f"({phase_direction_label(
                        initial_true_anomaly,
                        desired_true_anomaly,
                    )
                }), cutoff = {AHEAD_BEHIND_CUTOFF_RAD:.2f} rad<br>"
                f"Original period = {orbital_period( original_orbit.semi_major_axis, gravitational_parameter,):.2f} s, "
                f"phase period = {calculated_phase_period:.2f} s<br>"
                f"Phase periapsis = {phase_orbit_periapsis(
                    phase_orbit_elements.semi_major_axis,
                    original_orbit,
                ):.2f} m, "
                f"phase apoapsis = {phase_orbit_apoapsis(
                    phase_orbit_elements.semi_major_axis,
                    original_orbit,
                ):.2f} m, "
                f"Δv = {delta_v:.4f} m/s"
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


def build_default_phase_orbit_2d_perifocal_figure(
    settings: PlotOrbital2DSettings | None = None,
) -> go.Figure:
    original_orbit = OrbitalElements(
        Inclination(Radians(Scalar(0))),
        RightAscension(Radians(Scalar(0))),
        ArgumentOfPeriapsis(Radians(Scalar(0.0))),
        SemiMajorAxis(Distance(Scalar(EARTH_RADIUS + INITIAL_ALTITUDE_M))),
        Eccentricity(Ratio(Scalar(0.0))),
        TrueAnomaly(Anomaly(Radians(Scalar(0.0)))),
    )

    return build_phase_orbit_2d_perifocal_figure(
        settings=settings or DEFAULT_PLOT_SETTINGS,
        original_orbit=original_orbit,
        initial_true_anomaly=TrueAnomaly(Anomaly(Radians(Scalar(0.5)))),
        desired_true_anomaly=TrueAnomaly(Anomaly(Radians(Scalar(1.0)))),
        gravitational_parameter=EARTH_MU,
    )
