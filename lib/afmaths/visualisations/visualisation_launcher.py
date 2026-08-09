from __future__ import annotations

import argparse
from collections.abc import Callable

import plotly.graph_objects as go

from afmaths.afmath_types import GroundStation
from afmaths.constants import EXAMPLE_ELEMENTS, ISS_NORAD_ID, KILCUMMIN_GROUND_STATION
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    orbital_elements_from_degrees,
)
from astronomy_types import (
    Degrees,
    GeographicCoordinates,
    OrbitalElements,
    Scalar,
)

from collision_detection import build_collision_detection_figure
from control_room import launch_control_room
from eci_orbit_3d import visualisation_3d_satellite_earth
from ground_track import (
    visualisation_2d_ground_track,
    visualisation_2d_ground_track_current_position,
)
from hohmann_tradeoff import build_hohmann_tradeoff_figure
from hohmann_transfer_perifocal_2d import (
    build_default_hohmann_transfer_2d_perifocal_figure,
)
from itrf_orbit_3d import visualisation_3d_itrf
from keplers_ellipse_2d import build_default_keplers_ellipse_2d_figure
from moon_earth_3d import build_moon_earth_3d_figure
from newton_iteration import build_newton_iteration_figure
from orbit_source import (
    Orbit,
    OrbitSource,
    default_orbit_count,
    parse_orbit_source,
    resolve_orbits,
)
from phase_orbit_2d import build_default_phase_orbit_2d_perifocal_figure
from solar_system_3d import build_solar_system_3d_figure
from two_body_visualiser_2d import build_default_two_body_visualiser_2d_figure
from velocity_time import build_velocity_time_figure


def normalise_name(name: str) -> str:
    return "_".join(name.strip().lower().replace("-", " ").split())


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


ORBIT_VISUALISATIONS = {
    "ground_track",
    "current_ground_track",
    "itrf_orbit_3d",
    "satellite_earth_3d",
}


ALIASES = {
    "controlroom": "control_room",
    "itrf": "itrf_orbit_3d",
    "satellite_earth": "satellite_earth_3d",
    "ground_track_tle": "ground_track",
    "ground_track_custom": "ground_track",
    "ground_track_current": "current_ground_track",
    "kepler": "keplers_ellipse_2d",
    "solar_system": "solar_system_3d",
    "moon_earth": "moon_earth_3d",
    "two_body": "two_body_2d",
    "hohmann_transfer": "hohmann_transfer_2d",
    "phase_orbit": "phase_orbit_2d",
    "itrf_custom": "itrf_orbit_3d",
}


def orbital_figure_builder(
    name: str,
    orbits: list[Orbit],
    total_orbits: float,
    ground_station: GroundStation = KILCUMMIN_GROUND_STATION,
) -> go.Figure:
    if not orbits:
        raise ValueError("At least one orbit is required.")

    selected_orbit = orbits[0]

    if name == "ground_track":
        return visualisation_2d_ground_track(
            orbit=selected_orbit,
            orbit_count=total_orbits,
            show_orbit_markers=True,
        )

    if name == "current_ground_track":
        return visualisation_2d_ground_track_current_position(
            orbit=selected_orbit,
            ground_station=ground_station,
            orbit_count=total_orbits,
        )

    if name == "itrf_orbit_3d":
        return visualisation_3d_itrf(
            orbits,
            track_for_orbits=total_orbits,
        )

    if name == "satellite_earth_3d":
        return visualisation_3d_satellite_earth(orbits)

    raise ValueError(f"Unknown orbital visualisation: {name}")


