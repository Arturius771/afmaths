import datetime

from astronomy_types import GravitationalParameter, Scalar

from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)

DISTANCE_SCALE_KM = 1_000_000
PLANET_RADIUS_SCALE = 1000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 50

SUN_RADIUS_KM = 696_340.0
SUN_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(132_712_440_018.0))


PLANETS = [
    BodyPlotConfig(
        "Mercury", HorizonsCommandTarget.MERCURY, 2_439.7, PLANET_RADIUS_SCALE
    ),
    BodyPlotConfig("Venus", HorizonsCommandTarget.VENUS, 6_051.8, PLANET_RADIUS_SCALE),
    BodyPlotConfig("Earth", HorizonsCommandTarget.EARTH, 6_371.0, PLANET_RADIUS_SCALE),
    BodyPlotConfig("Mars", HorizonsCommandTarget.MARS, 3_389.5, PLANET_RADIUS_SCALE),
    BodyPlotConfig("Jupiter", HorizonsCommandTarget.JUPITER, 69_911.0, 80.0),
    BodyPlotConfig("Saturn", HorizonsCommandTarget.SATURN, 58_232.0, 80.0),
    BodyPlotConfig("Uranus", HorizonsCommandTarget.URANUS, 25_362.0, 150.0),
    BodyPlotConfig("Neptune", HorizonsCommandTarget.NEPTUNE, 24_622.0, 150.0),
]


def main() -> None:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.SUN,
        gravitational_parameter=SUN_GRAVITATIONAL_PARAMETER,
        distance_scale_km=DISTANCE_SCALE_KM,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=124),
        add_prediction_to_orbit=False,
    )

    build_3d_orbit_figure(
        settings=settings,
        title="Heliocentric solar system model",
        central_body_name="Sun",
        central_body_radius_km=SUN_RADIUS_KM,
        central_body_radius_scale=SUN_RADIUS_SCALE,
        central_body_opacity=0.6,
        orbiting_bodies=PLANETS,
    ).show()


if __name__ == "__main__":
    main()
