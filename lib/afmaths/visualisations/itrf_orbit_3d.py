import datetime

import plotly.graph_objects as go

from astronomy_types import Epoch, GravitationalParameter, Scalar, JulianDate, Second
from afmaths.constants import (
    BEIDOU_IGSO_6,
    EARTH_RADIUS,
    EUTELSAT_EUTE_117_NORAD_ID,
    GALILEO_7_NORAD_ID,
    ISS_NORAD_ID,
    MINUTES_PER_DAY,
    MOLNIYA_3_50_NORAD_ID,
)
from afmaths.physics.space.astronomy.time_functions import (
    julian_date_from_full_Date,
    minutes_from_seconds,
)
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    EARTH_MU,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    state_vector_at_time,
)
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    general_orbital_characteristics,
    orbits_per_day,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
    parse_full_date,
    parse_norad_id,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id

from afmaths.physics.space.transformations import itrf_positions_from_gcrs_position
from afmaths.visualisations.base import OrbitPlotSettings, build_3d_itrf_orbit_figure
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget

DISTANCE_SCALE = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 50


def visualisation_3d_itrf(tles: list[str], track_for_orbits: float = 3) -> go.Figure:

    itrf_positions = []

    for tle in tles:
        track_for = (
            minutes_from_seconds(orbital_period_from_tle(tle)) * track_for_orbits
        )

        orbital_elements = orbital_elements_from_tle(tle)

        gcrs_positions = [
            state_vector_at_time(
                orbital_elements,
                Second(Scalar(minute * 60)),
                EARTH_MU,
            ).position
            for minute in range(int(track_for))
        ]

        epoch = Epoch(
            JulianDate(Scalar(float(julian_date_from_full_Date(parse_full_date(tle)))))
        )

        itrf_positions.append(itrf_positions_from_gcrs_position(gcrs_positions, epoch))

    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_MU,
        distance_scale=DISTANCE_SCALE,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=1),
        add_prediction_to_orbit=False,
    )

    return build_3d_itrf_orbit_figure(
        settings=settings,
        itrf_positions=itrf_positions,
        title=(
            f"Satellite {parse_norad_id(tles[0])} TLE ground track | Orbits: {track_for_orbits}"
            f"<br>{general_orbital_characteristics(tles[0])}"
        ),
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbit_name=[f"{parse_norad_id(tles[i])}" for i in range(len(tles))],
    )
