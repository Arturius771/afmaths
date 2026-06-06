import datetime

from astronomy_types import GravitationalParameter, Scalar

from afmaths.physics.space.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base_orbit_plot import Base3DOrbitPlot
from afmaths.visualisations.helpers import BodyPlotConfig, OrbitPlotSettings

DISTANCE_SCALE_KM = 1_000_000
PLANET_RADIUS_SCALE = 1000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 500

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


class HeliocentricSolarSystemPlot(Base3DOrbitPlot):
    @property
    def title_prefix(self) -> str:
        return "Heliocentric solar system model"

    @property
    def central_body_name(self) -> str:
        return "Sun"

    @property
    def central_body_radius_km(self) -> float:
        return SUN_RADIUS_KM

    @property
    def central_body_radius_scale(self) -> float:
        return SUN_RADIUS_SCALE

    @property
    def central_body_opacity(self) -> float:
        return 0.6

    @property
    def orbiting_bodies(self) -> list[BodyPlotConfig]:
        return PLANETS


def main() -> None:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.SUN,
        gravitational_parameter=SUN_GRAVITATIONAL_PARAMETER,
        distance_scale_km=DISTANCE_SCALE_KM,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=124),
        add_prediction_to_orbit=True,
    )

    HeliocentricSolarSystemPlot(settings).show()


if __name__ == "__main__":
    main()
