from __future__ import annotations

import math

import plotly.graph_objects as go

from afmaths.constants import DeltaV, EARTH_MU_KM_CUBED
from afmaths.physics.space.astrodynamics import (
    transfer_eccentricity,
    transfer_semi_major_axis,
)
from afmaths.physics.space.celestial_mechanics import (
    orbit_radius,
    orbital_period,
    periapsis_radius,
    vis_viva,
)
from afmaths.visualisations.base import (
    burn_direction,
    coordinates_for_elements,
    delta_v_between_speeds,
    eccentric_anomaly_for_transfer_radius,
    transfer_arc_angles,
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
    distance_to_scale_distance,
    scale_distance_to_distance,
)
from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
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
    start_radius: Distance,
    final_radius: Distance,
    transfer_start_eccentric_anomaly: EccentricAnomaly,
    transfer_arrival_eccentric_anomaly: EccentricAnomaly,
    transfer_time: Second,
    mu: GravitationalParameter,
) -> list[PlotNode]:
    initial_speed = vis_viva(
        gravitational_parameter=mu,
        orbit_radius=scale_distance_to_distance(start_radius, settings.distance_scale),
        semi_major_axis=SemiMajorAxis(
            scale_distance_to_distance(
                initial_orbit.semi_major_axis,
                settings.distance_scale,
            )
        ),
    )

    transfer_start_speed = vis_viva(
        gravitational_parameter=mu,
        orbit_radius=scale_distance_to_distance(start_radius, settings.distance_scale),
        semi_major_axis=SemiMajorAxis(
            scale_distance_to_distance(
                transfer_orbit.semi_major_axis,
                settings.distance_scale,
            )
        ),
    )

    transfer_arrival_speed = vis_viva(
        gravitational_parameter=mu,
        orbit_radius=scale_distance_to_distance(final_radius, settings.distance_scale),
        semi_major_axis=SemiMajorAxis(
            scale_distance_to_distance(
                transfer_orbit.semi_major_axis,
                settings.distance_scale,
            )
        ),
    )

    final_speed = vis_viva(
        gravitational_parameter=mu,
        orbit_radius=scale_distance_to_distance(final_radius, settings.distance_scale),
        semi_major_axis=SemiMajorAxis(
            scale_distance_to_distance(
                final_orbit.semi_major_axis,
                settings.distance_scale,
            )
        ),
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
            name="Arrival burn at final circular orbit",
            coordinate=transfer_burn_coordinate,
            text=(
                f"Arrival burn at final circular orbit<br>"
                f"Direction = {arrival_direction.value}<br>"
                f"Δv = {arrival_delta_v:.4f} km/s<br>"
                f"t = {transfer_time:.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
        PlotNode(
            name="Transfer burn at initial periapsis",
            coordinate=arrival_burn_coordinate,
            text=(
                f"Transfer burn at initial periapsis<br>"
                f"Direction = {transfer_direction.value}<br>"
                f"Δv = {transfer_delta_v:.4f} km/s<br>"
                f"t = {Second(Scalar(0)):.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
    ]


def build_hohmann_transfer_2d_perifocal_figure(
    settings: OrbitPlot2DSettings,
    initial_orbit: OrbitalElements,
    final_altitude: Distance,
    gravitational_parameter: GravitationalParameter,
    central_body_name: str = "Earth",
    central_body_radius_km: float = 6_371.0,
    title_prefix: str = "Hohmann transfer in the perifocal frame",
) -> go.Figure:
    primary_focus_plot_coordinate = plot_centre(settings)

    final_orbit_radius = distance_to_scale_distance(
        orbit_radius(
            final_altitude,
            EARTH_RADIUS_KM,
        ),
        settings.distance_scale,
    )

    final_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        ArgumentOfPeriapsis(Radians(Scalar(0))),
        SemiMajorAxis(final_orbit_radius),
        Eccentricity(Ratio(Scalar(0))),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    start_radius = periapsis_radius(
        initial_orbit.semi_major_axis,
        initial_orbit.eccentricity,
    )

    final_radius = final_orbit.semi_major_axis

    transfer_periapsis_radius = min(start_radius, final_radius)
    transfer_apoapsis_radius = max(start_radius, final_radius)

    transfer_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        initial_orbit.argument_of_periapsis,
        SemiMajorAxis(
            transfer_semi_major_axis(
                transfer_periapsis_radius,
                transfer_apoapsis_radius,
            )
        ),
        transfer_eccentricity(
            transfer_periapsis_radius,
            transfer_apoapsis_radius,
        ),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

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
        SemiMajorAxis(
            scale_distance_to_distance(
                transfer_orbit.semi_major_axis,
                settings.distance_scale,
            )
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
            name="Final circular orbit",
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
            settings.distance_scale,
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
        vis_viva(
            gravitational_parameter=gravitational_parameter,
            orbit_radius=scale_distance_to_distance(
                start_radius, settings.distance_scale
            ),
            semi_major_axis=SemiMajorAxis(
                scale_distance_to_distance(
                    initial_orbit.semi_major_axis,
                    settings.distance_scale,
                )
            ),
        ),
        vis_viva(
            gravitational_parameter=gravitational_parameter,
            orbit_radius=scale_distance_to_distance(
                start_radius, settings.distance_scale
            ),
            semi_major_axis=SemiMajorAxis(
                scale_distance_to_distance(
                    transfer_orbit.semi_major_axis,
                    settings.distance_scale,
                )
            ),
        ),
    )

    arrival_delta_v = delta_v_between_speeds(
        vis_viva(
            gravitational_parameter=gravitational_parameter,
            orbit_radius=scale_distance_to_distance(
                final_radius, settings.distance_scale
            ),
            semi_major_axis=SemiMajorAxis(
                scale_distance_to_distance(
                    transfer_orbit.semi_major_axis,
                    settings.distance_scale,
                )
            ),
        ),
        vis_viva(
            gravitational_parameter=gravitational_parameter,
            orbit_radius=scale_distance_to_distance(
                final_radius, settings.distance_scale
            ),
            semi_major_axis=SemiMajorAxis(
                scale_distance_to_distance(
                    final_orbit.semi_major_axis,
                    settings.distance_scale,
                )
            ),
        ),
    )

    total_delta_v = DeltaV(Velocity(Scalar(transfer_delta_v + arrival_delta_v)))

    fig.update_layout(
        title=(
            f"{title_prefix}<br>"
            f"Start = initial periapsis, "
            f"arrival = final circular orbit<br>"
            f"Total Δv = {total_delta_v:.4f} km/s, "
            f"transfer time = {transfer_time:.2f} s"
        )
    )

    return fig


DISTANCE_SCALE_KM = 12_824.9333333

EARTH_RADIUS_KM = Distance(Scalar(6_371.0))
INITIAL_ALTITUDE_KM = Distance(Scalar(140_000.0))
TARGET_ALTITUDE_KM = Distance(Scalar(400000.0 - EARTH_RADIUS_KM))


if __name__ == "__main__":
    build_hohmann_transfer_2d_perifocal_figure(
        settings=OrbitPlot2DSettings(
            distance_scale=DISTANCE_SCALE_KM,
        ),
        initial_orbit=OrbitalElements(
            Inclination(Radians(Scalar(0))),
            RightAscension(Radians(Scalar(0))),
            ArgumentOfPeriapsis(Radians(Scalar(math.radians(10)))),
            SemiMajorAxis(
                distance_to_scale_distance(
                    orbit_radius(
                        INITIAL_ALTITUDE_KM,
                        EARTH_RADIUS_KM,
                    ),
                    DISTANCE_SCALE_KM,
                )
            ),
            Eccentricity(Ratio(Scalar(0.6))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        final_altitude=TARGET_ALTITUDE_KM,
        gravitational_parameter=EARTH_MU_KM_CUBED,
    ).show()
