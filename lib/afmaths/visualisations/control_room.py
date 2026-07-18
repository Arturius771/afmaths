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
    orbital_period_from_tle,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id

from eci_orbit_3d import visualisation_3d_satellite_earth
from itrs_orbit_3d import visualisation_3d_itrs
from ground_track import visualisation_2d_ground_track
from astronomy_types import Scalar, Second


def launch_control_room(
    norad_ids: list[int], total_orbits: int, point_interval: int = 60
):
    for id in norad_ids:
        tle = get_tle_from_norad_id(id)
        visualisation_3d_itrs(tle, total_orbits)

        visualisation_2d_ground_track(
            tle, total_orbits, Second(Scalar(point_interval)), True
        ).show()

    visualisation_3d_satellite_earth([get_tle_from_norad_id(id) for id in norad_ids])


# 41321, 25867, 13901, 26402 interesting sat
# 10967 retrograde
if __name__ == "__main__":
    norad_id: int = ISS_NORAD_ID or random.randrange(1, 69999)
    tle = get_tle_from_norad_id(norad_id)
    total_orbits = round(orbits_per_day(orbital_period_from_tle(tle)))
    point_interval = 30

    launch_control_room(
        [ISS_NORAD_ID, 26402, 26382, 63326, 52708], total_orbits, point_interval
    )
