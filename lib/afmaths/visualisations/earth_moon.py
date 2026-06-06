import datetime

from astronomy_types import GravitationalParameter, Scalar

from afmaths.physics.space.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base_orbit_plot import Base3DOrbitPlot
from afmaths.visualisations.helpers import BodyPlotConfig, OrbitPlotSettings

DISTANCE_SCALE_KM = 10_000
BODY_RADIUS_SCALE = 20.0
ORBIT_POINTS = 500

EARTH_RADIUS_KM = 6_371.0
MOON_RADIUS_KM = 1_737.4
EARTH_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398_600.4418))


class EarthMoonOrbitPlot(Base3DOrbitPlot):
    @property
    def title_prefix(self) -> str:
        return "Earth-Moon system"

    @property
    def central_body_name(self) -> str:
        return "Earth"

    @property
    def central_body_radius_km(self) -> float:
        return EARTH_RADIUS_KM

    @property
    def central_body_radius_scale(self) -> float:
        return BODY_RADIUS_SCALE

    @property
    def orbiting_bodies(self) -> list[BodyPlotConfig]:
        return [
            BodyPlotConfig(
                name="Moon",
                target=HorizonsCommandTarget.MOON,
                radius_km=MOON_RADIUS_KM,
                radius_scale=BODY_RADIUS_SCALE,
            )
        ]


def main() -> None:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_GRAVITATIONAL_PARAMETER,
        distance_scale_km=DISTANCE_SCALE_KM,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=30),
        add_prediction_to_orbit=True,
    )

    EarthMoonOrbitPlot(settings).show()


if __name__ == "__main__":
    main()
