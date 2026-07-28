import math

from afmaths.constants import EXAMPLE_ELEMENTS
from afmaths.visualisations.base import (
    keplerian_element_plot_nodes,
    orbit_plot_coordinates,
)
from afmaths.visualisations.helpers import (
    PlotOrbital2DSettings,
    add_plot_nodes,
    distance_to_scale_distance,
    figure_layout,
    figure_orbit_line,
    plot_max,
    plot_min,
    plot_origin,
)
from astronomy_types import (
    ArgumentOfPeriapsis,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)
import plotly.graph_objects as go

DISTANCE_SCALE = 12_824.9333333 * 1000
ORBIT_RESOLUTION = 720


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


def plot_elements_from_example() -> OrbitalElements:
    return OrbitalElements(
        Inclination(EXAMPLE_ELEMENTS.inclination),
        RightAscension(EXAMPLE_ELEMENTS.right_ascension_of_ascending_node),
        ArgumentOfPeriapsis(EXAMPLE_ELEMENTS.argument_of_periapsis),
        SemiMajorAxis(
            distance_to_scale_distance(
                Distance(Scalar(EXAMPLE_ELEMENTS.semi_major_axis)),
                DISTANCE_SCALE,
            )
        ),
        Eccentricity(EXAMPLE_ELEMENTS.eccentricity),
        TrueAnomaly(EXAMPLE_ELEMENTS.true_anomaly),
    )


def build_default_keplers_ellipse_2d_figure():
    return build_keplerian_elements_2d_figure(
        settings=PlotOrbital2DSettings(
            distance_scale=DISTANCE_SCALE * 1000,
            plot_width=600,
            plot_height=1000,
        ),
        elements=plot_elements_from_example(),
        orbit_resolution=ORBIT_RESOLUTION,
    )
