import datetime

from astronomy_types import GravitationalParameter, Scalar

from afmaths.physics.space.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)

DISTANCE_SCALE_KM = 10_000
BODY_RADIUS_SCALE = 5.0
ORBIT_POINTS = 50

EARTH_RADIUS_KM = 6_371.0
MOON_RADIUS_KM = 1_737.4
EARTH_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398_600.4418))


def main() -> None:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_GRAVITATIONAL_PARAMETER,
        distance_scale_km=DISTANCE_SCALE_KM,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=15),
        add_prediction_to_orbit=True,
    )

    build_3d_orbit_figure(
        settings=settings,
        title="Earth-Moon system",
        central_body_name="Earth",
        central_body_radius_km=EARTH_RADIUS_KM,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbiting_bodies=[
            BodyPlotConfig(
                name="Moon",
                target=HorizonsCommandTarget.MOON,
                radius_km=MOON_RADIUS_KM,
                radius_scale=BODY_RADIUS_SCALE,
            )
        ],
    ).show()


if __name__ == "__main__":
    main()
