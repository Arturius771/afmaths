from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

import plotly.graph_objects as go

from afmaths.constants import (
    EXAMPLE_ELEMENTS,
    ISS_NORAD_ID,
    KILCUMMIN_GROUND_STATION,
)
from afmaths.visualisations.helpers import (
    PlotOrbital2DSettings,
    defined_kwargs,
    with_plot_settings_overrides,
)
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)

from collision_detection import build_collision_detection_figure
from control_room import launch_control_room
from eci_orbit_3d import visualisation_3d_satellite_earth
from ground_track import (
    GROUND_TRACK_POINTS,
    visualisation_2d_ground_track,
    visualisation_2d_ground_track_current_position,
)
from hohmann_tradeoff import build_hohmann_tradeoff_figure
from hohmann_transfer_perifocal_2d import (
    DEFAULT_PLOT_SETTINGS as HOHMANN_PLOT_SETTINGS,
    build_default_hohmann_transfer_2d_perifocal_figure,
)
from itrf_orbit_3d import visualisation_3d_itrf
from moon_earth_3d import build_moon_earth_3d_figure
from newton_iteration import build_newton_iteration_figure
from orbit_source import (
    Orbit,
    OrbitSource,
    default_orbit_count,
    parse_orbit_source,
    resolve_orbits,
)
from orbit_visualiser_2d import (
    DEFAULT_PLOT_SETTINGS as ORBIT_2D_PLOT_SETTINGS,
    build_default_orbit_visualiser_2d_figure,
    satellite_orbiting_body,
)
from phase_orbit_2d import (
    DEFAULT_PLOT_SETTINGS as PHASE_PLOT_SETTINGS,
    build_default_phase_orbit_2d_perifocal_figure,
)
from solar_system_3d import build_solar_system_3d_figure
from velocity_time import build_velocity_time_figure


@dataclass(frozen=True)
class PlotOptions:
    distance_scale: float | None = None
    plot_width: int | None = None
    plot_height: int | None = None
    plot_min_x: float | None = None
    plot_min_y: float | None = None
    plot_max_x: float | None = None
    plot_max_y: float | None = None
    slider_steps: int | None = None
    plot_points: int | None = None
    lines: bool | None = None
    show_orbit_markers: bool | None = None
    dashboard_columns: int = 1
    output_path: Path | None = None

    def __post_init__(self) -> None:
        if self.distance_scale is not None and self.distance_scale <= 0:
            raise ValueError("distance_scale must be greater than 0.")

        if self.plot_width is not None and self.plot_width <= 0:
            raise ValueError("plot_width must be greater than 0.")

        if self.plot_height is not None and self.plot_height <= 0:
            raise ValueError("plot_height must be greater than 0.")

        if self.slider_steps is not None and self.slider_steps < 2:
            raise ValueError("slider_steps must be at least 2.")

        if self.plot_points is not None and self.plot_points < 2:
            raise ValueError("plot_points must be at least 2.")

        if self.dashboard_columns < 1:
            raise ValueError("dashboard_columns must be at least 1.")


def normalise_name(name: str) -> str:
    return "_".join(name.strip().lower().replace("-", " ").split())


STATIC_VISUALISATIONS: dict[str, Callable[[], go.Figure]] = {
    "collision_detection": build_collision_detection_figure,
    "hohmann_tradeoff": build_hohmann_tradeoff_figure,
    "newton_iteration": build_newton_iteration_figure,
    "velocity_time": build_velocity_time_figure,
}


ORBIT_VISUALISATIONS = {
    "ground_track",
    "current_ground_track",
    "itrf_orbit_3d",
    "satellite_earth_3d",
}


CONFIGURABLE_VISUALISATIONS = {
    "hohmann_transfer_2d",
    "moon_earth_3d",
    "orbit_2d",
    "phase_orbit_2d",
    "solar_system_3d",
}


