from __future__ import annotations

import argparse
from collections.abc import Callable

import plotly.graph_objects as go

from afmaths.constants import ISS_NORAD_ID
from afmaths.physics.space.engineering.astrodynamics.ground_track import orbits_per_day
from afmaths.physics.space.engineering.two_line_elements import orbital_period_from_tle
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from astronomy_types import Degrees, GeographicCoordinates, Scalar, Second

from collision_detection import build_collision_detection_figure
from control_room import launch_control_room
from eci_orbit_3d import visualisation_3d_satellite_earth
from ground_track import (
    visualisation_2d_ground_track_current_position_propogation,
    visualisation_2d_ground_track_tle_propagation,
)
from hohmann_tradeoff import build_hohmann_tradeoff_figure
from hohmann_transfer_perifocal_2d import (
    build_default_hohmann_transfer_2d_perifocal_figure,
)
from itrf_orbit_3d import visualisation_3d_itrf
from keplers_ellipse_2d import build_default_keplers_ellipse_2d_figure
from moon_earth_3d import build_moon_earth_3d_figure
from newton_iteration import build_newton_iteration_figure
from phase_orbit_2d import build_default_phase_orbit_2d_perifocal_figure
from solar_system_3d import build_solar_system_3d_figure
from two_body_visualiser_2d import build_default_two_body_visualiser_2d_figure
from velocity_time import build_velocity_time_figure


def normalise_name(name: str) -> str:
    return "_".join(name.strip().lower().replace("-", " ").split())


def default_orbit_count(tle: str) -> int:
    return max(1, round(orbits_per_day(orbital_period_from_tle(tle))))


def satellite_figure_builder(
    name: str,
    norad_ids: list[int],
    total_orbits: int | None,
) -> go.Figure:
    tles = [get_tle_from_norad_id(norad_id) for norad_id in norad_ids]
    selected_tle = tles[0]
    orbit_count = total_orbits or default_orbit_count(selected_tle)

    if name == "itrf_orbit_3d":
        return visualisation_3d_itrf(selected_tle, orbit_count)
    if name == "satellite_earth_3d":
        return visualisation_3d_satellite_earth(tles)
    if name == "ground_track_tle":
        return visualisation_2d_ground_track_tle_propagation(
            tle=selected_tle,
            orbit_count=orbit_count,
            show_orbit_markers=True,
        )
    if name == "ground_track_current":
        return visualisation_2d_ground_track_current_position_propogation(
            tle=selected_tle,
            ground_station=GeographicCoordinates(
                Degrees(Scalar(53)),
                Degrees(Scalar(-6)),
            ),
            ground_station_name="Dublin, Ireland",
            ground_station_longitude_range=Degrees(Scalar(5)),
            orbit_count=orbit_count,
        )

    raise ValueError(f"Unknown satellite visualisation: {name}")


STATIC_VISUALISATIONS: dict[str, Callable[[], go.Figure]] = {
    "collision_detection": build_collision_detection_figure,
    "hohmann_tradeoff": build_hohmann_tradeoff_figure,
    "hohmann_transfer_2d": build_default_hohmann_transfer_2d_perifocal_figure,
    "keplers_ellipse_2d": build_default_keplers_ellipse_2d_figure,
    "moon_earth_3d": build_moon_earth_3d_figure,
    "newton_iteration": build_newton_iteration_figure,
    "phase_orbit_2d": build_default_phase_orbit_2d_perifocal_figure,
    "solar_system_3d": build_solar_system_3d_figure,
    "two_body_2d": build_default_two_body_visualiser_2d_figure,
    "velocity_time": build_velocity_time_figure,
}

ALIASES = {
    "controlroom": "control_room",
    "itrf": "itrf_orbit_3d",
    "satellite_earth": "satellite_earth_3d",
    "ground_track": "ground_track_tle",
    "current_ground_track": "ground_track_current",
    "kepler": "keplers_ellipse_2d",
    "solar_system": "solar_system_3d",
    "moon_earth": "moon_earth_3d",
    "two_body": "two_body_2d",
    "hohmann_transfer": "hohmann_transfer_2d",
    "phase_orbit": "phase_orbit_2d",
}

SATELLITE_VISUALISATIONS = {
    "itrf_orbit_3d",
    "satellite_earth_3d",
    "ground_track_tle",
    "ground_track_current",
}


def launch_visualisation(
    name: str,
    norad_ids: list[int] | None = None,
    total_tle_orbits: int | None = None,
    total_current_orbits: int | None = None,
) -> None:
    """Launch one named visualisation or the multi-plot control room."""
    resolved_name = ALIASES.get(normalise_name(name), normalise_name(name))
    resolved_ids = norad_ids or [ISS_NORAD_ID]

    if resolved_name == "control_room":
        selected_tle = get_tle_from_norad_id(resolved_ids[0])
        launch_control_room(
            norad_ids=resolved_ids,
            total_tle_orbits=total_tle_orbits or default_orbit_count(selected_tle),
            total_current_orbits=total_current_orbits
            or default_orbit_count(selected_tle),
        )
        return

    if resolved_name in SATELLITE_VISUALISATIONS:
        satellite_figure_builder(
            resolved_name,
            resolved_ids,
            total_tle_orbits,
        ).show()
        return

    try:
        figure_builder = STATIC_VISUALISATIONS[resolved_name]
    except KeyError as error:
        available = sorted(
            ["control_room", *SATELLITE_VISUALISATIONS, *STATIC_VISUALISATIONS]
        )
        raise ValueError(
            f"Unknown visualisation '{name}'. Available names: {', '.join(available)}"
        ) from error

    figure_builder().show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch an AFMaths Plotly visualisation by name."
    )
    parser.add_argument("name", help='Visualisation name, for example "control room".')
    parser.add_argument(
        "--norad-id",
        dest="norad_ids",
        type=int,
        action="append",
        help="NORAD ID. Repeat to include multiple satellites.",
    )
    parser.add_argument("--tle-orbits", type=int, default=None)
    parser.add_argument("--current-orbits", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    launch_visualisation(
        name=args.name,
        norad_ids=args.norad_ids,
        total_tle_orbits=args.tle_orbits,
        total_current_orbits=args.current_orbits,
    )


if __name__ == "__main__":
    main()
