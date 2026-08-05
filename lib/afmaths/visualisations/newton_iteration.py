import math

import plotly.graph_objects as go

from afmaths.constants import EXAMPLE_ELEMENTS
from astronomy_types import Anomaly, MeanAnomaly, Radians, Scalar

from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    eccentric_anomaly_solved,
    newtons_method_eccentric_anomaly,
)


def build_newton_iteration_figure() -> go.Figure:
    _, history = eccentric_anomaly_solved(
        newtons_method_eccentric_anomaly,
        EXAMPLE_ELEMENTS.eccentricity,
        MeanAnomaly(Anomaly(Radians(Scalar(1.8 * math.pi)))),
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[row[0] for row in history],
            y=[row[1] for row in history],
            mode="lines+markers",
            name="Eccentric anomaly",
        )
    )
    fig.update_layout(
        title="Newton iteration convergence",
        xaxis_title="Iteration",
        yaxis_title="Eccentric anomaly E [rad]",
    )

    return fig
