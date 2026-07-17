from pathlib import Path

import plotly.graph_objects as go
from afmaths.constants import (
    EARTH_MU,
)
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    greenwich_full_Date_from_julian_date,
    julian_date_delta,
    julian_date_now,
    pretty_print_full_date,
    seconds_from_julian_date_delta,
)
from afmaths.physics.space.celestial_mechanics import (
    apoapsis_true_anomaly,
    current_orbital_elapsed_period_from_epoch,
    elapsed_time_to_true_anomaly,
    orbital_direction_from_inclination,
    orbital_elements_from_state_vectors,
    orbital_radius_from_position_vector,
    periapsis_true_anomaly,
    state_vector_at_time,
    vis_viva,
)
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    earth_geographic_coordinate_from_itrs,
    earth_start_of_orbit_coordinates,
    general_orbital_characteristics,
    westward_drift_from_angular_velocity_and_period,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
    parse_julian_date,
    parse_norad_id,
)
from afmaths.physics.space.transformations import (
    itrs_position_from_gcrs_position,
)
from afmaths.types import OrbitalDirection
from afmaths.visualisations.helpers import (
    PlotNode,
    add_plot_nodes,
    with_data_background_image,
)
from astronomy_types import (
    Coordinate2D,
    Epoch,
    Scalar,
    Second,
)


def visualisation_2d_ground_track(
    tle: str,
    track_for_orbits: int = 3,
    tracking_interval: Second = Second(Scalar(60)),
    show_orbit_markers: bool = False,
    background_image_path: Path = Path(__file__).with_name("Earth-hires.jpg"),
    lines: bool = False,
) -> go.Figure:
    if track_for_orbits < 1:
        track_for_orbits = 1

    if tracking_interval < 1:
        tracking_interval = Second(Scalar(60))

    track_for_duration = orbital_period_from_tle(tle) * track_for_orbits

    tle_epoch_elements = orbital_elements_from_tle(tle)

    tle_epoch = Epoch(parse_julian_date(tle))

    elapsed_times = [
        Second(Scalar(second))
        for second in range(
            0,
            int(track_for_duration),
            int(float(tracking_interval)),
        )
    ]

    geographic_coordinates = [
        earth_geographic_coordinate_from_itrs(
            itrs_position_from_gcrs_position(
                epoch_offset(tle_epoch, elapsed_time),
                gcrs_position,
            )
        )
        for elapsed_time, gcrs_position in zip(
            elapsed_times,
            [
                state_vector_at_time(
                    tle_epoch_elements,
                    elapsed_time,
                ).position
                for elapsed_time in elapsed_times
            ],
        )
    ]

    orbital_period = orbital_period_from_tle(tle)

    epoch_to_now_seconds = seconds_from_julian_date_delta(julian_date_delta(tle_epoch))

    current_state = state_vector_at_time(
        tle_epoch_elements,
        epoch_to_now_seconds,
    )
    current_elements = orbital_elements_from_state_vectors(current_state)

    current_epoch = epoch_offset(
        tle_epoch,
        epoch_to_now_seconds,
    )

    time_to_perigee = elapsed_time_to_true_anomaly(
        current_elements,
        periapsis_true_anomaly(),
    )

    time_to_apogee = elapsed_time_to_true_anomaly(
        current_elements,
        apoapsis_true_anomaly(),
    )

    perigee = earth_geographic_coordinate_from_itrs(
        itrs_position_from_gcrs_position(
            epoch_offset(current_epoch, time_to_perigee),
            state_vector_at_time(
                current_elements,
                time_to_perigee,
            ).position,
        )
    )

    apogee = earth_geographic_coordinate_from_itrs(
        itrs_position_from_gcrs_position(
            epoch_offset(current_epoch, time_to_apogee),
            state_vector_at_time(
                current_elements,
                time_to_apogee,
            ).position,
        )
    )

    current_radius = orbital_radius_from_position_vector(current_state.position)

    current_position = earth_geographic_coordinate_from_itrs(
        itrs_position_from_gcrs_position(
            current_epoch,
            current_state.position,
        )
    )

    fig = add_plot_nodes(
        add_plot_nodes(
            add_plot_nodes(
                go.Figure().add_trace(
                    go.Scatter(
                        x=[
                            (float(coordinate.longitude))
                            for coordinate in geographic_coordinates
                        ],
                        y=[
                            float(coordinate.latitude)
                            for coordinate in geographic_coordinates
                        ],
                        mode="markers+lines" if lines else "markers",
                        name="Satellite ground track",
                        marker={
                            "color": list(range(len(geographic_coordinates))),
                            "colorscale": "greys",
                            "reversescale": True,
                            "showscale": False,
                            "colorbar": {
                                "title": "Iteration",
                            },
                        },
                    )
                ),
                [
                    PlotNode(
                        name=f"Apogee",
                        coordinate=Coordinate2D(
                            Scalar(apogee.longitude),
                            Scalar(apogee.latitude),
                        ),
                        text=f"Apogee",
                        size=20,
                        symbol="circle",
                        colour="Orange",
                        marker_only=True,
                    )
                ],
            ),
            [
                PlotNode(
                    name=f"Perigee",
                    coordinate=Coordinate2D(
                        Scalar(perigee.longitude),
                        Scalar(perigee.latitude),
                    ),
                    text=f"Perigee",
                    size=20,
                    symbol="circle",
                    colour="Orange",
                    marker_only=True,
                )
            ],
        ),
        [
            PlotNode(
                name=f"Position: {pretty_print_full_date(greenwich_full_Date_from_julian_date(julian_date_now()),  show_timesystem=True)}",
                coordinate=Coordinate2D(
                    Scalar(current_position.longitude),
                    Scalar(current_position.latitude),
                ),
                text=f"Lon: {current_position.longitude:.1f}, Lat: {current_position.latitude:.1f} t={current_orbital_elapsed_period_from_epoch(epoch_to_now_seconds, orbital_period):.0f}s v={vis_viva(EARTH_MU,current_radius,tle_epoch_elements.semi_major_axis,):.2f}m/s r={current_radius:.2f}m",
                size=20,
                symbol="diamond",
                colour="Red",
                marker_only=True,
            )
        ],
    ).update_layout(
        title=(
            f"Satellite {parse_norad_id(tle)} ground track | Duration: {track_for_duration:.0f}s"
            f"<br>{general_orbital_characteristics(tle)}"
        ),
        xaxis_title="Longitude [deg]",
        yaxis_title="Latitude [deg]",
    )

    plot_nodes = []

    if show_orbit_markers:

        orbit_marker_coordinates = earth_start_of_orbit_coordinates(
            tle_epoch_elements, tle_epoch, track_for_orbits
        )

        orbit_epoch = [
            greenwich_full_Date_from_julian_date(
                epoch_offset(tle_epoch, Second(Scalar(orbital_period * min)))
            )
            for min in range(len(orbit_marker_coordinates))
        ]

        plot_nodes.extend(
            PlotNode(
                name=f"orbit {orbit_number}: {pretty_print_full_date(orbit_epoch, show_timesystem=True)}",
                coordinate=Coordinate2D(
                    Scalar(coordinate.longitude),
                    Scalar(coordinate.latitude),
                ),
                text=f"Orbit {orbit_number} @ {pretty_print_full_date(orbit_epoch, show_timesystem=True)}",
                size=10,
                symbol="circle",
                marker_only=True,
            )
            for (orbit_number, coordinate), orbit_epoch in zip(
                enumerate(
                    orbit_marker_coordinates,
                    start=1,
                ),
                orbit_epoch,
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
