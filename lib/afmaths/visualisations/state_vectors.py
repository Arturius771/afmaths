import plotly.graph_objects as go

from astronomy_types import OrbitalElements

from afmaths.physics.space.celestial_mechanics.state_vector import (
    position_vectors_for_period,
    velocity_vectors_for_period,
)


def _build_vector_figure(
    history: list,
    trace_names: tuple[str, str, str],
    title: str,
    yaxis_title: str,
) -> go.Figure:
    seconds = list(range(len(history)))
    fig = go.Figure()

    for component, trace_name in zip(("x", "y", "z"), trace_names, strict=True):
        fig.add_trace(
            go.Scatter(
                x=seconds,
                y=[getattr(vector, component) for vector in history],
                mode="lines",
                name=trace_name,
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Time [s]",
        yaxis_title=yaxis_title,
    )
    return fig


def build_position_vector_figure(
    orbital_elements: OrbitalElements,
    number_of_orbits: int = 1,
) -> go.Figure:
    return _build_vector_figure(
        position_vectors_for_period(orbital_elements, number_of_orbits),
        ("x", "y", "z"),
        "Position vector over time",
        "Position [m]",
    )


def build_velocity_vector_figure(
    orbital_elements: OrbitalElements,
    number_of_orbits: int = 1,
) -> go.Figure:
    return _build_vector_figure(
        velocity_vectors_for_period(orbital_elements, number_of_orbits),
        ("vx", "vy", "vz"),
        "Velocity vector over time",
        "Velocity [m/s]",
    )
