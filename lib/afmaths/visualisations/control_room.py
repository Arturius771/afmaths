import math
import random

from afmaths.constants import (
    ARIANE_6_FM1_UPPER,
    BEIDOU_IGSO_6,
    GALILEO_7_NORAD_ID,
    ISS_NORAD_ID,
    ISS_TLE_EXAMPLE,
    JAMES_WEBB,
    MINUTES_PER_DAY,
    MOLNIYA_3_50_NORAD_ID,
)
from afmaths.physics.space.astronomy.time_functions import julian_date_now
from afmaths.physics.space.engineering.astrodynamics.ground_track import orbits_per_day
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from base import BodyPlotConfig
from eci_orbit_3d import visualisation_3d_satellite_earth
from itrs_orbit_3d import visualisation_3d_itrs
from ground_track import visualisation_2d_ground_track
from astronomy_types import Distance, Scalar, Second

# 41321, 25867, 13901, 26402 interesting sat
# 10967 retrograde
if __name__ == "__main__":
    norad_id: int = 26402 or random.randrange(1, 69999)
    tle = get_tle_from_norad_id(norad_id)
    total_orbits = round(orbits_per_day(orbital_period_from_tle(tle)) * 10)
    point_interval = 30

    visualisation_3d_itrs(tle, total_orbits)
    visualisation_3d_satellite_earth(
        [
            tle,
            get_tle_from_norad_id(ISS_NORAD_ID),
            get_tle_from_norad_id(26382),
            get_tle_from_norad_id(63326),
            get_tle_from_norad_id(52708),
        ]
    )
    visualisation_2d_ground_track(
        tle, total_orbits, Second(Scalar(point_interval)), True
    ).show()