ALIASES = {
    "controlroom": "control_room",
    "itrf": "itrf_orbit_3d",
    "satellite_earth": "satellite_earth_3d",
    "ground_track_tle": "ground_track",
    "ground_track_custom": "ground_track",
    "ground_track_current": "current_ground_track",
    # Merged Kepler/two-body visualisation.
    "kepler": "orbit_2d",
    "keplers_ellipse_2d": "orbit_2d",
    "two_body": "orbit_2d",
    "two_body_2d": "orbit_2d",
    "orbit": "orbit_2d",
    "solar_system": "solar_system_3d",
    "moon_earth": "moon_earth_3d",
    "hohmann_transfer": "hohmann_transfer_2d",
    "phase_orbit": "phase_orbit_2d",
    "itrf_custom": "itrf_orbit_3d",
}


def _plot_2d_settings(
    defaults: PlotOrbital2DSettings,
    options: PlotOptions,
) -> PlotOrbital2DSettings:
    return with_plot_settings_overrides(
        defaults,
        distance_scale=options.distance_scale,
        plot_width=options.plot_width,
        plot_height=options.plot_height,
        plot_min_x=options.plot_min_x,
        plot_min_y=options.plot_min_y,
        plot_max_x=options.plot_max_x,
        plot_max_y=options.plot_max_y,
        slider_steps=options.slider_steps,
        orbit_points=options.plot_points,
    )


def resolve_optional_orbits(
    source: OrbitSource,
    norad_ids: list[int] | None,
    horizons_targets: list[str] | None,
    elements: OrbitalElements | None,
) -> list[Orbit]:
    """
    Resolve explicitly supplied orbit data.

    Unlike the main orbital visualisations, an orbit_2d invocation with no
    supplied orbit data should remain the default Earth-Moon system rather
    than implicitly adding the ISS.
    """
    has_explicit_orbit = (
        elements is not None or bool(norad_ids) or bool(horizons_targets)
    )

    if not has_explicit_orbit:
        return []

    return resolve_orbits(
        source=source,
        norad_ids=norad_ids,
        horizons_targets=horizons_targets,
        elements=elements,
    )


def orbital_figure_builder(
    name: str,
    orbits: list[Orbit],
    total_orbits: float,
    options: PlotOptions,
) -> go.Figure:
    if not orbits:
        raise ValueError("At least one orbit is required.")

    selected_orbit = orbits[0]

    ground_track_points = (
        options.plot_points if options.plot_points is not None else GROUND_TRACK_POINTS
    )

    lines = options.lines if options.lines is not None else False

    if name == "ground_track":
        return visualisation_2d_ground_track(
            orbit=selected_orbit,
            orbit_count=total_orbits,
            show_orbit_markers=(
                options.show_orbit_markers
                if options.show_orbit_markers is not None
                else True
            ),
            number_of_points=ground_track_points,
            lines=lines,
        )

    if name == "current_ground_track":
        return visualisation_2d_ground_track_current_position(
            orbit=selected_orbit,
            ground_station=KILCUMMIN_GROUND_STATION,
            orbit_count=total_orbits,
            number_of_points=ground_track_points,
            lines=lines,
        )

    if name == "itrf_orbit_3d":
        return visualisation_3d_itrf(
            orbits,
            track_for_orbits=total_orbits,
            **defined_kwargs(
                distance_scale=options.distance_scale,
                orbit_points=options.plot_points,
            ),
        )

    if name == "satellite_earth_3d":
        return visualisation_3d_satellite_earth(
            orbits,
            **defined_kwargs(
                distance_scale=options.distance_scale,
                orbit_points=options.plot_points,
            ),
        )

    raise ValueError(f"Unknown orbital visualisation: {name}")


