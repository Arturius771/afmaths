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
    julian_date_from_full_Date,
    seconds_from_minutes,
)
from afmaths.physics.space.celestial_mechanics import (
    state_vector_at_time,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    parse_full_date,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.transformations import (
    itrs_positions_from_gcrs_position,
    transform_geographic_coordinates_from_itrs,
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
)

BACKGROUND_IMAGE = Path(__file__).with_name("Earth-hires.jpg")


def visualisation_2d_ground_track(
    norad_target_id: int, track_for: int = MINUTES_PER_DAY
) -> go.Figure:
    tle = get_tle_from_norad_id(norad_target_id)

    orbital_elements = orbital_elements_from_tle(tle)

    positions = itrs_positions_from_gcrs_position(
        [
            state_vector_at_time(
                orbital_elements,
                seconds_from_minutes(Minute(int(minute))),
            ).position
            for minute in range(track_for)
        ],
        Epoch(
            JulianDate(Scalar(float(julian_date_from_full_Date(parse_full_date(tle)))))
        ),
    )

    geographic_coordinates = [
        transform_geographic_coordinates_from_itrs(position) for position in positions
    ]

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

    fig.update_layout(
        title=f"Satellite {norad_target_id} ground track",
        xaxis_title="Longitude",
        yaxis_title="Latitude",
    )

    start = geographic_coordinates[0]

    return add_plot_nodes(
        with_data_background_image(
            fig,
            image_source=BACKGROUND_IMAGE,
            x_min=-180,
            x_max=180,
            y_min=-90,
            y_max=90,
            opacity=0.6,
            set_axis_ranges=True,
            lock_aspect_ratio=False,
        ),
        [
            PlotNode(
                name="track start",
                coordinate=Coordinate2D(
                    Scalar(start.longitude),
                    Scalar(start.latitude),
                ),
                text="Start",
                size=12,
                symbol="x",
            )
        ],
    )


if __name__ == "__main__":
    # build_ground_track_figure(
    #     synthetic_iss_like_itrs_positions(
    #         samples=100,
    #         orbits=3.3,
    #     )
    # ).show()
    visualisation_2d_ground_track(BEIDOU_IGSO_6)
