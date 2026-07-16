import random

from afmaths.constants import (
    BEIDOU_IGSO_6,
    GALILEO_7_NORAD_ID,
    ISS_NORAD_ID,
    JAMES_WEBB,
    MINUTES_PER_DAY,
    MOLNIYA_3_50_NORAD_ID,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from base import BodyPlotConfig
from eci_orbit_3d import visualisation_3d_satellite_earth
from itrs_orbit_3d import visualisation_3d_itrs
from ground_track import visualisation_2d_ground_track
from astronomy_types import Distance, Scalar

# 41321, 25867, 13901 interesting sat
# 10967 retrograde
# TODO: investigate why orbits dont align for 25867
if __name__ == "__main__":
    norad_id: int = 25867 or random.randrange(1, 69999)
    track_for_minutes = MINUTES_PER_DAY
    tle = get_tle_from_norad_id(norad_id)

    visualisation_3d_itrs(tle, track_for_minutes)
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
    visualisation_2d_ground_track(tle, track_for_minutes, True).show()
