import math

from afmaths.constants import EXAMPLE_ELEMENTS, TWO_PI
from afmaths.physics.space.type_conversion_helpers import make_true_anomaly
from afmaths.visualisations.base import (
    apoapsis_plot_coordinate,
    ascending_node_plot_coordinate,
    current_position_plot_coordinate,
    descending_node_plot_coordinate,
    periapsis_plot_coordinate,
    plot_coordinate_for_true_anomaly,
    scaled_elements,
    secondary_focus_plot_coordinate,
)
from afmaths.visualisations.helpers import (
    PlotNode,
    PlotOrbital2DSettings,
    add_plot_nodes,
    figure_layout,
    figure_orbit_line,
    plot_max,
    plot_min,
    plot_origin,
)
from astronomy_types import (
    Coordinate2D,
    OrbitalElements,
)
import plotly.graph_objects as go

DISTANCE_SCALE = 50
ORBIT_RESOLUTION = 720
DEFAULT_PLOT_SETTINGS = PlotOrbital2DSettings(
    distance_scale=DISTANCE_SCALE,
    plot_width=600,
    plot_height=1000,
    orbit_points=ORBIT_RESOLUTION,
)


def orbit_plot_coordinates(
    elements: OrbitalElements,
    resolution: int,
    primary_focus_plot_coordinate: Coordinate2D = plot_origin(),
) -> list[Coordinate2D]:
    if resolution < 3:
        raise ValueError("resolution must be at least 3")

    return [
        plot_coordinate_for_true_anomaly(
            primary_focus_plot_coordinate,
            elements,
            make_true_anomaly(TWO_PI * index / resolution),
        )
        for index in range(resolution + 1)
    ]


# Subject: orbital geometry / derived plot markers.
def keplerian_element_plot_nodes(
    elements: OrbitalElements,
    primary_focus_plot_coordinate: Coordinate2D = plot_origin(),
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
            "true anomaly",
            current_position_plot_coordinate(primary_focus_plot_coordinate, elements),
        ),
    ]


# Subject: high-level 2D orbital-plane figure composition.
# Builds a single, internally consistent Keplerian-element ellipse plot using the
# focus-origin transform for the orbit line and all markers.
def build_keplerian_elements_2d_figure(
    settings: PlotOrbital2DSettings,
    elements: OrbitalElements,
    orbit_resolution: int | None = None,
    title_prefix: str = "2D orbital-plane ellipse",
) -> go.Figure:
    resolution = orbit_resolution if orbit_resolution is not None else settings.orbit_points
    coordinates = orbit_plot_coordinates(
        elements,
        resolution,
    )

    nodes = keplerian_element_plot_nodes(
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
        f"θ={math.degrees(elements.true_anomaly):.2f}°"
    )

    fig = figure_orbit_line(
        figure_layout(
            go.Figure(),
            settings.plot_width,
            settings.plot_height,
            plot_min(settings),
            plot_max(settings),
            title=title,
        ),
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


def build_default_keplers_ellipse_2d_figure(
    elements: OrbitalElements = EXAMPLE_ELEMENTS,
    settings: PlotOrbital2DSettings | None = None,
    orbit_resolution: int | None = None,
) -> go.Figure:
    plot_settings = settings or DEFAULT_PLOT_SETTINGS
    return build_keplerian_elements_2d_figure(
        settings=plot_settings,
        elements=scaled_elements(elements, plot_settings.distance_scale),
        orbit_resolution=orbit_resolution,
    )
