import math

from afmaths.visualisations.helpers import (
    EXAMPLE_ELEMENTS,
    add_moveable_planetary_body,
    add_orbit_line,
    add_planetary_body,
    add_plot_centre,
    attach_slider,
    calculate_central_body_position,
    generate_info_slider_steps,
    set_figure_layout,
)
import plotly.graph_objects as go
from afmaths.geometry import (
    calculate_semi_minor_axis,
)
from astronomy_types import (
    Anomaly,
    EccentricAnomaly,
    Radians,
    Scalar,
    Distance,
    Coordinate2D,
    GravitationalParameter,
    Vector2D,
)
from afmaths.astrodynamics import (
    generate_relative_coordinate_from_eccentric_anomaly,
)

# =========================================================
# 🧭 SYSTEM PARAMETERS (ONLY EDIT THESE)
# =========================================================

PLOT_MIN = Vector2D(x=0, y=0)
PLOT_MAX = Vector2D(x=70, y=70)
PLOT_WIDTH = 800
PLOT_HEIGHT = 800
DISTANCE_SCALE_KM = 12824.9333333  # 1 x/y on plot = ?
PRIMARY_BODY_RADIUS_KM = 6371 / DISTANCE_SCALE_KM  # visual radius of Primary body
NUM_STEPS = 100  # slider resolution
PRIMARY_BODY_LABEL = "Earth"
SECONDARY_BODY_LABEL = "Moon"

# =========================================================
# 🎨 BUILD FIGURE
# =========================================================
central_point = Coordinate2D(
    PLOT_MAX.x / 2,
    PLOT_MAX.y / 2,
)
primary_coordinates = calculate_central_body_position(central_point, EXAMPLE_ELEMENTS)
b = calculate_semi_minor_axis(
    EXAMPLE_ELEMENTS.semi_major_axis, EXAMPLE_ELEMENTS.eccentricity
)

add_plot_centre(
    attach_slider(
        set_figure_layout(
            add_planetary_body(
                add_orbit_line(
                    add_moveable_planetary_body(
                        go.Figure(),
                        generate_relative_coordinate_from_eccentric_anomaly(
                            central_point,
                            EXAMPLE_ELEMENTS.semi_major_axis,
                            b,
                            EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
                        ),
                        SECONDARY_BODY_LABEL,
                        "white",
                        "grey",
                    ),
                    central_point,
                    EXAMPLE_ELEMENTS,
                ),
                primary_coordinates,
                Distance(Scalar(PRIMARY_BODY_RADIUS_KM)),
                PRIMARY_BODY_LABEL,
                "Black",
                "blue",
                "green",
            ),
            PLOT_WIDTH,
            PLOT_HEIGHT,
            PLOT_MIN,
            PLOT_MAX,
        ),
        generate_info_slider_steps(
            NUM_STEPS,
            central_point,
            primary_coordinates,
            EXAMPLE_ELEMENTS,
            b,
            DISTANCE_SCALE_KM,
            GravitationalParameter(Scalar(398600.4418)),
        ),
    ),
    central_point,
).show()