def launch_visualisation(
    name: str,
    source: OrbitSource = OrbitSource.TLE,
    norad_ids: list[int] | None = None,
    horizons_targets: list[str] | None = None,
    elements: OrbitalElements | None = None,
    total_orbits: float | None = None,
    total_current_orbits: float | None = None,
) -> None:
    """Launch one named visualisation or the multi-plot control room."""
    resolved_name = ALIASES.get(normalise_name(name), normalise_name(name))

    if resolved_name in {*ORBIT_VISUALISATIONS, "control_room"}:
        if source is OrbitSource.TLE and not norad_ids:
            norad_ids = [ISS_NORAD_ID]

        orbits = resolve_orbits(
            source=source,
            norad_ids=norad_ids,
            horizons_targets=horizons_targets,
            elements=elements,
        )

        orbit_count = total_orbits or default_orbit_count(orbits[0])
        current_orbit_count = total_current_orbits or orbit_count

        if resolved_name == "control_room":
            launch_control_room(
                orbits=orbits,
                total_orbits=orbit_count,
                total_current_orbits=current_orbit_count,
            )
            return

        orbital_figure_builder(
            resolved_name,
            orbits,
            orbit_count,
        ).show()
        return

    try:
        figure_builder = STATIC_VISUALISATIONS[resolved_name]
    except KeyError as error:
        available = sorted(
            ["control_room", *ORBIT_VISUALISATIONS, *STATIC_VISUALISATIONS]
        )
        raise ValueError(
            f"Unknown visualisation '{name}'. "
            f"Available names: {', '.join(available)}"
        ) from error

    figure_builder().show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch an AFMaths Plotly visualisation by name."
    )

    parser.add_argument(
        "name",
        help='Visualisation name, for example "ground track".',
    )
    parser.add_argument(
        "--source",
        type=parse_orbit_source,
        default=OrbitSource.TLE,
        help="Orbital data source: tle, horizon, or elements.",
    )
    parser.add_argument(
        "--norad-id",
        dest="norad_ids",
        type=int,
        nargs="+",
        help="One or more NORAD IDs for --source tle.",
    )
    parser.add_argument(
        "--target",
        dest="horizons_targets",
        nargs="+",
        help=(
            "One or more Horizons targets for --source horizon, "
            "for example MOON or MARS."
        ),
    )
    parser.add_argument(
        "--orbits",
        "--tle-orbits",
        dest="orbits",
        type=float,
        default=None,
        help="Number of orbits to propagate.",
    )
    parser.add_argument(
        "--current-orbits",
        type=float,
        default=None,
        help=(
            "Number of current-position orbits in the control room. "
            "Defaults to --orbits."
        ),
    )
    parser.add_argument(
        "--inclination",
        type=float,
        help="Orbital inclination in degrees.",
    )
    parser.add_argument(
        "--right-ascension-of-ascending-node",
        type=float,
        help="Right ascension of the ascending node in degrees.",
    )
    parser.add_argument(
        "--argument-of-periapsis",
        type=float,
        help="Argument of periapsis in degrees.",
    )
    parser.add_argument(
        "--semi-major-axis",
        type=float,
        help="Semi-major axis.",
    )
    parser.add_argument(
        "--eccentricity",
        type=float,
        help="Orbital eccentricity (unitless).",
    )
    parser.add_argument(
        "--true-anomaly",
        type=float,
        help="True anomaly in degrees.",
    )

    return parser.parse_args()


def _value_or_default[T](value: T | None, default: T) -> T:
    return value if value is not None else default


def custom_elements_from_args(args: argparse.Namespace) -> OrbitalElements:
    elements_in_degrees = OrbitalElements(
        inclination=_value_or_default(
            args.inclination,
            EXAMPLE_ELEMENTS.inclination,
        ),
        right_ascension_of_ascending_node=_value_or_default(
            args.right_ascension_of_ascending_node,
            EXAMPLE_ELEMENTS.right_ascension_of_ascending_node,
        ),
        argument_of_periapsis=_value_or_default(
            args.argument_of_periapsis,
            EXAMPLE_ELEMENTS.argument_of_periapsis,
        ),
        semi_major_axis=_value_or_default(
            args.semi_major_axis,
            EXAMPLE_ELEMENTS.semi_major_axis,
        ),
        eccentricity=_value_or_default(
            args.eccentricity,
            EXAMPLE_ELEMENTS.eccentricity,
        ),
        true_anomaly=_value_or_default(
            args.true_anomaly,
            EXAMPLE_ELEMENTS.true_anomaly,
        ),
    )

    return orbital_elements_from_degrees(elements_in_degrees)


def main() -> None:
    args = parse_args()

    elements = (
        custom_elements_from_args(args) if args.source is OrbitSource.ELEMENTS else None
    )

    launch_visualisation(
        name=args.name,
        source=args.source,
        norad_ids=args.norad_ids,
        horizons_targets=args.horizons_targets,
        elements=elements,
        total_orbits=args.orbits,
        total_current_orbits=args.current_orbits,
    )


if __name__ == "__main__":
    main()
