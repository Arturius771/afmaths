from __future__ import annotations

from pathlib import Path

import plotly.graph_objects as go

from afmaths.afmath_types import GroundStation
from afmaths.constants import EARTH_MU
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    greenwich_full_Date_from_julian_date,
    pretty_print_full_date,
)
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    orbital_radius_from_position_vector,
    vis_viva,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    apoapsis_true_anomaly,
    periapsis_true_anomaly,
    state_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import (
    orbital_period,
    time_to_true_anomaly,
)
from afmaths.physics.space.celestial_mechanics.utils import second_intervals_for_orbits
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    earth_geographic_coordinate_from_itrf,
    earth_start_of_orbit_coordinates,
    general_orbital_characteristics,
)
from afmaths.physics.space.transformations import itrf_position_from_gcrs_position
from afmaths.visualisations.helpers import (
    PlotNode,
    add_plot_nodes,
    figure_circle,
    with_data_background_image,
)
from astronomy_types import (
    Coordinate2D,
    GeographicCoordinates,
    OrbitalElements,
    Scalar,
    Second,
)

from orbit_source import (
    Orbit,
    orbit_at_current_epoch,
    orbit_from_elements,
    orbit_from_tle,
)

EARTH_IMAGE_PATH = Path(__file__).with_name("Earth-hires.jpg")


def _orbital_characteristics_title(orbit: Orbit) -> str:
    if orbit.tle is None:
        return ""

    return f"<br>{general_orbital_characteristics(orbit.tle)}"


def _geographic_coordinates(
    orbit: Orbit,
    orbit_count: float,
    number_of_points: int,
    time_interval: Second | None = None,
) -> list[GeographicCoordinates]:
    period = orbital_period(orbit.elements.semi_major_axis)
    duration = Second(Scalar(period * orbit_count))

    elapsed_times = second_intervals_for_orbits(
        Second(Scalar(0)),
        duration,
        number_of_points,
        time_interval,
    )

    return [
        earth_geographic_coordinate_from_itrf(
            itrf_position_from_gcrs_position(
                epoch_offset(orbit.epoch, elapsed_time),
                state_vector_at_time(
                    orbit.elements,
                    elapsed_time,
                    EARTH_MU,
                ).position,
            )
        )
        for elapsed_time in elapsed_times
    ]


def visualisation_2d_ground_track(
    orbit: Orbit,
    orbit_count: float = 3,
    show_orbit_markers: bool = False,
    background_image_path: Path = EARTH_IMAGE_PATH,
    time_interval: Second | None = None,
    lines: bool = False,
    number_of_points: int = 2000,
) -> go.Figure:
    coordinates = _geographic_coordinates(
        orbit,
        orbit_count,
        number_of_points,
        time_interval,
    )

    fig = (
        go.Figure()
        .add_trace(
            go.Scatter(
                x=[float(coordinate.longitude) for coordinate in coordinates],
                y=[float(coordinate.latitude) for coordinate in coordinates],
                mode="markers+lines" if lines else "markers",
                name=f"{orbit.name} ground track",
                marker={
                    "color": list(range(len(coordinates))),
                    "colorscale": "greys",
                    "reversescale": True,
                    "showscale": False,
                },
            )
        )
        .update_layout(
            title=(
                f"{orbit.name} ground track | "
                f"Source: {orbit.source.value} | Orbits: {orbit_count}"
                f"{_orbital_characteristics_title(orbit)}"
            ),
            xaxis_title="Longitude [deg]",
            yaxis_title="Latitude [deg]",
        )
    )

    plot_nodes: list[PlotNode] = []

    if show_orbit_markers:
        period = orbital_period(orbit.elements.semi_major_axis)
        marker_coordinates = earth_start_of_orbit_coordinates(
            orbit.elements,
            orbit.epoch,
            int(orbit_count),
        )

        marker_epochs = [
            greenwich_full_Date_from_julian_date(
                epoch_offset(
                    orbit.epoch,
                    Second(Scalar(period * orbit_number)),
                )
            )
            for orbit_number in range(len(marker_coordinates))
        ]

        plot_nodes.extend(
            PlotNode(
                name=(
                    f"orbit {orbit_number}: "
                    f"{pretty_print_full_date(marker_epoch, show_timesystem=True)}"
                ),
                coordinate=Coordinate2D(
                    Scalar(coordinate.longitude),
                    Scalar(coordinate.latitude),
                ),
                text=(
                    f"Orbit {orbit_number} @ "
                    f"{pretty_print_full_date(marker_epoch, show_timesystem=True)}"
                ),
                size=10,
                symbol="circle",
                marker_only=True,
            )
            for (orbit_number, coordinate), marker_epoch in zip(
                enumerate(marker_coordinates, start=1),
                marker_epochs,
            )
        )

    return add_plot_nodes(
        with_data_background_image(
            fig,
            image_source=background_image_path,
            x_min=-180,
            x_max=180,
            y_min=-90,
            y_max=90,
            opacity=0.5,
            set_axis_ranges=True,
            lock_aspect_ratio=False,
        ),
        plot_nodes,
    )


