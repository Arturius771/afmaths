from afmaths.constants import OTHER_EXAMPLE_ELEMENTS
from afmaths.physics.space.space_engineering import EXAMPLE_ELEMENTS
from afmaths.visualisations.helpers import (
    OrbitPlot2DSettings,
    build_2d_orbit_visualiser_figure,
)

DISTANCE_SCALE_KM = 12_824.9333333


def main() -> None:
    settings = OrbitPlot2DSettings(
        distance_scale_km=DISTANCE_SCALE_KM,
    )

    build_2d_orbit_visualiser_figure(
        settings=settings,
        central_body_name="Earth",
        central_body_radius_km=6_371.0,
        central_body_mass_kg=5.9722e24,
        orbiting_body_names=["Moon", "Sat"],
        orbiting_body_radius_km=[1_737.4, 1_737.4],
        orbiting_body_mass_kg=[7.346e22, 1000],
        orbiting_body_is_satellite=[False, True],
        orbital_elements=[EXAMPLE_ELEMENTS, OTHER_EXAMPLE_ELEMENTS],
        title="Earth-Moon system",
    ).show()


if __name__ == "__main__":
    main()
