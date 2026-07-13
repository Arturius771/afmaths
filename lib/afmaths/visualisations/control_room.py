import random

from afmaths.constants import MINUTES_PER_DAY
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from base import BodyPlotConfig
from iss_earth_3d import visualisation_3d_satellite_earth
from itrs_orbit_3d import visualisation_3d_itrs
from ground_track import visualisation_2d_ground_track

if __name__ == "__main__":
    random_tle = random.randrange(1, 69999)
    track_for_minutes = 280
    visualisation_3d_itrs(random_tle, track_for_minutes)
    visualisation_3d_satellite_earth(
        [
            BodyPlotConfig(
                name=f"SAT: {random_tle}",
                target=orbital_elements_from_tle(get_tle_from_norad_id(random_tle)),
                radius_km=200,
                radius_scale=1.0,
            )
        ]
    )
    visualisation_2d_ground_track(random_tle, track_for_minutes).show()
