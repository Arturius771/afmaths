from __future__ import annotations

import math

import plotly.graph_objects as go

from afmaths.constants import DeltaV, EARTH_MU_KM_CUBED
from afmaths.physics.space.celestial_mechanics import orbit_radius, orbital_period
from afmaths.visualisations.base import (
    TransferApsis,
    apsis_radius,
    burn_direction,
    delta_v_between_speeds,
    eccentric_anomaly_for_transfer_radius,
    opposite_apsis,
    scaled_semi_major_axis_km,
    transfer_arc_angles,
    transfer_orbit_from_apsides,
    velocity_at_radius_km_s,
)
from afmaths.visualisations.helpers import (
    OrbitPlot2DSettings,
    PerifocalOrbitLine,
    PlotNode,
    add_perifocal_orbit_line,
    add_plot_centre,
    add_plot_node,
    central_body_radius_plot,
    figure_layout,
    figure_planetary_body,
    plot_centre,
    plot_max,
    plot_min,
)
from afmaths.visualisations.base import coordinates_for_elements
from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    Eccentricity,
    GravitationalParameter,
    Inclination,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
    Velocity,
)


def transfer_burn_plot_nodes(
    settings: OrbitPlot2DSettings,
    primary_focus_plot_coordinate: Coordinate2D,
    initial_orbit: OrbitalElements,
    transfer_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    start_apsis: TransferApsis,
    final_apsis: TransferApsis,
    start_radius: Distance,
    final_radius: Distance,
    transfer_start_eccentric_anomaly: EccentricAnomaly,
    transfer_arrival_eccentric_anomaly: EccentricAnomaly,
    transfer_time: Second,
    mu: GravitationalParameter,
) -> list[PlotNode]:
    initial_speed = velocity_at_radius_km_s(
        initial_orbit,
        start_radius,
        settings.distance_scale_km,
        mu,
    )

    transfer_start_speed = velocity_at_radius_km_s(
        transfer_orbit,
        start_radius,
        settings.distance_scale_km,
        mu,
    )

    transfer_arrival_speed = velocity_at_radius_km_s(
        transfer_orbit,
        final_radius,
        settings.distance_scale_km,
        mu,
    )

    final_speed = velocity_at_radius_km_s(
        final_orbit,
        final_radius,
        settings.distance_scale_km,
        mu,
    )

    transfer_delta_v = delta_v_between_speeds(
        initial_speed,
        transfer_start_speed,
    )

    arrival_delta_v = delta_v_between_speeds(
        transfer_arrival_speed,
        final_speed,
    )

    transfer_direction = burn_direction(
        initial_speed,
        transfer_start_speed,
    )

    arrival_direction = burn_direction(
        transfer_arrival_speed,
        final_speed,
    )

    transfer_burn_coordinate = coordinates_for_elements(
        primary_focus_plot_coordinate,
        transfer_orbit,
        transfer_start_eccentric_anomaly,
    )

    arrival_burn_coordinate = coordinates_for_elements(
        primary_focus_plot_coordinate,
        transfer_orbit,
        transfer_arrival_eccentric_anomaly,
    )

    return [
        PlotNode(
            name=f"Transfer burn at initial {start_apsis.value}",
            coordinate=transfer_burn_coordinate,
            text=(
                f"Transfer burn at initial {start_apsis.value}<br>"
                f"Direction = {transfer_direction.value}<br>"
                f"Δv = {transfer_delta_v:.4f} km/s<br>"
                f"t = {Second(Scalar(0)):.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
        PlotNode(
            name=f"Arrival burn at final {final_apsis.value}",
            coordinate=arrival_burn_coordinate,
            text=(
                f"Arrival burn at final {final_apsis.value}<br>"
                f"Direction = {arrival_direction.value}<br>"
                f"Δv = {arrival_delta_v:.4f} km/s<br>"
                f"t = {transfer_time:.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
    ]


def build_hohmann_transfer_2d_perifocal_figure(
    settings: OrbitPlot2DSettings,
    initial_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    gravitational_parameter: GravitationalParameter,
    start_apsis: TransferApsis = TransferApsis.PERIAPSIS,
    final_apsis: TransferApsis | None = None,
    central_body_name: str = "Earth",
    central_body_radius_km: float = 6_371.0,
    title_prefix: str = "Hohmann transfer in the perifocal frame",
) -> go.Figure:
    final_apsis = final_apsis or opposite_apsis(start_apsis)
    primary_focus_plot_coordinate = plot_centre(settings)

    transfer_orbit = transfer_orbit_from_apsides(
        initial_orbit,
        final_orbit,
        start_apsis,
        final_apsis,
    )

    start_radius = apsis_radius(initial_orbit, start_apsis)
    final_radius = apsis_radius(final_orbit, final_apsis)

    transfer_periapsis_radius = min(start_radius, final_radius)
    transfer_apoapsis_radius = max(start_radius, final_radius)

    transfer_start_eccentric_anomaly = eccentric_anomaly_for_transfer_radius(
        start_radius,
        transfer_periapsis_radius,
        transfer_apoapsis_radius,
    )

    transfer_arrival_eccentric_anomaly = eccentric_anomaly_for_transfer_radius(
        final_radius,
        transfer_periapsis_radius,
        transfer_apoapsis_radius,
    )

    transfer_arc_start_angle, transfer_arc_end_angle = transfer_arc_angles(
        transfer_start_eccentric_anomaly,
        transfer_arrival_eccentric_anomaly,
    )

    transfer_period = orbital_period(
        scaled_semi_major_axis_km(
            transfer_orbit,
            settings.distance_scale_km,
        ),
        gravitational_parameter,
    )

    transfer_time = Second(Scalar(transfer_period / 2))

    burn_nodes = transfer_burn_plot_nodes(
        settings,
        primary_focus_plot_coordinate,
        initial_orbit,
        transfer_orbit,
        final_orbit,
        start_apsis,
        final_apsis,
        start_radius,
        final_radius,
        transfer_start_eccentric_anomaly,
        transfer_arrival_eccentric_anomaly,
        transfer_time,
        gravitational_parameter,
    )

    fig = go.Figure()

    fig = add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name="Initial orbit",
            orbital_elements=initial_orbit,
            colour="grey",
        ),
    )

    fig = add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name="Transfer arc",
            orbital_elements=transfer_orbit,
            colour="orange",
            start_eccentric_anomaly=transfer_arc_start_angle,
            end_eccentric_anomaly=transfer_arc_end_angle,
            show_secondary_focus=True,
        ),
    )

    fig = add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name="Final orbit",
            orbital_elements=final_orbit,
            colour="grey",
        ),
    )

    for node in burn_nodes:
        fig = add_plot_node(fig, node)

    fig = figure_planetary_body(
        fig,
        primary_focus_plot_coordinate,
        central_body_radius_plot(
            central_body_radius_km,
            settings.distance_scale_km,
        ),
        central_body_name,
        "Black",
        "blue",
        "green",
    )

    fig = figure_layout(
        fig,
        settings.plot_width,
        settings.plot_height,
        plot_min(settings),
        plot_max(settings),
    )

    fig = add_plot_centre(
        fig,
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )

    transfer_delta_v = delta_v_between_speeds(
        velocity_at_radius_km_s(
            initial_orbit,
            start_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
        velocity_at_radius_km_s(
            transfer_orbit,
            start_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
    )

    arrival_delta_v = delta_v_between_speeds(
        velocity_at_radius_km_s(
            transfer_orbit,
            final_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
        velocity_at_radius_km_s(
            final_orbit,
            final_radius,
            settings.distance_scale_km,
            gravitational_parameter,
        ),
    )

    total_delta_v = DeltaV(Velocity(Scalar(transfer_delta_v + arrival_delta_v)))

    fig.update_layout(
        title=(
            f"{title_prefix}<br>"
            f"Start = initial {start_apsis.value}, "
            f"arrival = final {final_apsis.value}<br>"
            f"Total Δv = {total_delta_v:.4f} km/s, "
            f"transfer time = {transfer_time:.2f} s"
        )
    )

    return fig


DISTANCE_SCALE_KM = 12_824.9333333

EARTH_RADIUS_KM = Distance(Scalar(6_371.0))
INITIAL_ALTITUDE_KM = Distance(Scalar(280_000.0))
TARGET_ALTITUDE_KM = Distance(Scalar(384_400.0 - 6_371.0))


def scaled_distance(distance_km: Distance) -> Distance:
    return Distance(Scalar(distance_km / DISTANCE_SCALE_KM))


if __name__ == "__main__":
    p = ArgumentOfPerigee(Radians(Scalar(math.radians(35))))
    build_hohmann_transfer_2d_perifocal_figure(
        settings=OrbitPlot2DSettings(
            distance_scale_km=DISTANCE_SCALE_KM,
        ),
        initial_orbit=OrbitalElements(
            Inclination(Radians(Scalar(0))),
            RightAscension(Radians(Scalar(0))),
            p,
            SemiMajorAxis(
                scaled_distance(
                    orbit_radius(
                        INITIAL_ALTITUDE_KM,
                        EARTH_RADIUS_KM,
                    )
                )
            ),
            Eccentricity(Ratio(Scalar(0.6))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        final_orbit=OrbitalElements(
            Inclination(Radians(Scalar(0))),
            RightAscension(Radians(Scalar(0))),
            p,
            SemiMajorAxis(
                scaled_distance(
                    orbit_radius(
                        TARGET_ALTITUDE_KM,
                        EARTH_RADIUS_KM,
                    )
                )
            ),
            Eccentricity(Ratio(Scalar(0.1))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        gravitational_parameter=EARTH_MU_KM_CUBED,
        start_apsis=TransferApsis.APOAPSIS,
    ).show()
