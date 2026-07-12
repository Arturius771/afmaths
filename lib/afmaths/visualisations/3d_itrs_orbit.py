import datetime

from astronomy_types import Epoch, GravitationalParameter, Scalar, JulianDate, Second
from afmaths.constants import ISS_NORAD_ID, MINUTES_PER_DAY
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    state_vector_at_time,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    parse_epoch,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.transformations import itrs_positions_from_gcrs_position
from afmaths.visualisations.base import OrbitPlotSettings, build_3d_itrs_orbit_figure
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget

DISTANCE_SCALE_KM = 10_000
BODY_RADIUS_SCALE = 5.0
ORBIT_POINTS = 50
EARTH_RADIUS_KM = 6_371.0
EARTH_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398_600.4418))

if __name__ == "__main__":
    tle = get_tle_from_norad_id(ISS_NORAD_ID)
    orbital_elements = orbital_elements_from_tle(tle)

    gcrs_positions = [
        state_vector_at_time(
            orbital_elements,
            Second(Scalar(minute * 60)),
            EARTH_MU_KM_CUBED,
        ).position
        for minute in range(MINUTES_PER_DAY)
    ]

    # assuming this has already been converted properly to a real JulianDate
    epoch = Epoch(JulianDate(Scalar(float(parse_epoch(tle)))))

    itrs_positions = itrs_positions_from_gcrs_position(
        gcrs_positions,
        epoch,
    )

    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_GRAVITATIONAL_PARAMETER,
        distance_scale_km=DISTANCE_SCALE_KM,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=1),
        add_prediction_to_orbit=False,
    )

    build_3d_itrs_orbit_figure(
        settings=settings,
        itrs_positions=itrs_positions,
        title="ISS ITRS orbit view",
        central_body_name="Earth",
        central_body_radius_km=EARTH_RADIUS_KM,
        central_body_radius_scale=1.0,
        orbit_name="ISS ITRS track",
    ).show()