def configurable_figure_builder(
    name: str,
    options: PlotOptions,
    *,
    orbits: list[Orbit] | None = None,
    total_orbits: float | None = None,
) -> go.Figure:
    if name == "hohmann_transfer_2d":
        return build_default_hohmann_transfer_2d_perifocal_figure(
            settings=_plot_2d_settings(
                HOHMANN_PLOT_SETTINGS,
                options,
            )
        )

    if name == "orbit_2d":
        satellites = [
            satellite_orbiting_body(
                name=orbit.name,
                elements=orbit.elements,
            )
            for orbit in (orbits or [])
        ]

        return build_default_orbit_visualiser_2d_figure(
            satellites=satellites,
            settings=_plot_2d_settings(
                ORBIT_2D_PLOT_SETTINGS,
                options,
            ),
            propagation_orbits=(total_orbits if total_orbits is not None else 1.0),
        )

    if name == "phase_orbit_2d":
        return build_default_phase_orbit_2d_perifocal_figure(
            settings=_plot_2d_settings(
                PHASE_PLOT_SETTINGS,
                options,
            )
        )

    if name == "moon_earth_3d":
        return build_moon_earth_3d_figure(
            **defined_kwargs(
                distance_scale=options.distance_scale,
                orbit_points=options.plot_points,
            )
        )

    if name == "solar_system_3d":
        return build_solar_system_3d_figure(
            **defined_kwargs(
                distance_scale=options.distance_scale,
                orbit_points=options.plot_points,
            )
        )

    raise ValueError(f"Unknown configurable visualisation: {name}")


def launch_visualisation(
    name: str,
    source: OrbitSource = OrbitSource.TLE,
    norad_ids: list[int] | None = None,
    horizons_targets: list[str] | None = None,
    elements: OrbitalElements | None = None,
    total_orbits: float | None = None,
    total_current_orbits: float | None = None,
    plot_options: PlotOptions | None = None,
) -> None:
    """Launch one named visualisation or the multi-plot control room."""
    resolved_name = ALIASES.get(
        normalise_name(name),
        normalise_name(name),
    )

    options = plot_options or PlotOptions()

    if resolved_name in {
        *ORBIT_VISUALISATIONS,
        "control_room",
    }:
        if source is OrbitSource.TLE and not norad_ids:
            norad_ids = [ISS_NORAD_ID]

        orbits = resolve_orbits(
            source=source,
            norad_ids=norad_ids,
            horizons_targets=horizons_targets,
            elements=elements,
        )

        if not orbits:
            raise ValueError("At least one orbit is required.")

        orbit_count = (
            total_orbits if total_orbits is not None else default_orbit_count(orbits[0])
        )

        current_orbit_count = (
            total_current_orbits if total_current_orbits is not None else orbit_count
        )

        if orbit_count <= 0 or current_orbit_count <= 0:
            raise ValueError("Orbit counts must be greater than 0.")

        if resolved_name == "control_room":
            launch_control_room(
                orbits=orbits,
                total_orbits=orbit_count,
                total_current_orbits=current_orbit_count,
                output_path=options.output_path,
                columns=options.dashboard_columns,
                distance_scale=options.distance_scale,
                plot_points=options.plot_points,
                lines=(options.lines if options.lines is not None else False),
                show_orbit_markers=(
                    options.show_orbit_markers
                    if options.show_orbit_markers is not None
                    else True
                ),
            )
            return

        orbital_figure_builder(
            resolved_name,
            orbits,
            orbit_count,
            options,
        ).show()

        return

    if resolved_name in CONFIGURABLE_VISUALISATIONS:
        resolved_orbits = (
            resolve_optional_orbits(
                source=source,
                norad_ids=norad_ids,
                horizons_targets=horizons_targets,
                elements=elements,
            )
            if resolved_name == "orbit_2d"
            else []
        )

        configurable_figure_builder(
            resolved_name,
            options,
            orbits=resolved_orbits,
            total_orbits=total_orbits,
        ).show()

        return

    try:
        figure_builder = STATIC_VISUALISATIONS[resolved_name]
    except KeyError as error:
        available = sorted(
            [
                "control_room",
                *ORBIT_VISUALISATIONS,
                *CONFIGURABLE_VISUALISATIONS,
                *STATIC_VISUALISATIONS,
            ]
        )

        raise ValueError(
            f"Unknown visualisation '{name}'. "
            f"Available names: {', '.join(available)}"
        ) from error

    figure_builder().show()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=("Launch an AFMaths Plotly visualisation by name.")
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
        help="Number of reference-body orbits to propagate.",
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
        help="Orbital inclination in radians.",
    )

    parser.add_argument(
        "--right-ascension-of-ascending-node",
        type=float,
        help=("Right ascension of the ascending node in radians."),
    )

    parser.add_argument(
        "--argument-of-periapsis",
        type=float,
        help="Argument of periapsis in radians.",
    )

    parser.add_argument(
        "--semi-major-axis",
        type=float,
        help="Semi-major axis in metres.",
    )

    parser.add_argument(
        "--eccentricity",
        type=float,
        help="Orbital eccentricity (unitless).",
    )

    parser.add_argument(
        "--true-anomaly",
        type=float,
        help="True anomaly in radians.",
    )

    plot_group = parser.add_argument_group("plot settings")

    plot_group.add_argument(
        "--distance-scale",
        type=float,
        help=("Physical distance represented by one plot unit " "where supported."),
    )

    plot_group.add_argument(
        "--plot-width",
        type=int,
        help="2D plot width in pixels.",
    )

    plot_group.add_argument(
        "--plot-height",
        type=int,
        help="2D plot height in pixels.",
    )

    plot_group.add_argument(
        "--plot-min-x",
        type=float,
        help="2D plot minimum X value.",
    )

    plot_group.add_argument(
        "--plot-min-y",
        type=float,
        help="2D plot minimum Y value.",
    )

    plot_group.add_argument(
        "--plot-max-x",
        type=float,
        help="2D plot maximum X value.",
    )

    plot_group.add_argument(
        "--plot-max-y",
        type=float,
        help="2D plot maximum Y value.",
    )

    plot_group.add_argument(
        "--slider-steps",
        type=int,
        help=("Number of slider steps for interactive 2D plots."),
    )

    plot_group.add_argument(
        "--plot-points",
        type=int,
        help=("Sampling resolution for orbit/ground-track plots."),
    )

    plot_group.add_argument(
        "--lines",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Draw lines between ground-track samples.",
    )

    plot_group.add_argument(
        "--show-orbit-markers",
        action=argparse.BooleanOptionalAction,
        default=None,
        help=("Show per-orbit markers on the ground-track plot."),
    )

    plot_group.add_argument(
        "--dashboard-columns",
        type=int,
        default=1,
        help=("Number of columns in the control-room dashboard."),
    )

    plot_group.add_argument(
        "--output-path",
        type=Path,
        help=("Optional control-room dashboard HTML output path."),
    )

    return parser.parse_args()


