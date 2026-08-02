import datetime

import plotly.graph_objects as go

from astronomy_types import Distance, Scalar

from afmaths.constants import (
    EARTH_MU,
    EARTH_RADIUS,
    EUTELSAT_EUTE_117_NORAD_ID,
    GALILEO_7_NORAD_ID,
    ISS_NORAD_ID,
    MOLNIYA_3_50_NORAD_ID,
)
from afmaths.physics.space.astronomy.time_functions import (
    julian_date_delta,
    seconds_from_julian_date_delta,
)
from afmaths.physics.space.celestial_mechanics import (
    orbital_elements_from_state_vectors,
    state_vector_at_time,
)
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    general_orbital_characteristics,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    parse_julian_date,
    parse_norad_id,
)
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)

DISTANCE_SCALE = 1000
BODY_RADIUS_SCALE = 1.0
ORBIT_POINTS = 100

SATELLITE_DISPLAY_RADIUS = Distance(Scalar(200_000))


def visualisation_3d_satellite_earth(tles: list[str]) -> go.Figure:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_MU,
        distance_scale=DISTANCE_SCALE,
        orbit_points=ORBIT_POINTS,
        start_time=datetime.datetime.now(),
        add_prediction_to_orbit=False,
    )

    adjusted_elements = []

    # Adjust elements to current time for each TLE
    for tle in tles:
        current_elements = orbital_elements_from_state_vectors(
            state_vector_at_time(
                orbital_elements_from_tle(tle),
                seconds_from_julian_date_delta(
                    julian_date_delta(parse_julian_date(tle))
                ),
            )
        )
        adjusted_elements.append(current_elements)

    return build_3d_orbit_figure(
        settings=settings,
        title=(
            f"Satellite {parse_norad_id(tles[0])} orbit"
            f"<br>{general_orbital_characteristics(tles[0])}"
        ),
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=BODY_RADIUS_SCALE,
        orbiting_bodies=[
            BodyPlotConfig(
                name=f"SAT: {parse_norad_id(tle)}",
                target_object=elements,
                radius=SATELLITE_DISPLAY_RADIUS,
                radius_scale=BODY_RADIUS_SCALE,
            )
            for elements, tle in zip(adjusted_elements, tles)
        ],
    )