def visualisation_2d_ground_track_current_position(
    orbit: Orbit,
    ground_station: GroundStation,
    background_image_path: Path = EARTH_IMAGE_PATH,
    lines: bool = False,
    number_of_points: int = 2000,
    orbit_count: float = 1,
) -> go.Figure:
    current_orbit = orbit_at_current_epoch(orbit)

    period = orbital_period(current_orbit.elements.semi_major_axis)
    coordinates = _geographic_coordinates(
        current_orbit,
        orbit_count,
        number_of_points,
    )

    current_state = state_vector_at_time(
        current_orbit.elements,
        Second(Scalar(0)),
        EARTH_MU,
    )

    time_to_perigee = time_to_true_anomaly(
        current_orbit.elements,
        periapsis_true_anomaly(),
    )
    time_to_apogee = time_to_true_anomaly(
        current_orbit.elements,
        apoapsis_true_anomaly(),
    )

    perigee = earth_geographic_coordinate_from_itrf(
        itrf_position_from_gcrs_position(
            epoch_offset(current_orbit.epoch, time_to_perigee),
            state_vector_at_time(
                current_orbit.elements,
                time_to_perigee,
                EARTH_MU,
            ).position,
        )
    )

    apogee = earth_geographic_coordinate_from_itrf(
        itrf_position_from_gcrs_position(
            epoch_offset(current_orbit.epoch, time_to_apogee),
            state_vector_at_time(
                current_orbit.elements,
                time_to_apogee,
                EARTH_MU,
            ).position,
        )
    )

    current_radius = orbital_radius_from_position_vector(current_state.position)

    current_position = earth_geographic_coordinate_from_itrf(
        itrf_position_from_gcrs_position(
            current_orbit.epoch,
            current_state.position,
        )
    )

    ground_station_coordinate = Coordinate2D(
        Scalar(ground_station.coordinates.longitude),
        Scalar(ground_station.coordinates.latitude),
    )

    return with_data_background_image(
        figure_circle(
            add_plot_nodes(
                go.Figure()
                .add_trace(
                    go.Scatter(
                        x=[float(coordinate.longitude) for coordinate in coordinates],
                        y=[float(coordinate.latitude) for coordinate in coordinates],
                        mode="markers+lines" if lines else "markers",
                        name=f"{current_orbit.name} ground track",
                        marker={"color": "black"},
                    )
                )
                .update_layout(
                    title=(
                        f"{current_orbit.name} current ground track | "
                        f"Source: {current_orbit.source.value} | "
                        f"Orbits: {orbit_count}"
                        f"{_orbital_characteristics_title(current_orbit)}"
                    ),
                    xaxis_title="Longitude [deg]",
                    yaxis_title="Latitude [deg]",
                ),
                [
                    PlotNode(
                        name=f"Ground Station: {ground_station.name or 'Unnamed'}",
                        coordinate=ground_station_coordinate,
                        text=f"Ground Station: {ground_station.name or 'Unnamed'}",
                        size=5,
                        symbol="circle",
                        colour="Blue",
                        marker_only=True,
                    ),
                    PlotNode(
                        name="Apogee",
                        coordinate=Coordinate2D(
                            Scalar(apogee.longitude),
                            Scalar(apogee.latitude),
                        ),
                        text="Apogee",
                        size=20,
                        symbol="circle",
                        colour="Orange",
                        marker_only=True,
                    ),
                    PlotNode(
                        name="Perigee",
                        coordinate=Coordinate2D(
                            Scalar(perigee.longitude),
                            Scalar(perigee.latitude),
                        ),
                        text="Perigee",
                        size=20,
                        symbol="circle",
                        colour="Orange",
                        marker_only=True,
                    ),
                    PlotNode(
                        name=("Position: " f"{pretty_print_full_date(
                                greenwich_full_Date_from_julian_date(
                                    current_orbit.epoch
                                ),
                                show_timesystem=True,
                            )}"),
                        coordinate=Coordinate2D(
                            Scalar(current_position.longitude),
                            Scalar(current_position.latitude),
                        ),
                        text=(
                            f"Lon: {current_position.longitude:.1f}, "
                            f"Lat: {current_position.latitude:.1f} "
                            f"t=0s "
                            f"v={vis_viva(
                                EARTH_MU,
                                current_radius,
                                current_orbit.elements.semi_major_axis,
                            ):.2f}m/s "
                            f"r={current_radius:.2f}m "
                            f"T={period:.2f}s"
                        ),
                        size=20,
                        symbol="diamond",
                        colour="Red",
                        marker_only=True,
                    ),
                ],
            ),
            ground_station_coordinate,
            ground_station.range,
            fill_colour=None,
        ),
        image_source=background_image_path,
        x_min=-180,
        x_max=180,
        y_min=-90,
        y_max=90,
        opacity=0.5,
        set_axis_ranges=True,
        lock_aspect_ratio=False,
    )


