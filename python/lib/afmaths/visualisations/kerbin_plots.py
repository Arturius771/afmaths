"""Independent Kerbin plots. No imports from other visualisation modules.

All distances are metres; the ground track is in a Kerbin-fixed frame.
Time zero is the supplied orbital-elements epoch and the prime meridian is
assumed aligned with the inertial +X axis at that epoch.
"""

from __future__ import annotations

import base64
import math
from pathlib import Path

import plotly.graph_objects as go
from astronomy_types import OrbitalElements, Scalar, Second

from afmaths.constants import KERBIN_MU
from afmaths.physics.space.celestial_mechanics.state_vector import state_vector_at_time

KERBIN_IMAGE_PATH = Path(__file__).resolve().parent / "kerbin.jpg"

KERBIN_ROTATION_PERIOD_SECONDS = 21_549.425  # KSP 1 stock Kerbin sidereal rotation
KERBIN_RADIUS_METRES = 600_000.0


def build_kerbin_orbit_plots(
    elements: OrbitalElements,
    *,
    orbit_count: float = 1.0,
    current_orbit_count: float = 1.0,
    points: int = 1000,
    show_lines: bool = True,
) -> list[go.Figure]:
    """Ground track, current position, orbital plane, and position/velocity history."""
    if orbit_count <= 0 or current_orbit_count <= 0 or points < 2:
        raise ValueError("Orbit counts must be positive and points >= 2.")
    a = float(elements.semi_major_axis)
    e = float(elements.eccentricity)
    if a <= 0 or not (0 <= e < 1):
        raise ValueError(
            "Kerbin control room requires an elliptical orbit (a > 0, 0 <= e < 1)."
        )

    orbital_period_seconds = 2 * math.pi * math.sqrt(a**3 / float(KERBIN_MU))
    duration_seconds = orbital_period_seconds * orbit_count
    current_duration_seconds = orbital_period_seconds * current_orbit_count

    def sample(
        duration: float,
    ) -> list[tuple[float, float, float, float, float, float, float]]:
        values = []
        for i in range(points):
            t = duration * i / (points - 1)
            state = state_vector_at_time(elements, Second(Scalar(t)), KERBIN_MU)
            p, v = state.position, state.velocity
            values.append(
                (
                    t,
                    float(p.x),
                    float(p.y),
                    float(p.z),
                    float(v.x),
                    float(v.y),
                    float(v.z),
                )
            )
        return values

    data = sample(duration_seconds)
    current_data = sample(current_duration_seconds)

    def geographic(
        samples: list[tuple[float, ...]],
    ) -> tuple[list[float | None], list[float | None]]:
        longitudes: list[float | None] = []
        latitudes: list[float | None] = []
        previous: float | None = None
        for t, x, y, z, *_ in samples:
            inertial_longitude = math.atan2(y, x)
            longitude = (
                math.degrees(
                    inertial_longitude
                    - 2 * math.pi * t / KERBIN_ROTATION_PERIOD_SECONDS
                )
                + 180
            ) % 360 - 180
            latitude = math.degrees(math.atan2(z, math.hypot(x, y)))
            if previous is not None and abs(longitude - previous) > 180:
                longitudes.append(None)
                latitudes.append(None)
            longitudes.append(longitude)
            latitudes.append(latitude)
            previous = longitude
        return longitudes, latitudes

    def add_kerbin_map(fig: go.Figure) -> None:
        """Place an equirectangular Kerbin map below latitude/longitude traces."""
        if not KERBIN_IMAGE_PATH.is_file():
            raise FileNotFoundError(
                f"Kerbin ground-track map not found: {KERBIN_IMAGE_PATH}. "
                "Place kerbin.jpg next to kerbin_plots.py."
            )
        suffix = KERBIN_IMAGE_PATH.suffix.lower()
        mime = "image/png" if suffix == ".png" else "image/jpeg"
        encoded = base64.b64encode(KERBIN_IMAGE_PATH.read_bytes()).decode("ascii")
        fig.add_layout_image(
            source=f"data:{mime};base64,{encoded}",
            xref="x",
            yref="y",
            x=-180,
            y=90,
            sizex=360,
            sizey=180,
            xanchor="left",
            yanchor="top",
            sizing="stretch",
            opacity=0.85,
            layer="below",
        )
        fig.update_layout(plot_bgcolor="white")
        fig.update_xaxes(range=[-180, 180])
        fig.update_yaxes(range=[-90, 90], scaleanchor="x", scaleratio=1)

    ground = go.Figure()
    lons, lats = geographic(data)
    ground.add_trace(
        go.Scatter(
            x=lons,
            y=lats,
            mode="lines" if show_lines else "markers",
            name="Kerbin ground track",
            line=dict(width=2),
        )
    )
    ground.update_layout(
        title=f"Kerbin ground track — {orbit_count:g} orbit(s)",
        xaxis_title="Longitude [degrees]",
        yaxis_title="Latitude [degrees]",
    )
    ground.update_xaxes(range=[-180, 180])
    add_kerbin_map(ground)

    current = go.Figure()
    clons, clats = geographic(current_data)
    current.add_trace(
        go.Scatter(
            x=clons,
            y=clats,
            mode="lines" if show_lines else "markers",
            name="Ground track",
        )
    )
    current.add_trace(
        go.Scatter(
            x=[clons[0]],
            y=[clats[0]],
            mode="markers",
            marker=dict(size=13, symbol="diamond", color="red"),
            name="Position at supplied epoch",
        )
    )
    current.update_layout(
        title=f"Kerbin ground track — epoch position / {current_orbit_count:g} orbit(s)",
        xaxis_title="Longitude [degrees]",
        yaxis_title="Latitude [degrees]",
    )
    current.update_xaxes(range=[-180, 180])
    add_kerbin_map(current)

    orbit = go.Figure()
    orbit.add_trace(
        go.Scatter(
            x=[s[1] / 1000 for s in data],
            y=[s[2] / 1000 for s in data],
            mode="lines",
            name="Orbit XY projection",
        )
    )
    orbit.add_trace(
        go.Scatter(
            x=[data[0][1] / 1000],
            y=[data[0][2] / 1000],
            mode="markers",
            marker=dict(size=10),
            name="Epoch position",
        )
    )
    theta = [2 * math.pi * i / 180 for i in range(181)]
    orbit.add_trace(
        go.Scatter(
            x=[KERBIN_RADIUS_METRES / 1000 * math.cos(t) for t in theta],
            y=[KERBIN_RADIUS_METRES / 1000 * math.sin(t) for t in theta],
            mode="lines",
            fill="toself",
            name="Kerbin equatorial outline",
        )
    )
    orbit.update_layout(
        title="Orbit projected onto Kerbin equatorial plane",
        xaxis_title="Inertial X [km]",
        yaxis_title="Inertial Y [km]",
    )
    orbit.update_yaxes(scaleanchor="x", scaleratio=1)

    position = go.Figure()
    velocity = go.Figure()
    t_minutes = [s[0] / 60 for s in data]
    for index, component in enumerate("xyz", start=1):
        position.add_trace(
            go.Scatter(
                x=t_minutes,
                y=[s[index] / 1000 for s in data],
                name=component,
                mode="lines",
            )
        )
        velocity.add_trace(
            go.Scatter(
                x=t_minutes,
                y=[s[index + 3] for s in data],
                name=f"v{component}",
                mode="lines",
            )
        )
    position.update_layout(
        title="Inertial position components",
        xaxis_title="Time since epoch [min]",
        yaxis_title="Position [km]",
    )
    velocity.update_layout(
        title="Inertial velocity components",
        xaxis_title="Time since epoch [min]",
        yaxis_title="Velocity [m/s]",
    )
    return [current, ground, orbit, position, velocity]
