from __future__ import annotations

import argparse
import datetime
from dataclasses import replace
from pathlib import Path

import plotly.graph_objects as go
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Distance,
    Epoch,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)

from afmaths.constants import EARTH_MU
from afmaths.physics.space.astronomy.time_functions import julian_date_now
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import EARTH_MU
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    orbital_elements_from_state_vectors,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.ground_track import orbits_per_day
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    parse_julian_date,
    parse_norad_id,
)
from afmaths.physics.space.external.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)
from afmaths.physics.space.external.space_track_api import (
    get_tle_from_norad_id,
    refresh_tle_cache,
)
from afmaths.physics.space.type_conversion_helpers import fulldate_from_python_datetime
from afmaths.visualisations.visualisation_types import (
    Orbit,
    OrbitSource,
    PlotOptions,
    PlotOrbital2DSettings,
    PlotOriginConfig,
)


def parse_orbit_source(value: str) -> OrbitSource:
    normalised = value.strip().lower().replace("-", "_")

    aliases = {
        "tle": OrbitSource.TLE,
        "horizon": OrbitSource.HORIZONS,
        "horizons": OrbitSource.HORIZONS,
        "element": OrbitSource.ELEMENTS,
        "elements": OrbitSource.ELEMENTS,
        "custom": OrbitSource.ELEMENTS,
        "orbital_elements": OrbitSource.ELEMENTS,
    }

    try:
        return aliases[normalised]
    except KeyError as error:
        available = "tle, horizon, elements"
        raise argparse.ArgumentTypeError(
            f"Unknown orbit source '{value}'. Expected one of: {available}."
        ) from error


def orbit_from_tle(tle: str) -> Orbit:
    return Orbit(
        name=f"{parse_norad_id(tle)}",
        epoch=Epoch(parse_julian_date(tle)),
        description=tle,
    )


def orbit_from_elements(
    elements: OrbitalElements,
    name: str = "Custom orbit",
    epoch: Epoch | None = None,
) -> Orbit:
    return Orbit(
        name=name,
        epoch=epoch or Epoch(julian_date_now()),
        description=elements,
    )


