from afmaths.constants import EXAMPLE_ELEMENTS
from afmaths.geometry.geometry import calculate_foci
from afmaths.visualisations.base import (
    primary_focus_coordinates_for_elements,
    secondary_focus_coordinates_for_elements,
)
from afmaths.visualisations.helpers import (
    OrbitPlot2DSettings,
    PerifocalOrbitLine,
    PlotNode,
    add_perifocal_orbit_line,
    add_plot_node,
    plot_centre,
    figure_layout,
    add_plot_centre,
    go,
    plot_max,
    plot_min,
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

DISTANCE_SCALE_KM = 12_824.9333333

settings = OrbitPlot2DSettings(
    distance_scale=DISTANCE_SCALE_KM,
)

centre_point = plot_centre(settings)

plot_elements = OrbitalElements(
    Inclination(EXAMPLE_ELEMENTS.inclination),
    RightAscension(EXAMPLE_ELEMENTS.right_ascension_of_ascending_node),
    ArgumentOfPeriapsis(EXAMPLE_ELEMENTS.argument_of_periapsis),
    SemiMajorAxis(
        Distance(Scalar(EXAMPLE_ELEMENTS.semi_major_axis / DISTANCE_SCALE_KM))
    ),
    Eccentricity(EXAMPLE_ELEMENTS.eccentricity),
    TrueAnomaly(EXAMPLE_ELEMENTS.true_anomaly),
)

add_plot_node(
    add_plot_node(
        add_plot_centre(
            add_perifocal_orbit_line(
                figure_layout(
                    go.Figure(),
                    settings.plot_width,
                    settings.plot_height,
                    plot_min(settings),
                    plot_max(settings),
                ),
                centre_point,
                PerifocalOrbitLine(
                    name="Initial orbit",
                    orbital_elements=plot_elements,
                    colour="grey",
                ),
            ),
            centre_point,
            Distance(Scalar(0.1)),
        ),
        PlotNode(
            "Primary focus",
            primary_focus_coordinates_for_elements(settings, plot_elements),
        ),
    ),
    PlotNode(
        "Secondary focus",
        secondary_focus_coordinates_for_elements(
            centre_point,
            plot_elements,
        ),
    ),
).update_layout(title="test").show()
