import datetime
import math
from pathlib import Path

import plotly.graph_objects as go
from afmaths.constants import (
    BEIDOU_IGSO_6,
    GALILEO_7_NORAD_ID,
    ISS_NORAD_ID,
    MINUTES_PER_DAY,
    MOLNIYA_3_50_NORAD_ID,
)
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    julian_date_from_full_Date,
    julian_date_now,
    seconds_from_julian_date_delta,
    seconds_from_minutes,
)
from afmaths.physics.space.celestial_mechanics import (
    orbital_direction_from_inclination,
    state_vector_at_time,
)
from afmaths.physics.space.engineering.astrodynamics.ground_track import (
    geographic_coordinate_from_itrs,
    ground_track_positions,
    start_of_orbit_positions,
    westware_drift_from_angular_velocity_and_period,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
    parse_full_date,
    parse_norad_id,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.transformations import (
    itrs_position_from_gcrs_position,
    transform_geographic_coordinates_from_itrs,
)
from afmaths.physics.space.type_conversion_helpers import fulldate_from_python_datetime
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
)

BACKGROUND_IMAGE = Path(__file__).with_name("Earth-hires.jpg")


def visualisation_2d_ground_track(
    tle: str,
    track_for: int = MINUTES_PER_DAY,
    show_orbit_markers: bool = False,
) -> go.Figure:

    orbital_elements = orbital_elements_from_tle(tle)

    direction = orbital_direction_from_inclination(orbital_elements.inclination)

    epoch = Epoch(julian_date_from_full_Date(parse_full_date(tle)))

    positions = ground_track_positions(
        [
            state_vector_at_time(
                orbital_elements,
                seconds_from_minutes(Minute(int(minute))),
            ).position
            for minute in range(track_for)
        ],
        epoch,
    )

    geographic_coordinates = [
        geographic_coordinate_from_itrs(position) for position in positions
    ]

    period = orbital_period_from_tle(tle)
    orbit_marker_positions = start_of_orbit_positions(positions, period)

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
                "line": {
                    "color": "black",
                    "width": 1,
                },
            },
        )
    )

    current_position = geographic_coordinate_from_itrs(
        itrs_position_from_gcrs_position(
            julian_date_now(),
            state_vector_at_time(
                orbital_elements,
                seconds_from_julian_date_delta(
                    JulianDate(Scalar(julian_date_now() - epoch))
                ),
            ).position,
        )
    )

    fig = add_plot_nodes(
        fig,
        [
            PlotNode(
                name=f"Current Position",
                coordinate=Coordinate2D(
                    Scalar(current_position.longitude),
                    Scalar(current_position.latitude),
                ),
                text=f"Lon: {current_position.longitude:.1f}, Lat: {current_position.latitude:.1f}",
                size=20,
                symbol="diamond",
                colour="orange",
            )
        ],
    )

    fig.update_layout(
        title=(
            f"Satellite {parse_norad_id(tle)} ground track"
            f"<br>Drift: {westware_drift_from_angular_velocity_and_period(period)} deg | Duration: {track_for} min | Direction: {direction}"
        ),
        xaxis_title="Longitude",
        yaxis_title="Latitude",
    )

    plot_nodes = []

    if show_orbit_markers:
        orbit_marker_coordinates = [
            geographic_coordinate_from_itrs(position)
            for position in orbit_marker_positions
        ]

        plot_nodes.extend(
            PlotNode(
                name=f"orbit {orbit_number} start",
                coordinate=Coordinate2D(
                    Scalar(coordinate.longitude),
                    Scalar(coordinate.latitude),
                ),
                text=f"Orbit {orbit_number}",
                size=10,
                symbol="circle",
            )
            for orbit_number, coordinate in enumerate(
                orbit_marker_coordinates,
                start=1,
            )
        )

    return add_plot_nodes(
        with_data_background_image(
            fig,
            image_source=BACKGROUND_IMAGE,
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