def visualisation_2d_ground_track_tle_propagation(
    tle: str,
    orbit_count: float = 3,
    show_orbit_markers: bool = False,
    background_image_path: Path = EARTH_IMAGE_PATH,
    time_interval: Second | None = None,
    lines: bool = False,
    number_of_points: int = 2000,
) -> go.Figure:
    return visualisation_2d_ground_track(
        orbit_from_tle(tle),
        orbit_count=orbit_count,
        show_orbit_markers=show_orbit_markers,
        background_image_path=background_image_path,
        time_interval=time_interval,
        lines=lines,
        number_of_points=number_of_points,
    )


def visualisation_2d_ground_track_current_position_propogation(
    tle: str,
    ground_station: GroundStation,
    background_image_path: Path = EARTH_IMAGE_PATH,
    lines: bool = False,
    number_of_points: int = 2000,
    orbit_count: float = 1,
) -> go.Figure:
    return visualisation_2d_ground_track_current_position(
        orbit_from_tle(tle),
        ground_station=ground_station,
        background_image_path=background_image_path,
        lines=lines,
        number_of_points=number_of_points,
        orbit_count=orbit_count,
    )


def visualisation_2d_ground_track_orbital_elements_propogation(
    elements: OrbitalElements,
    ground_station: GroundStation,
    background_image_path: Path = EARTH_IMAGE_PATH,
    lines: bool = False,
    number_of_points: int = 2000,
    orbit_count: float = 1,
) -> go.Figure:
    return visualisation_2d_ground_track_current_position(
        orbit_from_elements(elements),
        ground_station=ground_station,
        background_image_path=background_image_path,
        lines=lines,
        number_of_points=number_of_points,
        orbit_count=orbit_count,
    )
