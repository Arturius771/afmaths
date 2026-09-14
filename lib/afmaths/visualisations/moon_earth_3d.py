import datetime

from afmaths.constants import EARTH_MU, EARTH_RADIUS
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.base import (
    BodyPlotConfig,
    OrbitPlotSettings,
    build_3d_orbit_figure,
)
from astronomy_types import Distance, Scalar

DISTANCE_SCALE = 10_000 * 1000
BODY_RADIUS_SCALE = 5.0
ORBIT_POINTS = 50

MOON_RADIUS = 1_737.4 * 1000


def build_moon_earth_3d_figure(
    *,
    distance_scale: float = DISTANCE_SCALE,
    body_radius_scale: float = BODY_RADIUS_SCALE,
    orbit_points: int = ORBIT_POINTS,
) -> go.Figure:
    settings = OrbitPlotSettings(
        centre=HorizonsCommandTarget.EARTH,
        gravitational_parameter=EARTH_MU,
        distance_scale=distance_scale,
        orbit_points=orbit_points,
        start_time=datetime.datetime.now(),
        time_offset=datetime.timedelta(days=15),
        add_prediction_to_orbit=True,
    )

    return build_3d_orbit_figure(
        settings=settings,
        title="Earth-Moon system",
        central_body_name="Earth",
        central_body_radius=EARTH_RADIUS,
        central_body_radius_scale=body_radius_scale,
        orbiting_bodies=[
            BodyPlotConfig(
                name="Moon",
                target_object=HorizonsCommandTarget.MOON,
                radius=Distance(Scalar(MOON_RADIUS)),
                radius_scale=body_radius_scale,
            )
        ],
    )
