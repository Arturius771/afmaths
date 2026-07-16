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

# 41321, 25867, 13901 interesting sat
# 10967 retrograde
if __name__ == "__main__":
    norad_id: int = BEIDOU_IGSO_6 or random.randrange(1, 69999)
    tle = ISS_TLE_EXAMPLE or get_tle_from_norad_id(norad_id)
    total_orbits = round(orbits_per_day(orbital_period_from_tle(tle)))
    point_interval = 60

    visualisation_3d_itrs(tle, total_orbits)
    visualisation_3d_satellite_earth(
        [
            BodyPlotConfig(
                name=f"SAT: {tle}",
                target=orbital_elements_from_tle(tle),
                radius=Distance(Scalar(200_000)),
                radius_scale=1.0,
            )
        ]
    )
    visualisation_2d_ground_track(
        tle, total_orbits, Second(Scalar(point_interval)), True
    ).show()
