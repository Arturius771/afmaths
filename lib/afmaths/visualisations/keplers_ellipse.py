from afmaths.constants import EXAMPLE_ELEMENTS
from afmaths.visualisations.base import build_keplerian_elements_2d_figure
from afmaths.visualisations.helpers import PlotOrbital2DSettings
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
ORBIT_RESOLUTION = 720


def plot_elements_from_example() -> OrbitalElements:
    return OrbitalElements(
        Inclination(EXAMPLE_ELEMENTS.inclination),
        RightAscension(EXAMPLE_ELEMENTS.right_ascension_of_ascending_node),
        ArgumentOfPeriapsis(EXAMPLE_ELEMENTS.argument_of_periapsis),
        SemiMajorAxis(
            Distance(Scalar(EXAMPLE_ELEMENTS.semi_major_axis / DISTANCE_SCALE_KM))
        ),
        Eccentricity(EXAMPLE_ELEMENTS.eccentricity),
        TrueAnomaly(EXAMPLE_ELEMENTS.true_anomaly),
    )


def main() -> None:
    build_keplerian_elements_2d_figure(
        settings=PlotOrbital2DSettings(
            distance_scale=DISTANCE_SCALE_KM,
            plot_width=600,
            plot_height=1000,
        ),
        elements=plot_elements_from_example(),
        orbit_resolution=ORBIT_RESOLUTION,
    ).show()


if __name__ == "__main__":
    main()
