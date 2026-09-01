import plotly.graph_objects as go

from afmaths.constants import EARTH_MU
from astronomy_types import OrbitalElements

from afmaths.physics.space.celestial_mechanics.state_vector import (
    position_vectors_for_period,
    velocity_vectors_for_period,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period


def build_position_vector_figure(
    orbital_elements: OrbitalElements,
    number_of_orbits: int = 1,
) -> go.Figure:

    history = position_vectors_for_period(orbital_elements, number_of_orbits)
    seconds = list(range(len(history)))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=seconds,
            y=[vector.x for vector in history],
            mode="lines",
            name="x",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=seconds,
            y=[vector.y for vector in history],
            mode="lines",
            name="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=seconds,
            y=[vector.z for vector in history],
            mode="lines",
            name="z",
        )
    )

    fig.update_layout(
        title="Position vector over time",
        xaxis_title="Time [s]",
        yaxis_title="Position [m]",
    )

    return fig


def build_velocity_vector_figure(
    orbital_elements: OrbitalElements,
    number_of_orbits: int = 1,
) -> go.Figure:

    history = velocity_vectors_for_period(orbital_elements, number_of_orbits)
    seconds = list(range(len(history)))

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=seconds,
            y=[vector.x for vector in history],
            mode="lines",
            name="vx",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=seconds,
            y=[vector.y for vector in history],
            mode="lines",
            name="vy",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=seconds,
            y=[vector.z for vector in history],
            mode="lines",
            name="vz",
        )
    )

    fig.update_layout(
        title="Velocity vector over time",
        xaxis_title="Time [s]",
        yaxis_title="Velocity [m/s]",
    )

    return fig
