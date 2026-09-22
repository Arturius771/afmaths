import math

import plotly.graph_objects as go
from astronomy_types import Anomaly, MeanAnomaly, Radians, Scalar

from afmaths.constants import EXAMPLE_ELEMENTS
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    eccentric_anomaly_solved,
    newtons_method_eccentric_anomaly,
)


def build_newton_iteration_figure() -> go.Figure:
    eccentricity = EXAMPLE_ELEMENTS.eccentricity
    mean_anomaly = MeanAnomaly(Anomaly(Radians(Scalar(1.8 * math.pi))))

    _, history = eccentric_anomaly_solved(
        newtons_method_eccentric_anomaly,
        eccentricity,
        mean_anomaly,
    )

    def function(E: float) -> float:
        return E - eccentricity * math.sin(E) - mean_anomaly

    def derivative(E: float) -> float:
        return 1 - eccentricity * math.cos(E)

    guesses = [float(row[1]) for row in history]

    min_E = min(guesses) - 1
    max_E = max(guesses) + 1

    resolution = 300
    step = (max_E - min_E) / (resolution - 1)

    curve_x = [min_E + index * step for index in range(resolution)]
    curve_y = [function(E) for E in curve_x]

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=curve_x,
            y=curve_y,
            mode="lines",
            name="f(E)",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[min_E, max_E],
            y=[0, 0],
            mode="lines",
            name="y = 0",
        )
    )

    frames = []

    # Each frame represents E_i -> E_(i+1).
    for iteration in range(len(guesses) - 1):
        E_i = guesses[iteration]
        E_next = guesses[iteration + 1]

        f_E_i = function(E_i)
        slope = derivative(E_i)

        # The tangent only needs to span from the current point to its
        # intersection with the x-axis.
        tangent_x = [E_i, E_next]
        tangent_y = [
            f_E_i,
            0,
        ]

        frames.append(
            go.Frame(
                name=str(iteration),
                data=[
                    go.Scatter(
                        x=curve_x,
                        y=curve_y,
                        mode="lines",
                        name="f(E)",
                    ),
                    go.Scatter(
                        x=[min_E, max_E],
                        y=[0, 0],
                        mode="lines",
                        name="y = 0",
                    ),
                    go.Scatter(
                        x=tangent_x,
                        y=tangent_y,
                        mode="lines",
                        name="Tangent",
                    ),
                    go.Scatter(
                        x=[E_i],
                        y=[f_E_i],
                        mode="markers+text",
                        text=[f"E{iteration}"],
                        textposition="top center",
                        name="Current guess",
                    ),
                    go.Scatter(
                        x=[E_next],
                        y=[0],
                        mode="markers+text",
                        text=[f"E{iteration + 1}"],
                        textposition="bottom center",
                        name="Next guess",
                    ),
                ],
                layout=go.Layout(
                    title=(
                        "Newton-Raphson iteration "
                        f"{iteration}: "
                        f"E{iteration} = {E_i:.6f} → "
                        f"E{iteration + 1} = {E_next:.6f}"
                    )
                ),
            )
        )

    figure.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="lines",
            name="Tangent",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="markers+text",
            name="Current guess",
        )
    )

    figure.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="markers+text",
            name="Next guess",
        )
    )

    figure.frames = frames

    if frames:
        for trace_index, trace in enumerate(frames[0].data):
            figure.data[trace_index].update(trace)

    figure.update_layout(
        title="Newton-Raphson iteration",
        xaxis_title="Eccentric anomaly E [rad]",
        yaxis_title="f(E)",
        sliders=[
            {
                "active": 0,
                "currentvalue": {
                    "prefix": "Iteration: ",
                },
                "steps": [
                    {
                        "label": str(iteration),
                        "method": "animate",
                        "args": [
                            [str(iteration)],
                            {
                                "mode": "immediate",
                                "frame": {
                                    "duration": 0,
                                    "redraw": True,
                                },
                                "transition": {
                                    "duration": 0,
                                },
                            },
                        ],
                    }
                    for iteration in range(len(frames))
                ],
            }
        ],
    )

    return figure
