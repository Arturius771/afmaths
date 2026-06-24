from __future__ import annotations

import math

import plotly.graph_objects as go

from afmaths.constants import EARTH_MU_KM_CUBED, BurnDirection
from afmaths.physics.space.astrodynamics import (
    transfer_period,
    hohmann_transfer,
    transfer_eccentricity,
    transfer_semi_major_axis,
)
from afmaths.physics.space.celestial_mechanics import (
    orbit_radius,
    orbital_period,
    periapsis_radius,
)
from afmaths.visualisations.base import (
    coordinates_for_elements,
    eccentric_anomaly_for_transfer_radius,
    transfer_arc_angles,
)
from afmaths.visualisations.helpers import (
    PlotOrbital2DSettings,
    PlotPerifocalOrbitLine,
    PlotNode,
    add_perifocal_orbit_line,
    add_plot_centre,
    add_plot_node,
    central_body_radius_plot,
    distance_to_scale_distance,
    figure_layout,
    figure_planetary_body,
    plot_centre,
    plot_max,
    plot_min,
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
    primary_focus_plot_coordinate: Coordinate2D,
    transfer_orbit: OrbitalElements,
    transfer_delta_v: Velocity,
    arrival_delta_v: Velocity,
    direction: BurnDirection,
    transfer_start_eccentric_anomaly: EccentricAnomaly,
    transfer_arrival_eccentric_anomaly: EccentricAnomaly,
    transfer_time: Second,
) -> list[PlotNode]:
    return [
        PlotNode(
            name="Transfer burn at initial periapsis",
            coordinate=coordinates_for_elements(
                primary_focus_plot_coordinate,
                transfer_orbit,
                transfer_start_eccentric_anomaly,
            ),
            text=(
                f"Transfer burn at initial periapsis<br>"
                f"Direction = {direction}<br>"
                f"Δv = {transfer_delta_v:.4f} km/s<br>"
                f"t = {Second(Scalar(0)):.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
        PlotNode(
            name="Arrival burn at final circular orbit",
            coordinate=coordinates_for_elements(
                primary_focus_plot_coordinate,
                transfer_orbit,
                transfer_arrival_eccentric_anomaly,
            ),
            text=(
                f"Arrival burn at final circular orbit<br>"
                f"Direction = {direction}<br>"
                f"Δv = {arrival_delta_v:.4f} km/s<br>"
                f"t = {transfer_time:.2f} s"
            ),
            colour="red",
            symbol="x",
        ),
    ]


def build_hohmann_transfer_2d_perifocal_figure(
    settings: PlotOrbital2DSettings,
    initial_orbit: OrbitalElements,
    final_altitude: Distance,
    gravitational_parameter: GravitationalParameter,
    central_body_name: str = "Earth",
    central_body_radius_km: float = 6_371.0,
    title_prefix: str = "Hohmann transfer in the perifocal frame",
) -> go.Figure:
    primary_focus_plot_coordinate = plot_centre(settings)

    final_radius = orbit_radius(
        final_altitude,
        Distance(Scalar(central_body_radius_km)),
    )

    final_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        ArgumentOfPeriapsis(Radians(Scalar(0))),
        SemiMajorAxis(
            distance_to_scale_distance(final_radius, settings.distance_scale)
        ),
        Eccentricity(Ratio(Scalar(0))),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    start_radius = periapsis_radius(
        initial_orbit.semi_major_axis,
        initial_orbit.eccentricity,
    )

    transfer_periapsis_radius = min(start_radius, final_orbit.semi_major_axis)
    transfer_apoapsis_radius = max(start_radius, final_orbit.semi_major_axis)

    transfer_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        (
            ArgumentOfPeriapsis(
                Radians(Scalar(initial_orbit.argument_of_periapsis + math.pi))
            )
            if final_orbit.semi_major_axis < start_radius
            else initial_orbit.argument_of_periapsis
        ),
        SemiMajorAxis(
            transfer_semi_major_axis(
                transfer_periapsis_radius,
                transfer_apoapsis_radius,
            )
        ),
        Eccentricity(
            Ratio(
                Scalar(
                    abs(
                        transfer_eccentricity(
                            transfer_periapsis_radius,
                            transfer_apoapsis_radius,
                        )
                    )
                )
            )
        ),
        TrueAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    transfer_start_eccentric_anomaly = eccentric_anomaly_for_transfer_radius(
        start_radius,
        transfer_periapsis_radius,
        transfer_apoapsis_radius,
    )

    transfer_arrival_eccentric_anomaly = eccentric_anomaly_for_transfer_radius(
        final_orbit.semi_major_axis,
        transfer_periapsis_radius,
        transfer_apoapsis_radius,
    )

    transfer_arc_start_angle, transfer_arc_end_angle = transfer_arc_angles(
        transfer_start_eccentric_anomaly,
        transfer_arrival_eccentric_anomaly,
    )

    total_delta_v, transfer_delta_v, arrival_delta_v, direction, transfer_time = (
        hohmann_transfer(
            initial_altitude_km=Distance(
                Scalar(
                    scale_distance_to_distance(start_radius, settings.distance_scale)
                    - central_body_radius_km
                )
            ),
            target_altitude_km=final_altitude,
            initial_body_radius=Distance(Scalar(central_body_radius_km)),
            gravitational_parameter=gravitational_parameter,
        )
    )

    burn_nodes = transfer_burn_plot_nodes(
        primary_focus_plot_coordinate=primary_focus_plot_coordinate,
        transfer_orbit=transfer_orbit,
        transfer_delta_v=transfer_delta_v,
        arrival_delta_v=arrival_delta_v,
        direction=direction,
        transfer_start_eccentric_anomaly=transfer_start_eccentric_anomaly,
        transfer_arrival_eccentric_anomaly=transfer_arrival_eccentric_anomaly,
        transfer_time=transfer_time,
    )

    fig = go.Figure()

    for node in burn_nodes:
        fig = add_plot_node(fig, node)

    return add_plot_centre(
        figure_layout(
            figure_planetary_body(
                add_perifocal_orbit_line(
                    add_perifocal_orbit_line(
                        add_perifocal_orbit_line(
                            fig,
                            primary_focus_plot_coordinate,
                            PlotPerifocalOrbitLine(
                                name="Initial orbit",
                                orbital_elements=initial_orbit,
                                colour="grey",
                            ),
                        ),
                        primary_focus_plot_coordinate,
                        PlotPerifocalOrbitLine(
                            name="Transfer arc",
                            orbital_elements=transfer_orbit,
                            colour="orange",
                            start_eccentric_anomaly=transfer_arc_start_angle,
                            end_eccentric_anomaly=transfer_arc_end_angle,
                            show_secondary_focus=True,
                        ),
                    ),
                    primary_focus_plot_coordinate,
                    PlotPerifocalOrbitLine(
                        name="Final circular orbit",
                        orbital_elements=final_orbit,
                        colour="grey",
                    ),
                ),
                primary_focus_plot_coordinate,
                central_body_radius_plot(
                    central_body_radius_km,
                    settings.distance_scale,
                ),
                central_body_name,
                "Black",
                "blue",
                "green",
            ),
            settings.plot_width,
            settings.plot_height,
            plot_min(settings),
            plot_max(settings),
            title=(
                f"{title_prefix}<br>"
                f"Start = initial periapsis, "
                f"arrival = final circular orbit<br>"
                f"Total Δv = {total_delta_v:.4f} km/s, "
                f"transfer time = {transfer_time:.2f} s"
            ),
        ),
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )


DISTANCE_SCALE_KM = 12_824.9333333

EARTH_RADIUS_KM = Distance(Scalar(6_371.0))
INITIAL_ALTITUDE_KM = Distance(Scalar(140_000.0))
TARGET_ALTITUDE_KM = Distance(Scalar(60_000.0))


if __name__ == "__main__":
    build_hohmann_transfer_2d_perifocal_figure(
        settings=PlotOrbital2DSettings(
            distance_scale=DISTANCE_SCALE_KM,
            plot_width=1000,
            plot_height=1000,
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
            Eccentricity(Ratio(Scalar(0.2))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        final_altitude=TARGET_ALTITUDE_KM,
        gravitational_parameter=EARTH_MU_KM_CUBED,
    ).show()
