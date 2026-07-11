import datetime

from astronomy_types import GravitationalParameter, Scalar

from afmaths.constants import ISS_NORAD_ID
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

DISTANCE_SCALE_KM = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 50

EARTH_RADIUS_KM = 6_371.0
ISS_RADIUS = 200
EARTH_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398_600.4418))


if __name__ == "__main__":
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_GRAVITATIONAL_PARAMETER,
        distance_scale_km=DISTANCE_SCALE_KM,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=15),
        add_prediction_to_orbit=False,
    )

    build_3d_orbit_figure(
        settings=settings,
        title="Earth-Moon system",
        central_body_name="Earth",
        central_body_radius_km=EARTH_RADIUS_KM,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbiting_bodies=[
            BodyPlotConfig(
                name="ISS",
                target=orbital_elements_from_tle(get_tle_from_norad_id(ISS_NORAD_ID)),
                radius_km=ISS_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            )
        ],
    ).show()
