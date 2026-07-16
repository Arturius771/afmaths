from pathlib import Path

import plotly.graph_objects as go
from afmaths.constants import (
    EARTH_MU,
)
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    greenwich_full_Date_from_julian_date,
    julian_date_delta,
    julian_date_from_full_Date,
    julian_date_now,
    minutes_from_seconds,
    pretty_print_full_date,
    seconds_from_julian_date_delta,
    seconds_from_minutes,
)
from afmaths.physics.space.celestial_mechanics import (
    current_orbital_elapsed_period,
    eccentric_anomaly_from_true_anomaly,
    kepler_equation,
    mean_anomaly_at_time,
    mean_motion,
    orbit_equation,
    orbital_direction_from_inclination,
    state_vector_at_time,
    true_anomaly,
    vis_viva,
)
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    earth_geographic_coordinate_from_itrs,
    earth_ground_track_positions,
    earth_start_of_orbit_positions,
    orbits_per_day,
    westward_drift_from_angular_velocity_and_period,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
    parse_epoch,
    parse_full_date,
    parse_julian_date,
    parse_mean_anomaly,
    parse_norad_id,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.transformations import (
    itrs_position_from_gcrs_position,
    transform_geographic_coordinates_from_itrs,
)
from afmaths.physics.space.type_conversion_helpers import (
    fulldate_from_python_datetime,
    make_true_anomaly,
)
from afmaths.visualisations.helpers import (
    PlotNode,
    add_plot_nodes,
    with_data_background_image,
)
from astronomy_types import (
    Coordinate2D,
    Epoch,
    JulianDate,
    Minute,
    PositionVector,
    Scalar,
    Second,
)


def visualisation_2d_ground_track(
    tle: str,
    track_for_orbits: int = 3,
    show_orbit_markers: bool = False,
    background_image_path: Path = Path(__file__).with_name("Earth-hires.jpg"),
) -> go.Figure:
    if track_for_orbits < 1:
        track_for_orbits = 1

    track_for = minutes_from_seconds(orbital_period_from_tle(tle)) * track_for_orbits

    epoch_elements = orbital_elements_from_tle(tle)

    direction = orbital_direction_from_inclination(epoch_elements.inclination)

    epoch = Epoch(parse_julian_date(tle))

    positions = earth_ground_track_positions(
        [
            state_vector_at_time(
                epoch_elements,
                seconds_from_minutes(Minute(int(minute))),
            ).position
            for minute in range(track_for)
        ],
        epoch,
    )

    geographic_coordinates = [
        earth_geographic_coordinate_from_itrs(position) for position in positions
    ]

    period = orbital_period_from_tle(tle)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[float(coordinate.longitude) for coordinate in geographic_coordinates],
            y=[float(coordinate.latitude) for coordinate in geographic_coordinates],
            mode="markers",
            name="Satellite ground track",
            marker={
                "color": list(range(len(geographic_coordinates))),
                "colorscale": "blues",
                "showscale": False,
                "reversescale": True,
                "colorbar": {
                    "title": "Iteration",
                },
                # "line": {
                #     "color": "black",
                #     "width": 1,
                # },
            },
        )
    )

    elapsed_seconds = seconds_from_julian_date_delta(julian_date_delta(epoch))

    state = state_vector_at_time(
        epoch_elements,
        elapsed_seconds,
    )

    current_radius = orbit_equation(
        epoch_elements.semi_major_axis,
        epoch_elements.eccentricity,
        true_anomaly(
            epoch_elements.eccentricity,
            mean_anomaly_at_time(
                kepler_equation(
                    eccentric_anomaly_from_true_anomaly(
                        make_true_anomaly(0), epoch_elements.eccentricity
                    ),
                    epoch_elements.eccentricity,
                ),
                elapsed_seconds,
                mean_motion(
                    epoch_elements.semi_major_axis,
                ),
            ),
        ),
    )

    current_velocity = vis_viva(
        EARTH_MU,
        current_radius,
        epoch_elements.semi_major_axis,
    )

    current_position = earth_geographic_coordinate_from_itrs(
        itrs_position_from_gcrs_position(
            julian_date_now(),
            state.position,
        )
    )

    current_orbital_period = current_orbital_elapsed_period(elapsed_seconds, period)

    fig = add_plot_nodes(
        fig,
        [
            PlotNode(
                name=f"Position @ {pretty_print_full_date(greenwich_full_Date_from_julian_date(julian_date_now()),  show_timesystem=True)}",
                coordinate=Coordinate2D(
                    Scalar(current_position.longitude),
                    Scalar(current_position.latitude),
                ),
                text=f"Lon: {current_position.longitude:.1f}, Lat: {current_position.latitude:.1f} t={current_orbital_period:.0f}s v={current_velocity:.2f}m/s r={current_radius:.2f}m",
                size=20,
                symbol="diamond",
                colour="orange",
                marker_only=True,
            )
        ],
    )

    fig.update_layout(
        title=(
            f"Satellite {parse_norad_id(tle)} ground track"
            f"<br>Drift: { westward_drift_from_angular_velocity_and_period(period):.2f}° | "
            f"Duration: {track_for} min | Direction: {direction} | "
            f"Epoch (JD): {parse_julian_date(tle)} | Period: {period:.0f}s"
        ),
        xaxis_title="Longitude [deg]",
        yaxis_title="Latitude [deg]",
    )

    plot_nodes = []

    if show_orbit_markers:
        orbit_marker_positions = earth_start_of_orbit_positions(positions, period)
        orbit_marker_coordinates = [
            earth_geographic_coordinate_from_itrs(position)
            for position in orbit_marker_positions
        ]

        orbit_epoch = [
            greenwich_full_Date_from_julian_date(
                epoch_offset(epoch, Second(Scalar(period * min)))
            )
            for min in range(len(orbit_marker_positions))
        ]

        plot_nodes.extend(
            PlotNode(
                name=f"orbit {orbit_number} start",
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
