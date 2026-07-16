import datetime
import random

from astronomy_types import Distance, GravitationalParameter, Scalar

from afmaths.constants import (
    EARTH_MU,
    EARTH_RADIUS,
    EUTELSAT_EUTE_117_NORAD_ID,
    GALILEO_7_NORAD_ID,
    ISS_NORAD_ID,
    MOLNIYA_3_50_NORAD_ID,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
)
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)

DISTANCE_SCALE = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 100

SATELLITE_DISPLAY_RADIUS = Distance(Scalar(200_000))


def visualisation_3d_satellite_earth(bodies: list[BodyPlotConfig]):
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_MU,
        distance_scale=DISTANCE_SCALE,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        add_prediction_to_orbit=False,
    )

    return build_3d_orbit_figure(
        settings=settings,
        title="Earth Artificial Satellites",
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbiting_bodies=bodies,
    ).show()


if __name__ == "__main__":
    random_tle = random.randrange(1, 69999)
    visualisation_3d_satellite_earth(
        [
            BodyPlotConfig(
                name="ISS",
                target=orbital_elements_from_tle(get_tle_from_norad_id(ISS_NORAD_ID)),
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            ),
            BodyPlotConfig(
                name="EUTE 117",
                target=orbital_elements_from_tle(
                    get_tle_from_norad_id(EUTELSAT_EUTE_117_NORAD_ID)
                ),
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            ),
            BodyPlotConfig(
                name="MOLNIYA 3 50",
                target=orbital_elements_from_tle(
                    get_tle_from_norad_id(MOLNIYA_3_50_NORAD_ID)
                ),
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            ),
            BodyPlotConfig(
                name="Galileo 7",
                target=orbital_elements_from_tle(
                    get_tle_from_norad_id(GALILEO_7_NORAD_ID)
                ),
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            ),
            BodyPlotConfig(
                name=f"Random: {random_tle}",
                target=orbital_elements_from_tle(get_tle_from_norad_id(random_tle)),
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            ),
        ]
    )
