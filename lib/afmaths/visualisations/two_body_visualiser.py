import math

import plotly.graph_objects as go

from afmaths.visualisations.helpers import (
    EXAMPLE_ELEMENTS,
    figure_circle,
    figure_moveable_planetary_body,
    figure_orbit_line,
    figure_planetary_body,
    figure_plot_centre,
    figure_slider,
    plot_foci_positions,
    generate_orbital_slider,
    figure_layout,
)
from afmaths.geometry import calculate_foci, calculate_semi_minor_axis
from afmaths.astrodynamics import generate_relative_coordinate_from_eccentric_anomaly

from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    Eccentricity,
    GravitationalParameter,
    Inclination,
    OrbitalElements,
    Radians,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
    Vector2D,
)

# =========================================================
# 🧭 SYSTEM PARAMETERS
# =========================================================

PLOT_MIN = Vector2D(x=0, y=0)
PLOT_MAX = Vector2D(x=70, y=70)
PLOT_WIDTH = 800
PLOT_HEIGHT = 800
DISTANCE_SCALE_KM = 12824.9333333  # 1 plot unit = this many km
PRIMARY_BODY_RADIUS_KM = 6371
PRIMARY_BODY_RADIUS_PLOT = PRIMARY_BODY_RADIUS_KM / DISTANCE_SCALE_KM
NUM_STEPS = 100
PRIMARY_BODY_LABEL = "Earth"
SECONDARY_BODY_LABEL = "Moon"
GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398600.4418))


PLOT_ELEMENTS = OrbitalElements(
    Inclination(EXAMPLE_ELEMENTS.inclination),
    RightAscension(EXAMPLE_ELEMENTS.right_ascension_of_ascending_node),
    ArgumentOfPerigee(EXAMPLE_ELEMENTS.argument_of_perigee),
    SemiMajorAxis(
        Distance(Scalar(EXAMPLE_ELEMENTS.semi_major_axis / DISTANCE_SCALE_KM))
    ),
    Eccentricity(EXAMPLE_ELEMENTS.eccentricity),
    TrueAnomaly(EXAMPLE_ELEMENTS.true_anomaly),
)


# =========================================================
# 🎨 BUILD FIGURE
# =========================================================

central_point = Coordinate2D(
    PLOT_MAX.x / 2,
    PLOT_MAX.y / 2,
)

primary_coordinates = plot_foci_positions(
    central_point,
    PLOT_ELEMENTS,
)

semi_minor_axis = calculate_semi_minor_axis(
    PLOT_ELEMENTS.semi_major_axis,
    PLOT_ELEMENTS.eccentricity,
)

figure_plot_centre(
    figure_slider(
        figure_layout(
            figure_circle(  # Foci
                figure_planetary_body(
                    figure_orbit_line(
                        figure_moveable_planetary_body(
                            go.Figure(),
                            generate_relative_coordinate_from_eccentric_anomaly(
                                central_point,
                                PLOT_ELEMENTS.semi_major_axis,
                                semi_minor_axis,
                                EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
                            ),
                            SECONDARY_BODY_LABEL,
                            "white",
                            "grey",
                        ),
                        central_point,
                        PLOT_ELEMENTS,
                    ),
                    primary_coordinates,
                    Distance(Scalar(PRIMARY_BODY_RADIUS_PLOT)),
                    PRIMARY_BODY_LABEL,
                    "Black",
                    "blue",
                    "green",
                ),
                plot_foci_positions(central_point, PLOT_ELEMENTS, 1),
                Distance(Scalar(0.1)),
                "red",
                "red",
            ),
            PLOT_WIDTH,
            PLOT_HEIGHT,
            PLOT_MIN,
            PLOT_MAX,
        ),
        generate_orbital_slider(
            NUM_STEPS,
            central_point,
            primary_coordinates,
            PLOT_ELEMENTS,
            semi_minor_axis,
            DISTANCE_SCALE_KM,
            GRAVITATIONAL_PARAMETER,
        ),
    ),
    central_point,
    Distance(Scalar(0.1)),
).show()
