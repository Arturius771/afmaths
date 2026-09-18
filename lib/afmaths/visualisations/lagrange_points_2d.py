from __future__ import annotations
from math import dist

import plotly.graph_objects as go

from afmaths.afmath_types import Mass
from astronomy_types import Coordinate2D, Distance, Vector2D

from afmaths.operation import negate
from afmaths.physics.space.celestial_mechanics.gravitation import (
    barycenter,
    lagrange_points,
    mass_parameter,
)
from base import translate_coordinate


def build_lagrange_points_figure(
    mass_1: Mass,
    mass_2: Mass,
    distance: Distance,
    plot_width: int | None = None,
    plot_height: int | None = None,
) -> go.Figure:
    """Build a 2D visualisation of the five Lagrange points."""

    mu = mass_parameter(mass_1, mass_2)

    l1, l2, l3, l4, l5 = lagrange_points(mass_1, mass_2, distance)

    system_barycenter = barycenter(mass_1, mass_2, distance)

    barycentric_offset = Coordinate2D(
        negate(system_barycenter),
        0,
    )

    primary = translate_coordinate(
        Coordinate2D(0, 0),
        barycentric_offset,
    )

    secondary = translate_coordinate(
        Coordinate2D(distance, 0),
        barycentric_offset,
    )

    figure = go.Figure()

    # Two massive bodies.
    figure.add_trace(
        go.Scatter(
            x=[primary.x, secondary.x],
            y=[0, 0],
            mode="markers+text",
            text=["m₁", "m₂"],
            textposition="top center",
            marker=dict(size=[24, 16]),
            name="Bodies",
            hovertemplate=("x=%{x:.6g} m" "<br>y=%{y:.6g} m" "<extra>%{text}</extra>"),
        )
    )

    # L1, L2 and L3.
    figure.add_trace(
        go.Scatter(
            x=[l1.x, l2.x, l3.x],
            y=[l1.y, l2.y, l3.y],
            mode="markers+text",
            text=["L1", "L2", "L3"],
            textposition="top center",
            marker=dict(size=10),
            name="Collinear Lagrange points",
            hovertemplate=(
                "%{text}" "<br>x=%{x:.6g} m" "<br>y=%{y:.6g} m" "<extra></extra>"
            ),
        )
    )

    # L4 and L5.
    figure.add_trace(
        go.Scatter(
            x=[l4.x, l5.x],
            y=[l4.y, l5.y],
            mode="markers+text",
            text=["L4", "L5"],
            textposition=["top center", "bottom center"],
            marker=dict(size=10),
            name="Triangular Lagrange points",
            hovertemplate=(
                "%{text}" "<br>x=%{x:.6g} m" "<br>y=%{y:.6g} m" "<extra></extra>"
            ),
        )
    )

    # Show the equilateral geometry of L4 and L5.
    figure.add_trace(
        go.Scatter(
            x=[
                primary.x,
                l4.x,
                secondary.x,
                None,
                primary.x,
                l5.x,
                secondary.x,
            ],
            y=[
                0,
                l4.y,
                0,
                None,
                0,
                l5.y,
                0,
            ],
            mode="lines",
            line=dict(dash="dot"),
            name="L4/L5 geometry",
            hoverinfo="skip",
        )
    )

    figure.update_layout(
        title=(
            "Lagrange Points"
            f"<br><sup>μ = {float(mu):.6g}, "
            f"separation = {float(distance):.6g} m</sup>"
        ),
        xaxis_title="Barycentric x (m)",
        yaxis_title="Barycentric y (m)",
        showlegend=True,
    )

    if plot_width is not None:
        figure.update_layout(width=plot_width)

    if plot_height is not None:
        figure.update_layout(height=plot_height)

    figure.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    return figure
