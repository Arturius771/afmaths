from afmaths.constants import OTHER_EXAMPLE_ELEMENTS
from afmaths.physics.space.space_engineering import EXAMPLE_ELEMENTS
from astronomy_types import (
    ArgumentOfPerigee,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)

from afmaths.visualisations.base_orbit_plot import Base2DOrbitPlot
from afmaths.visualisations.helpers import OrbitPlot2DSettings

DISTANCE_SCALE_KM = 12_824.9333333


class EarthMoon2DOrbitPlot(Base2DOrbitPlot):
    @property
    def title_prefix(self) -> str:
        return "Earth-Moon system"

    @property
    def central_body_name(self) -> str:
        return "Earth"

    @property
    def central_body_radius_km(self) -> float:
        return 6_371.0

    @property
    def central_body_mass_kg(self) -> float:
        return 5.9722e24

    @property
    def orbiting_body_names(self) -> list[str]:
        return ["Moon", "Sat"]

    @property
    def orbiting_body_radius_km(self) -> list[float]:
        return [1_737.4, 1_737.4]

    @property
    def orbiting_body_mass_kg(self) -> list[float]:
        return [7.346e22, 1000]

    @property
    def orbital_elements(self) -> list[OrbitalElements]:
        return [
            OrbitalElements(
                Inclination(EXAMPLE_ELEMENTS.inclination),
                RightAscension(EXAMPLE_ELEMENTS.right_ascension_of_ascending_node),
                ArgumentOfPerigee(EXAMPLE_ELEMENTS.argument_of_perigee),
                SemiMajorAxis(
                    Distance(
                        Scalar(EXAMPLE_ELEMENTS.semi_major_axis / DISTANCE_SCALE_KM)
                    )
                ),
                Eccentricity(EXAMPLE_ELEMENTS.eccentricity),
                TrueAnomaly(EXAMPLE_ELEMENTS.true_anomaly),
            ),
            OrbitalElements(
                Inclination(OTHER_EXAMPLE_ELEMENTS.inclination),
                RightAscension(
                    OTHER_EXAMPLE_ELEMENTS.right_ascension_of_ascending_node
                ),
                ArgumentOfPerigee(OTHER_EXAMPLE_ELEMENTS.argument_of_perigee),
                SemiMajorAxis(
                    Distance(
                        Scalar(
                            OTHER_EXAMPLE_ELEMENTS.semi_major_axis / DISTANCE_SCALE_KM
                        )
                    )
                ),
                Eccentricity(OTHER_EXAMPLE_ELEMENTS.eccentricity),
                TrueAnomaly(OTHER_EXAMPLE_ELEMENTS.true_anomaly),
            ),
        ]


if __name__ == "__main__":
    settings = OrbitPlot2DSettings(
        distance_scale_km=DISTANCE_SCALE_KM,
    )

    EarthMoon2DOrbitPlot(settings).show()
