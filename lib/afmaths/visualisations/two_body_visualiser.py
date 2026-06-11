import plotly.graph_objects as go
from afmaths.visualisations.helpers import (
    figure_circle,
    figure_orbit_line,
    figure_planetary_body,
    figure_plot_centre,
    figure_slider,
    plot_foci_positions,
    generate_orbital_slider_data,
    figure_layout,
)
from afmaths.geometry import semi_minor_axis
from afmaths.physics.space.celestial_mechanics import (
    translate_ellipse_coordinate,
)
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

from afmaths.physics.space.space_engineering import EXAMPLE_ELEMENTS
from afmaths.visualisations.helpers import figure_plot_centre, figure_slider

# =========================================================
# 🧭 SYSTEM PARAMETERS
# =========================================================

PLOT_MIN = Vector2D(x=0, y=0)
PLOT_MAX = Vector2D(x=70, y=70)
PLOT_WIDTH = 800
PLOT_HEIGHT = 800
NUM_STEPS = 51
DISTANCE_SCALE_KM = 12824.9333333  # 1 plot unit = this many km
PRIMARY_BODY_RADIUS_KM = 6371
PRIMARY_BODY_RADIUS_PLOT = PRIMARY_BODY_RADIUS_KM / DISTANCE_SCALE_KM
PRIMARY_BODY_LABEL = "Earth"
SECONDARY_BODY_RADIUS_KM = 1737.4
SECONDARY_BODY_RADIUS_PLOT = SECONDARY_BODY_RADIUS_KM / DISTANCE_SCALE_KM
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

b = semi_minor_axis(
    PLOT_ELEMENTS.semi_major_axis,
    PLOT_ELEMENTS.eccentricity,
)

figure_plot_centre(
    figure_slider(
        figure_layout(
            figure_circle(
                figure_planetary_body(
                    figure_orbit_line(
                        figure_planetary_body(
                            go.Figure(),
                            translate_ellipse_coordinate(
                                central_point,
                                PLOT_ELEMENTS.semi_major_axis,
                                b,
                                EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
                            ),
                            Distance(Scalar(SECONDARY_BODY_RADIUS_PLOT)),
                            SECONDARY_BODY_LABEL,
                            "white",
                            "grey",
                            moveable=True,
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
        generate_orbital_slider_data(
            NUM_STEPS,
            central_point,
            primary_coordinates,
            PLOT_ELEMENTS,
            b,
            DISTANCE_SCALE_KM,
            GRAVITATIONAL_PARAMETER,
        ),
    ),
    central_point,
    Distance(Scalar(0.1)),
).show()
