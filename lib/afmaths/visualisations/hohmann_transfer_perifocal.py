from __future__ import annotations

import math

import plotly.graph_objects as go

from afmaths.constants import EARTH_MU_KM_CUBED
from afmaths.physics.space.engineering.astrodynamics import (
    hohmann_transfer_from_radii,
    transfer_eccentricity,
    transfer_semi_major_axis,
)
from afmaths.physics.space.celestial_mechanics import (
    orbit_radius,
    periapsis_radius,
)
from afmaths.types import BurnDirection
from afmaths.visualisations.base import (
    coordinates_for_elements,
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


def transfer_burn_plot_node(
    name: str,
    label: str,
    primary_focus_plot_coordinate: Coordinate2D,
    transfer_orbit: OrbitalElements,
    E: EccentricAnomaly,
    delta_v: Velocity,
    direction: BurnDirection,
    time: Second,
) -> PlotNode:
    return PlotNode(
        name=name,
        coordinate=coordinates_for_elements(
            primary_focus_plot_coordinate,
            transfer_orbit,
            E,
        ),
        text=(
            f"{label}<br>"
            f"Direction = {direction}<br>"
            f"Δv = {delta_v:.4f} km/s<br>"
            f"t = {time:.2f} s"
        ),
        colour="red",
        symbol="x",
    )


def plotted_radius_from_primary_focus(
    primary_focus_plot_coordinate: Coordinate2D,
    coordinate: Coordinate2D,
) -> float:
    return math.hypot(
        coordinate.x - primary_focus_plot_coordinate.x,
        coordinate.y - primary_focus_plot_coordinate.y,
    )


def plotted_radius_for_transfer_endpoint(
    primary_focus_plot_coordinate: Coordinate2D,
    transfer_orbit: OrbitalElements,
    E: EccentricAnomaly,
) -> float:
    return plotted_radius_from_primary_focus(
        primary_focus_plot_coordinate,
        coordinates_for_elements(
            primary_focus_plot_coordinate,
            transfer_orbit,
            E,
        ),
    )


def build_hohmann_transfer_2d_perifocal_figure(
    settings: PlotOrbital2DSettings,
    initial_orbit: OrbitalElements,
    final_altitude: Distance,
    gravitational_parameter: GravitationalParameter,
    central_body_name: str = "Earth",
    central_body_radius_km: Distance = Distance(Scalar(6_371.0)),
    title_prefix: str = "Hohmann transfer in the perifocal frame",
) -> go.Figure:
    primary_focus_plot_coordinate = plot_centre(settings)

    final_orbit = OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        ArgumentOfPeriapsis(Radians(Scalar(0))),
        SemiMajorAxis(
            distance_to_scale_distance(
                orbit_radius(
                    final_altitude,
                    Distance(Scalar(central_body_radius_km)),
                ),
                settings.distance_scale,
            )
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

    transfer_endpoint_a_eccentric_anomaly = EccentricAnomaly(
        Anomaly(Radians(Scalar(0)))
    )

    transfer_endpoint_b_eccentric_anomaly = EccentricAnomaly(
        Anomaly(Radians(Scalar(math.pi)))
    )

    transfer_endpoint_a_radius = plotted_radius_for_transfer_endpoint(
        primary_focus_plot_coordinate,
        transfer_orbit,
        transfer_endpoint_a_eccentric_anomaly,
    )

    transfer_endpoint_b_radius = plotted_radius_for_transfer_endpoint(
        primary_focus_plot_coordinate,
        transfer_orbit,
        transfer_endpoint_b_eccentric_anomaly,
    )

    endpoint_a_matches_start = abs(transfer_endpoint_a_radius - start_radius)
    endpoint_b_matches_start = abs(transfer_endpoint_b_radius - start_radius)

    if endpoint_a_matches_start <= endpoint_b_matches_start:
        transfer_burn_eccentric_anomaly = transfer_endpoint_a_eccentric_anomaly
        arrival_burn_eccentric_anomaly = transfer_endpoint_b_eccentric_anomaly
    else:
        transfer_burn_eccentric_anomaly = transfer_endpoint_b_eccentric_anomaly
        arrival_burn_eccentric_anomaly = transfer_endpoint_a_eccentric_anomaly

    total_delta_v, transfer_delta_v, arrival_delta_v, direction, transfer_time = (
        hohmann_transfer_from_radii(
            initial_radius=Distance(
                Scalar(
                    scale_distance_to_distance(start_radius, settings.distance_scale)
                )
            ),
            target_radius=orbit_radius(final_altitude, central_body_radius_km),
            mu=gravitational_parameter,
        )
    )

    fig = add_plot_node(
        go.Figure(),
        transfer_burn_plot_node(
            name="Transfer burn at initial periapsis",
            label="Transfer burn at initial periapsis",
            primary_focus_plot_coordinate=primary_focus_plot_coordinate,
            transfer_orbit=transfer_orbit,
            E=transfer_burn_eccentric_anomaly,
            delta_v=transfer_delta_v,
            direction=direction,
            time=Second(Scalar(0)),
        ),
    )

    fig = add_plot_node(
        fig,
        transfer_burn_plot_node(
            name="Arrival burn at final circular orbit",
            label="Arrival burn at final circular orbit",
            primary_focus_plot_coordinate=primary_focus_plot_coordinate,
            transfer_orbit=transfer_orbit,
            E=arrival_burn_eccentric_anomaly,
            delta_v=arrival_delta_v,
            direction=direction,
            time=transfer_time,
        ),
    )

    transfer_arc_start_angle, transfer_arc_end_angle = transfer_arc_angles(
        transfer_burn_eccentric_anomaly,
        arrival_burn_eccentric_anomaly,
    )

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
INITIAL_ALTITUDE_KM = Distance(Scalar(200_000))
TARGET_ALTITUDE_KM = Distance(Scalar(140_000))


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
            Eccentricity(Ratio(Scalar(0.0))),
            TrueAnomaly(Anomaly(Radians(Scalar(0)))),
        ),
        final_altitude=TARGET_ALTITUDE_KM,
        gravitational_parameter=EARTH_MU_KM_CUBED,
    ).show()
