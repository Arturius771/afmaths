import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    SemiMajorAxis,
    TrueAnomaly,
)

from afmaths.constants import EARTH_MU_KM_CUBED, EARTH_RADIUS_KM
from afmaths.physics.space.celestial_mechanics import orbit_radius, periapsis_radius
from afmaths.physics.space.engineering.astrodynamics.hohmann_transfer import (
    hohmann_transfer_from_radii,
)

INITIAL_ALTITUDE_KM = Distance(Scalar(10_000))
MAX = INITIAL_ALTITUDE_KM * 500
INTERVAL = INITIAL_ALTITUDE_KM / 2

if __name__ == "__main__":
    initial_orbit = OrbitalElements(
        Inclination(Radians(Scalar(0))),
        RightAscension(Radians(Scalar(0))),
        ArgumentOfPeriapsis(Radians(Scalar(math.radians(10)))),
        SemiMajorAxis(
            orbit_radius(
                INITIAL_ALTITUDE_KM,
                EARTH_RADIUS_KM,
            )
        ),
        Eccentricity(Ratio(Scalar(0.0))),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    initial_radius_km = orbit_radius(
        INITIAL_ALTITUDE_KM,
        EARTH_RADIUS_KM,
    )

    x = []
    initial_burn = []
    arrival_burn = []
    delta_v_data = []
    time_data_days = []

    for i in range(int(INITIAL_ALTITUDE_KM), int(MAX), int(INTERVAL)):
        target_radius_km = orbit_radius(
            Distance(Scalar(i)),
            EARTH_RADIUS_KM,
        )

        total_delta_v, transfer_delta_v, arrival_delta_v, direction, transfer_time = (
            hohmann_transfer_from_radii(
                initial_radius=initial_radius_km,
                target_radius=target_radius_km,
                mu=EARTH_MU_KM_CUBED,
            )
        )

        x.append(target_radius_km / initial_radius_km)
        delta_v_data.append(total_delta_v)
        initial_burn.append(transfer_delta_v)
        arrival_burn.append(arrival_delta_v)

        # Convert seconds to days so the values are more readable.
        time_data_days.append(transfer_time / 86_400)

    peak_delta_v = max(delta_v_data)
    peak_index = delta_v_data.index(peak_delta_v)
    peak_time_days = time_data_days[peak_index]
    peak_radius_km = x[peak_index] * initial_radius_km

    tradeoff_x = []
    days_per_m_per_s_saved = []
    tradeoff_time_days = []
    tradeoff_delta_v = []

    for index in range(peak_index + 1, len(x)):
        delta_v_saved_km_s = peak_delta_v - delta_v_data[index]
        delta_v_saved_m_s = delta_v_saved_km_s * 1000

        extra_time_days = time_data_days[index] - peak_time_days

        if delta_v_saved_m_s <= 0:
            continue

        tradeoff_x.append(x[index])
        days_per_m_per_s_saved.append(extra_time_days / delta_v_saved_m_s)
        tradeoff_time_days.append(time_data_days[index])
        tradeoff_delta_v.append(delta_v_data[index])

    best_tradeoff_index = days_per_m_per_s_saved.index(min(days_per_m_per_s_saved))

    best_tradeoff_x = tradeoff_x[best_tradeoff_index]
    best_tradeoff_delta_v = tradeoff_delta_v[best_tradeoff_index]
    best_tradeoff_time_days = tradeoff_time_days[best_tradeoff_index]
    best_tradeoff_days_per_m_per_s = days_per_m_per_s_saved[best_tradeoff_index]

    best_tradeoff_radius_km = best_tradeoff_x * initial_radius_km
    best_tradeoff_delta_v_saved_m_s = (peak_delta_v - best_tradeoff_delta_v) * 1000

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            "Hohmann transfer Δv",
            "Extra transfer time per Δv saved after the worst circular orbit",
        ),
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=delta_v_data,
            mode="lines",
            name="Total Δv",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=initial_burn,
            mode="lines",
            name="Initial burn Δv",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=arrival_burn,
            mode="lines",
            name="Arrival burn Δv",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=[x[peak_index]],
            y=[peak_delta_v],
            mode="markers",
            name=f"Worst circular orbit: {peak_radius_km:.0f} km",
            marker=dict(size=10),
            customdata=[
                [
                    peak_radius_km,
                    peak_time_days,
                ]
            ],
            hovertemplate=(
                "Worst circular orbit<br>"
                "Radius ratio: %{x:.2f}<br>"
                "Radius: %{customdata[0]:.0f} km<br>"
                "Total Δv: %{y:.4f} km/s<br>"
                "Transfer time: %{customdata[1]:.2f} days"
                "<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=[best_tradeoff_x],
            y=[best_tradeoff_delta_v],
            mode="markers",
            name=f"Best time/Δv tradeoff: {best_tradeoff_radius_km:.0f} km",
            marker=dict(size=12, symbol="diamond"),
            customdata=[
                [
                    best_tradeoff_radius_km,
                    best_tradeoff_time_days,
                    best_tradeoff_delta_v_saved_m_s,
                    best_tradeoff_days_per_m_per_s,
                ]
            ],
            hovertemplate=(
                "Best time/Δv tradeoff<br>"
                "Radius ratio: %{x:.2f}<br>"
                "Radius: %{customdata[0]:.0f} km<br>"
                "Total Δv: %{y:.4f} km/s<br>"
                "Transfer time: %{customdata[1]:.2f} days<br>"
                "Δv saved from peak: %{customdata[2]:.2f} m/s<br>"
                "Cost: %{customdata[3]:.2f} days per m/s saved"
                "<extra></extra>"
            ),
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=tradeoff_x,
            y=days_per_m_per_s_saved,
            mode="lines",
            name="Days per m/s saved",
            customdata=[
                [time_days, delta_v]
                for time_days, delta_v in zip(tradeoff_time_days, tradeoff_delta_v)
            ],
            hovertemplate=(
                "Radius ratio: %{x:.2f}<br>"
                "Days per m/s saved: %{y:.2f}<br>"
                "Transfer time: %{customdata[0]:.2f} days<br>"
                "Total Δv: %{customdata[1]:.4f} km/s"
                "<extra></extra>"
            ),
        ),
        row=2,
        col=1,
    )

    fig.update_layout(
        title=(
            "Hohmann transfer tradeoff "
            f"(initial orbit: {periapsis_radius(initial_orbit.semi_major_axis, initial_orbit.eccentricity):.0f} km)<br>"
            "<sup>After the worst circular orbit, Δv falls slightly, but the time cost grows rapidly</sup>"
        ),
        height=900,
    )

    fig.update_yaxes(
        title_text="Δv [km/s]",
        row=1,
        col=1,
    )

    fig.update_yaxes(
        title_text="Extra days per m/s saved",
        type="log",
        row=2,
        col=1,
    )

    fig.update_xaxes(
        title_text="Target radius / initial radius",
        row=2,
        col=1,
    )

    fig.show()
