import plotly.graph_objects as go

from astronomy_types import Scalar, Second

from afmaths.geometry.geometry import euclidian_distance_3d
from afmaths.physics.space.celestial_mechanics.state_vector import (
    state_vector_at_time,
)
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    orbital_period_from_tle,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.perturbation_models.sgp4 import (
    sgp4_satrec,
    state_vector_from_satrec_at_time,
)
from afmaths.physics.space.type_conversion_helpers import (
    coordinate3d_from_vector,
)


def calculate_orbital_error(predicted_position, actual_position):
    return euclidian_distance_3d(predicted_position, actual_position)


def sample_orbit_comparison(
    norad_id: int,
    duration_seconds: int | None = None,
    time_step_seconds: int = 60,
):
    tle = get_tle_from_norad_id(norad_id)
    orbital_elements = orbital_elements_from_tle(tle)
    satrec = sgp4_satrec(tle)

    if duration_seconds is None:
        duration_seconds = int(orbital_period_from_tle(tle))

    offsets = list(range(0, duration_seconds + 1, time_step_seconds))

    local_positions = []
    sgp4_positions = []
    errors = []

    for offset in offsets:
        time_offset = Second(Scalar(offset))

        local_state = state_vector_at_time(orbital_elements, time_offset)
        sgp4_state = state_vector_from_satrec_at_time(satrec, time_offset)

        local_position = coordinate3d_from_vector(local_state.position)
        sgp4_position = coordinate3d_from_vector(sgp4_state.position)

        local_positions.append(local_position)
        sgp4_positions.append(sgp4_position)
        errors.append(calculate_orbital_error(local_position, sgp4_position))

    return offsets, local_positions, sgp4_positions, errors


def build_orbit_comparison_figure(
    norad_id: int,
    duration_seconds: int | None = None,
    time_step_seconds: int = 60,
    highlight_index: int = 0,
):
    offsets, local_positions, sgp4_positions, _ = sample_orbit_comparison(
        norad_id=norad_id,
        duration_seconds=duration_seconds,
        time_step_seconds=time_step_seconds,
    )

    if highlight_index >= len(offsets):
        raise ValueError("highlight_index is out of range")

    local_x = [position.x for position in local_positions]
    local_y = [position.y for position in local_positions]
    local_z = [position.z for position in local_positions]

    sgp4_x = [position.x for position in sgp4_positions]
    sgp4_y = [position.y for position in sgp4_positions]
    sgp4_z = [position.z for position in sgp4_positions]

    local_highlight = local_positions[highlight_index]
    sgp4_highlight = sgp4_positions[highlight_index]
    highlight_minutes = offsets[highlight_index] / 60.0

    fig = go.Figure()

    fig.add_trace(
        go.Scatter3d(
            x=local_x,
            y=local_y,
            z=local_z,
            mode="lines",
            name="Local two-body implementation",
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=sgp4_x,
            y=sgp4_y,
            z=sgp4_z,
            mode="lines",
            name="SGP4 implementation",
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[local_highlight.x],
            y=[local_highlight.y],
            z=[local_highlight.z],
            mode="markers",
            name=f"Local position at t={highlight_minutes:.1f} min",
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[sgp4_highlight.x],
            y=[sgp4_highlight.y],
            z=[sgp4_highlight.z],
            mode="markers",
            name=f"SGP4 position at t={highlight_minutes:.1f} min",
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=[local_highlight.x, sgp4_highlight.x],
            y=[local_highlight.y, sgp4_highlight.y],
            z=[local_highlight.z, sgp4_highlight.z],
            mode="lines",
            name="Error vector",
        )
    )

    fig.update_layout(
        title=f"Orbit comparison for NORAD ID {norad_id}",
        scene=dict(
            xaxis_title="x (m)",
            yaxis_title="y (m)",
            zaxis_title="z (m)",
            aspectmode="data",
        ),
    )

    return fig


def build_error_over_time_figure(
    norad_id: int,
    duration_seconds: int | None = None,
    time_step_seconds: int = 60,
):
    offsets, _, _, errors = sample_orbit_comparison(
        norad_id=norad_id,
        duration_seconds=duration_seconds,
        time_step_seconds=time_step_seconds,
    )

    time_minutes = [offset / 60.0 for offset in offsets]
    error_km = [error / 1000.0 for error in errors]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=time_minutes,
            y=error_km,
            mode="lines",
            name="Position error",
        )
    )

    fig.update_layout(
        title=f"Position error over time for NORAD ID {norad_id}",
        xaxis_title="Time since epoch (minutes)",
        yaxis_title="Position error (km)",
    )

    return fig


if __name__ == "__main__":
    norad_id = 25544

    orbit_figure = build_orbit_comparison_figure(
        norad_id=norad_id,
        time_step_seconds=60,
        highlight_index=0,
    )
    orbit_figure.show()

    error_figure = build_error_over_time_figure(
        norad_id=norad_id,
        time_step_seconds=60,
    )
    error_figure.show()
