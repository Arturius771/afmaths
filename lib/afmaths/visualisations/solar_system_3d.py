import datetime

from astronomy_types import Distance, GravitationalParameter, Scalar

from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)

DISTANCE_SCALE = 1_000_000_000
PLANET_RADIUS_SCALE = 2000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 100

SUN_RADIUS = Distance(Scalar(696_340.0 * 1000))
SUN_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(1.32712440018e20))


PLANETS = [
    BodyPlotConfig(
        "Mercury",
        HorizonsCommandTarget.MERCURY,
        Distance(Scalar(2_439.7 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Venus",
        HorizonsCommandTarget.VENUS,
        Distance(Scalar(6_051.8 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Earth",
        HorizonsCommandTarget.EARTH,
        Distance(Scalar(6_371.0 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Mars",
        HorizonsCommandTarget.MARS,
        Distance(Scalar(3_389.5 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Jupiter",
        HorizonsCommandTarget.JUPITER,
        Distance(Scalar(69_911.0 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Saturn",
        HorizonsCommandTarget.SATURN,
        Distance(Scalar(58_232.0 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Uranus",
        HorizonsCommandTarget.URANUS,
        Distance(Scalar(25_362.0 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
    BodyPlotConfig(
        "Neptune",
        HorizonsCommandTarget.NEPTUNE,
        Distance(Scalar(24_622.0 * 1000)),
        PLANET_RADIUS_SCALE,
    ),
]


def main() -> None:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.SUN,
        gravitational_parameter=SUN_GRAVITATIONAL_PARAMETER,
        distance_scale=DISTANCE_SCALE,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=124),
        add_prediction_to_orbit=False,
    )

    build_3d_orbit_figure(
        settings=settings,
        title="Heliocentric solar system model",
        central_body_name="Sun",
        central_body_radius=SUN_RADIUS,
        central_body_radius_scale=SUN_RADIUS_SCALE,
        central_body_opacity=0.6,
        orbiting_bodies=PLANETS,
    ).show()


if __name__ == "__main__":
    main()