def custom_elements_from_args(
    args: argparse.Namespace,
) -> OrbitalElements:
    return replace(
        EXAMPLE_ELEMENTS,
        **defined_kwargs(
            inclination=(
                Inclination(Radians(Scalar(args.inclination)))
                if args.inclination is not None
                else None
            ),
            right_ascension_of_ascending_node=(
                RightAscension(Radians(Scalar(args.right_ascension_of_ascending_node)))
                if (args.right_ascension_of_ascending_node is not None)
                else None
            ),
            argument_of_periapsis=(
                ArgumentOfPeriapsis(Radians(Scalar(args.argument_of_periapsis)))
                if args.argument_of_periapsis is not None
                else None
            ),
            semi_major_axis=(
                SemiMajorAxis(Distance(Scalar(args.semi_major_axis)))
                if args.semi_major_axis is not None
                else None
            ),
            eccentricity=(
                Eccentricity(Ratio(Scalar(args.eccentricity)))
                if args.eccentricity is not None
                else None
            ),
            true_anomaly=(
                TrueAnomaly(Anomaly(Radians(Scalar(args.true_anomaly))))
                if args.true_anomaly is not None
                else None
            ),
        ),
    )


def plot_options_from_args(
    args: argparse.Namespace,
) -> PlotOptions:
    return PlotOptions(
        distance_scale=args.distance_scale,
        plot_width=args.plot_width,
        plot_height=args.plot_height,
        plot_min_x=args.plot_min_x,
        plot_min_y=args.plot_min_y,
        plot_max_x=args.plot_max_x,
        plot_max_y=args.plot_max_y,
        slider_steps=args.slider_steps,
        plot_points=args.plot_points,
        lines=args.lines,
        show_orbit_markers=args.show_orbit_markers,
        dashboard_columns=args.dashboard_columns,
        output_path=args.output_path,
    )


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
        plot_options=plot_options_from_args(args),
    )


if __name__ == "__main__":
    main()