def orbit_from_horizons(
    target: HorizonsCommandTarget,
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> Orbit:
    start_time = datetime.datetime.now()
    stop_time = start_time + datetime.timedelta(minutes=1)

    state_vectors = get_object_state_vectors_from_horizon(
        target=target,
        centre=centre,
        start_time=fulldate_from_python_datetime(start_time),
        stop_time=fulldate_from_python_datetime(stop_time),
    )

    if not state_vectors:
        raise ValueError(f"No Horizons state vectors returned for {target.name}.")

    return Orbit(
        name=target.name.title().replace("_", " "),
        epoch=Epoch(julian_date_now()),
        description=orbital_elements_from_state_vectors(
            state_vectors[0],
            mu=gravitational_parameter,
        ),
    )


def parse_horizons_target(value: str) -> HorizonsCommandTarget:
    normalised = value.strip().lower().replace("-", "_").replace(" ", "_")

    for target in HorizonsCommandTarget:
        if target.name.lower() == normalised:
            return target

        if str(target.value).lower() == normalised:
            return target

    available = ", ".join(target.name.lower() for target in HorizonsCommandTarget)
    raise ValueError(
        f"Unknown Horizons target '{value}'. Available targets: {available}"
    )


def resolve_orbits(
    source: OrbitSource,
    norad_ids: list[int] | None = None,
    horizons_targets: list[str] | None = None,
    elements: OrbitalElements | None = None,
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> list[Orbit]:
    match source:
        case OrbitSource.TLE:
            if not norad_ids:
                raise ValueError("--norad-id is required for --source tle.")

            refresh_tle_cache()

            return [
                orbit_from_tle(get_tle_from_norad_id(norad_id))
                for norad_id in norad_ids
            ]

        case OrbitSource.HORIZONS:
            if not horizons_targets:
                raise ValueError("--target is required for --source horizon.")

            return [
                orbit_from_horizons(
                    parse_horizons_target(target),
                    centre=centre,
                    gravitational_parameter=gravitational_parameter,
                )
                for target in horizons_targets
            ]

        case OrbitSource.ELEMENTS:
            if elements is None:
                raise ValueError("Orbital elements are required for --source elements.")

            return [orbit_from_elements(elements)]

    raise ValueError(f"Unsupported orbit source: {source}")


def orbit_elements(orbit: Orbit) -> OrbitalElements:
    if isinstance(orbit.description, OrbitalElements):
        return orbit.description

    return orbital_elements_from_tle(orbit.description)


def default_orbit_count(orbit: Orbit) -> int:
    return max(
        1,
        min(
            round(
                orbits_per_day(
                    orbital_period(orbit_elements(orbit).semi_major_axis),
                )
            ),
            100,
        ),
    )


def with_plot_settings_overrides(
    settings: PlotOrbital2DSettings,
    *,
    distance_scale: float | None = None,
    plot_width: int | None = None,
    plot_height: int | None = None,
    plot_min_x: float | None = None,
    plot_min_y: float | None = None,
    plot_max_x: float | None = None,
    plot_max_y: float | None = None,
    slider_steps: int | None = None,
    orbit_points: int | None = None,
) -> PlotOrbital2DSettings:
    """Apply only explicitly supplied command-line plot overrides."""
    overrides = {
        name: value
        for name, value in {
            "distance_scale": distance_scale,
            "plot_width": plot_width,
            "plot_height": plot_height,
            "plot_min_x": plot_min_x,
            "plot_min_y": plot_min_y,
            "plot_max_x": plot_max_x,
            "plot_max_y": plot_max_y,
            "slider_steps": slider_steps,
            "orbit_points": orbit_points,
        }.items()
        if value is not None
    }
    return replace(settings, **overrides)


def defined_kwargs(**kwargs):
    """Return only explicitly supplied keyword arguments."""
    return {name: value for name, value in kwargs.items() if value is not None}


from collections.abc import Callable

from astronomy_types import (
    Eccentricity,
    Inclination,
    Ratio,
    RightAscension,
)

from afmaths.afmath_types import Mass
from afmaths.constants import (
    EXAMPLE_ELEMENTS,
    ISS_NORAD_ID,
    KILCUMMIN_GROUND_STATION,
)
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.collision_detection import build_collision_detection_figure
from afmaths.visualisations.ground_track import (
    GROUND_TRACK_POINTS,
    visualisation_2d_ground_track,
    visualisation_2d_ground_track_current_position,
)
from afmaths.visualisations.hohmann_tradeoff import build_hohmann_tradeoff_figure
from afmaths.visualisations.hohmann_transfer_perifocal_2d import (
    DEFAULT_PLOT_SETTINGS as HOHMANN_PLOT_SETTINGS,
)
from afmaths.visualisations.hohmann_transfer_perifocal_2d import (
    build_default_hohmann_transfer_2d_perifocal_figure,
)
from afmaths.visualisations.kerbin_plots import build_kerbin_orbit_plots
from afmaths.visualisations.lagrange_points_2d import build_lagrange_points_figure
from afmaths.visualisations.newton_iteration import build_newton_iteration_figure
from afmaths.visualisations.orbit_system_3d import (
    DEFAULT_SOLAR_SYSTEM_BODIES,
    build_3d_orbit_system_figure,
)
from afmaths.visualisations.orbit_visualiser_2d import (
    DEFAULT_PLOT_SETTINGS as ORBIT_2D_PLOT_SETTINGS,
)
from afmaths.visualisations.orbit_visualiser_2d import (
    build_default_orbit_visualiser_2d_figure,
    satellite_orbiting_body,
)
from afmaths.visualisations.phase_orbit_2d import (
    DEFAULT_PLOT_SETTINGS as PHASE_PLOT_SETTINGS,
)
from afmaths.visualisations.phase_orbit_2d import (
    build_default_phase_orbit_2d_perifocal_figure,
)
from afmaths.visualisations.velocity_time import build_velocity_time_figure


def normalise_name(name: str) -> str:
    return "_".join(name.strip().lower().replace("-", " ").split())


def parse_horizons_target(
    value: str | HorizonsCommandTarget,
) -> HorizonsCommandTarget:
    """Resolve a CLI target name without re-parsing an enum default."""
    if isinstance(value, HorizonsCommandTarget):
        return value
    try:
        return HorizonsCommandTarget[value.upper()]
    except KeyError as error:
        raise argparse.ArgumentTypeError(f"Unknown Horizons target: {value}") from error


STATIC_VISUALISATIONS: dict[str, Callable[[], go.Figure]] = {
    "collision_detection": build_collision_detection_figure,
    "hohmann_tradeoff": build_hohmann_tradeoff_figure,
    "newton_iteration": build_newton_iteration_figure,
    "velocity_time": build_velocity_time_figure,
}
ORBIT_VISUALISATIONS = {
    "ground_track",
    "current_ground_track",
}
CONFIGURABLE_VISUALISATIONS = {
    "hohmann_transfer_2d",
    "lagrange_points",
    "orbit_3d",
    "orbit_2d",
    "phase_orbit_2d",
}
ALIASES = {
    "kerbin": "kerbin_control_room",
    "kerbin_control_room": "kerbin_control_room",
    "kerbin_3d": "orbit_3d",
    "controlroom": "control_room",
    "itrf": "orbit_3d",
    "satellite_earth": "orbit_3d",
    "ground_track_tle": "ground_track",
    "ground_track_custom": "ground_track",
    "ground_track_current": "current_ground_track",
    # Merged Kepler/two-body visualisation.
    "kepler": "orbit_2d",
    "keplers_ellipse_2d": "orbit_2d",
    "two_body": "orbit_2d",
    "two_body_2d": "orbit_2d",
    "orbit": "orbit_2d",
    "solar_system": "orbit_3d",
    "solar_system_3d": "orbit_3d",
    "moon_earth": "orbit_3d",
    "moon_earth_3d": "orbit_3d",
    "satellite_earth_3d": "orbit_3d",
    "itrf_orbit_3d": "orbit_3d",
    "hohmann_transfer": "hohmann_transfer_2d",
    "phase_orbit": "phase_orbit_2d",
    "itrf_custom": "orbit_3d",
    "lagrange": "lagrange_points",
    "lagrange_points_2d": "lagrange_points",
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
    raise ValueError(f"Unknown orbital visualisation: {name}")


def configurable_figure_builder(
    name: str,
    options: PlotOptions,
    *,
    orbits: list[Orbit] | None = None,
    total_orbits: float | None = None,
    mass_1: Mass | None = None,
    mass_2: Mass | None = None,
    distance: Distance | None = None,
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
                elements=orbit_elements(orbit),
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
    if name == "lagrange_points":
        if mass_1 is None or mass_2 is None or distance is None:
            raise ValueError(
                "lagrange_points requires --mass-1, --mass-2, and --distance."
            )
        return build_lagrange_points_figure(
            mass_1=mass_1,
            mass_2=mass_2,
            distance=distance,
            plot_width=options.plot_width,
            plot_height=options.plot_height,
        )
    if name == "phase_orbit_2d":
        return build_default_phase_orbit_2d_perifocal_figure(
            settings=_plot_2d_settings(
                PHASE_PLOT_SETTINGS,
                options,
            )
        )
    if name == "orbit_3d":
        default_bodies = (
            []
            if options.reference_frame == "ITRF"
            else (
                DEFAULT_SOLAR_SYSTEM_BODIES
                if options.central_body is HorizonsCommandTarget.SUN
                else (
                    []
                    if isinstance(options.central_body, PlotOriginConfig)
                    else [HorizonsCommandTarget.MOON]
                )
            )
        )
        return build_3d_orbit_system_figure(
            origin_body=options.central_body,
            horizons_bodies=(
                options.horizons_bodies
                if options.horizons_bodies is not None
                else (default_bodies if options.include_default_system_bodies else [])
            ),
            satellite_orbits=orbits or [],
            reference_frame=options.reference_frame,
            track_for_orbits=(total_orbits if total_orbits is not None else 3.0),
            **defined_kwargs(
                distance_scale=options.distance_scale,
                orbit_points=options.plot_points,
            ),
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
    mass_1: Mass | None = None,
    mass_2: Mass | None = None,
    distance: Distance | None = None,
) -> None:
    """Launch one named visualisation or the multi-plot control room."""
    requested_name = normalise_name(name)
    resolved_name = ALIASES.get(requested_name, requested_name)
    options = plot_options or PlotOptions()
    # Preserve the old specialised commands while routing all three through the
    # generic builder. The canonical orbit_3d command remains composable: it
    # combines its default system bodies with explicitly supplied satellites.
    if requested_name in {"solar_system", "solar_system_3d"}:
        options = replace(
            options,
            central_body=HorizonsCommandTarget.SUN,
            horizons_bodies=(options.horizons_bodies or DEFAULT_SOLAR_SYSTEM_BODIES),
        )
    elif requested_name in {"moon_earth", "moon_earth_3d"}:
        options = replace(
            options,
            central_body=HorizonsCommandTarget.EARTH,
            horizons_bodies=(options.horizons_bodies or [HorizonsCommandTarget.MOON]),
        )
    elif requested_name in {"kerbin", "kerbin_3d", "kerbin_control_room"}:
        if source is not OrbitSource.ELEMENTS:
            raise ValueError(
                "Kerbin requires --source elements; TLE and Horizons data are Earth/Solar-System sources."
            )
        if elements is None:
            raise ValueError("Kerbin requires supplied orbital elements.")
        if options.reference_frame != "ICRF":
            raise ValueError(
                "Kerbin supports only the inertial ICRF-aligned plot, not Earth-fixed ITRF/GCRF."
            )
        options = replace(
            options,
            central_body=PlotOriginConfig(
                name="Kerbin",
                target=None,
                radius=Distance(Scalar(600_000)),
                gravitational_parameter=GravitationalParameter(Scalar(3.5316e12)),
                radius_scale=1.0,
                distance_scale=100_000.0,
                texture_path=Path(__file__).resolve().parent / "kerbin.jpg",
            ),
            horizons_bodies=[],
            include_default_system_bodies=False,
        )
    elif requested_name in {
        "satellite_earth",
        "satellite_earth_3d",
        "itrf",
        "itrf_orbit_3d",
        "itrf_custom",
    }:
        options = replace(
            options,
            central_body=HorizonsCommandTarget.EARTH,
            horizons_bodies=[],
            reference_frame=("ITRF" if requested_name.startswith("itrf") else "ICRF"),
        )
    requires_default_satellite = requested_name in {
        "kerbin",
        "kerbin_3d",
        "kerbin_control_room",
        "satellite_earth",
        "satellite_earth_3d",
        "itrf",
        "itrf_orbit_3d",
        "itrf_custom",
    }
    if (
        resolved_name
        in {
            *ORBIT_VISUALISATIONS,
            "control_room",
        }
        or requires_default_satellite
    ):
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
        if resolved_name == "kerbin_control_room":
            if not isinstance(options.central_body, PlotOriginConfig):
                raise ValueError("Kerbin control room requires a custom Kerbin origin.")
            plots = [
                configurable_figure_builder(
                    "orbit_3d", options, orbits=orbits, total_orbits=orbit_count
                ),
                *build_kerbin_orbit_plots(
                    orbit_elements(orbits[0]),
                    orbit_count=orbit_count,
                    current_orbit_count=current_orbit_count,
                    points=options.plot_points or 1000,
                    show_lines=options.lines if options.lines is not None else True,
                ),
            ]
            show_visualisation_dashboard(
                plots,
                title=f"Kerbin Control Room — {orbits[0].name}",
                columns=options.dashboard_columns,
                output_path=options.output_path,
            )
            return
        if resolved_name == "control_room":
            if options.reference_frame == "ITRF":
                raise ValueError(
                    "The control room already includes an ITRF panel. "
                    "Choose ICRF or GCRF for its inertial panel."
                )
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
                central_body=options.central_body,
                horizons_bodies=options.horizons_bodies,
                include_default_system_bodies=options.include_default_system_bodies,
                inertial_reference_frame=options.reference_frame,
            )
            return
        if requires_default_satellite:
            configurable_figure_builder(
                "orbit_3d",
                options,
                orbits=orbits,
                total_orbits=orbit_count,
            ).show()
        else:
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
            if resolved_name in {"orbit_2d", "orbit_3d"}
            else []
        )
        configurable_figure_builder(
            resolved_name,
            options,
            orbits=resolved_orbits,
            total_orbits=total_orbits,
            mass_1=mass_1,
            mass_2=mass_2,
            distance=distance,
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
    lagrange_group = parser.add_argument_group("Lagrange point system")
    lagrange_group.add_argument(
        "--mass-1",
        type=float,
        help="Mass of the primary body in kilograms.",
    )
    lagrange_group.add_argument(
        "--mass-2",
        type=float,
        help="Mass of the secondary body in kilograms.",
    )
    lagrange_group.add_argument(
        "--distance",
        type=float,
        help="Distance between the two bodies in metres.",
    )
    parser.add_argument(
        "--reference-frame",
        choices=["ICRF", "GCRF", "ITRF"],
        default="ICRF",
        help="3D orbit reference frame.",
    )
    parser.add_argument(
        "--centre",
        type=parse_horizons_target,
        default=HorizonsCommandTarget.EARTH,
        choices=[HorizonsCommandTarget.EARTH, HorizonsCommandTarget.SUN],
        help="Central body for orbit_3d: EARTH or SUN.",
    )
    parser.add_argument(
        "--body",
        dest="horizons_bodies",
        type=parse_horizons_target,
        nargs="+",
        help=(
            "Horizons bodies to display in orbit_3d, for example MOON or "
            "MERCURY VENUS EARTH MARS. Omit to use the centre's default set."
        ),
    )
    parser.add_argument(
        "--system-bodies",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Include the default Moon or planet set when --body is omitted. "
            "Use --no-system-bodies for a satellite-only plot."
        ),
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
        reference_frame=args.reference_frame,
        central_body=args.centre,
        horizons_bodies=args.horizons_bodies,
        include_default_system_bodies=args.system_bodies,
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
        mass_1=(Mass(Scalar(args.mass_1)) if args.mass_1 is not None else None),
        mass_2=(Mass(Scalar(args.mass_2)) if args.mass_2 is not None else None),
        distance=(
            Distance(Scalar(args.distance)) if args.distance is not None else None
        ),
    )


import tempfile
import webbrowser
from collections.abc import Sequence
from html import escape
from typing import Literal

import plotly.io as pio

from afmaths.afmath_types import GroundStation
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.visualisations.state_vectors import (
    build_position_vector_figure,
    build_velocity_vector_figure,
)


def write_visualisation_dashboard(
    figures: Sequence[go.Figure],
    title: str = "AFMaths Visualisations",
    columns: int = 1,
    output_path: Path | None = None,
) -> Path:
    """Write independent Plotly figures into one responsive HTML dashboard."""
    if not figures:
        raise ValueError("At least one figure is required.")
    if columns < 1:
        raise ValueError("columns must be at least 1.")

    if output_path is None:
        with tempfile.NamedTemporaryFile(
            prefix="afmaths-visualisations-",
            suffix=".html",
            delete=False,
        ) as temporary_file:
            output_path = Path(temporary_file.name)
    else:
        output_path = output_path.expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)

    panels: list[str] = []

    for index, figure in enumerate(figures):
        dashboard_figure = go.Figure(figure)

        dashboard_figure.update_layout(
            width=None,
            height=None,
            autosize=True,
        )

        panels.append(
            '<section class="plot-panel">'
            + pio.to_html(
                dashboard_figure,
                full_html=False,
                include_plotlyjs=index == 0,
                config={
                    "responsive": True,
                    "displaylogo": False,
                },
                default_width="100%",
                default_height="100%",
            )
            + "</section>"
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; }}
    body {{
      padding: 16px;
      background: #eef1f5;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    h1 {{ margin: 0 0 16px; font-size: 24px; }}
    .dashboard {{
      display: grid;
      grid-template-columns: repeat({columns}, minmax(0, 1fr));
      gap: 16px;
    }}
    .plot-panel {{
      min-width: 0;
      height: min(800px, 85vh);
      overflow: hidden;
      background: white;
      border: 1px solid #d8dde5;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    .plot-panel > div,
    .plot-panel .plotly-graph-div {{
      width: 100% !important;
      height: 100% !important;
    }}
    @media (max-width: 1100px) {{
      .dashboard {{ grid-template-columns: 1fr; }}
      .plot-panel {{ height: 600px; }}
    }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <main class="dashboard">{''.join(panels)}</main>
  <script>
    const resizePlots = () => document
      .querySelectorAll('.plotly-graph-div')
      .forEach(plot => Plotly.Plots.resize(plot));
    window.addEventListener('load', resizePlots);
    window.addEventListener('resize', resizePlots);
  </script>
</body>
</html>
"""

    output_path.write_text(document, encoding="utf-8")
    return output_path


def show_visualisation_dashboard(
    figures: Sequence[go.Figure],
    title: str = "AFMaths Visualisations",
    columns: int = 1,
    output_path: Path | None = None,
) -> Path:
    """Write a dashboard and open it in the default browser."""
    dashboard_path = write_visualisation_dashboard(
        figures=figures,
        title=title,
        columns=columns,
        output_path=output_path,
    )
    webbrowser.open(dashboard_path.resolve().as_uri())
    return dashboard_path


def build_control_room_figures(
    orbits: list[Orbit],
    total_orbits: float,
    total_current_orbits: float,
    ground_station: GroundStation = KILCUMMIN_GROUND_STATION,
    *,
    distance_scale: float | None = None,
    plot_points: int | None = None,
    lines: bool = False,
    show_orbit_markers: bool = True,
    central_body: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    horizons_bodies: list[HorizonsCommandTarget] | None = None,
    include_default_system_bodies: bool = True,
    inertial_reference_frame: Literal["ICRF", "GCRF"] = "GCRF",
) -> list:
    """Build the independent figures used by the control-room dashboard."""
    if not orbits:
        raise ValueError("At least one orbit is required.")

    selected_orbit = orbits[0]
    selected_elements = orbit_elements(selected_orbit)
    ground_track_points = (
        plot_points if plot_points is not None else GROUND_TRACK_POINTS
    )
    orbit_2d_settings = with_plot_settings_overrides(
        ORBIT_2D_PLOT_SETTINGS, distance_scale=distance_scale, orbit_points=plot_points
    )
    satellites = [
        satellite_orbiting_body(name=orbit.name, elements=orbit_elements(orbit))
        for orbit in orbits
    ]
    orbit_plot_kwargs = defined_kwargs(
        distance_scale=distance_scale, orbit_points=plot_points
    )
    inertial_bodies = horizons_bodies
    if inertial_bodies is None and include_default_system_bodies:
        inertial_bodies = (
            DEFAULT_SOLAR_SYSTEM_BODIES
            if central_body is HorizonsCommandTarget.SUN
            else []
        )
    inertial_satellites = orbits if central_body is HorizonsCommandTarget.EARTH else []

    return [
        # Control room figures start here
        # 2D ground track of the selected orbit's current position
        visualisation_2d_ground_track_current_position(
            orbit=selected_orbit,
            ground_station=ground_station,
            orbit_count=total_current_orbits,
            number_of_points=ground_track_points,
            lines=lines,
        ),
        # 3D orbit system figure centered on the central body
        build_3d_orbit_system_figure(
            origin_body=central_body,
            horizons_bodies=inertial_bodies,
            satellite_orbits=inertial_satellites,
            reference_frame=inertial_reference_frame,
            **orbit_plot_kwargs,
        ),
        # 3D orbit system figure in the Earth-centered ITRF frame
        build_3d_orbit_system_figure(
            satellite_orbits=orbits,
            reference_frame="ITRF",
            track_for_orbits=total_orbits,
            **orbit_plot_kwargs,
        ),
        # 2D ground track of the selected orbit's full orbit
        visualisation_2d_ground_track(
            orbit=selected_orbit,
            orbit_count=total_orbits,
            show_orbit_markers=show_orbit_markers,
            number_of_points=ground_track_points,
            lines=lines,
        ),
        # Default 2D orbit visualiser figure
        build_default_orbit_visualiser_2d_figure(
            satellites=satellites,
            settings=orbit_2d_settings,
            propagation_orbits=total_orbits,
        ),
        # Position vector figure for the selected orbit
        build_position_vector_figure(selected_elements, int(total_orbits)),
        # Velocity vector figure for the selected orbit
        build_velocity_vector_figure(selected_elements, int(total_orbits)),
    ]


def launch_control_room(
    orbits: list[Orbit],
    total_orbits: float,
    total_current_orbits: float,
    output_path: Path | None = None,
    *,
    columns: int = 1,
    distance_scale: float | None = None,
    plot_points: int | None = None,
    lines: bool = False,
    show_orbit_markers: bool = True,
    central_body: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    horizons_bodies: list[HorizonsCommandTarget] | None = None,
    include_default_system_bodies: bool = True,
    inertial_reference_frame: Literal["ICRF", "GCRF"] = "GCRF",
) -> Path:
    """Open the control-room figures in one browser dashboard."""
    figures = build_control_room_figures(
        orbits=orbits,
        total_orbits=total_orbits,
        total_current_orbits=total_current_orbits,
        distance_scale=distance_scale,
        plot_points=plot_points,
        lines=lines,
        show_orbit_markers=show_orbit_markers,
        central_body=central_body,
        horizons_bodies=horizons_bodies,
        include_default_system_bodies=include_default_system_bodies,
        inertial_reference_frame=inertial_reference_frame,
    )
    return show_visualisation_dashboard(
        figures,
        title=f"AFMaths Control Room - {orbits[0].name}",
        columns=columns,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
