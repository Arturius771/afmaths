from __future__ import annotations

from dataclasses import replace
import math
import plotly.graph_objects as go

from afmaths.constants import EARTH_MU, EARTH_RADIUS, EARTH_RADIUS
from afmaths.physics.space.engineering.astrodynamics.phase_orbit import (
    phase_apoapsis,
    phase_orbit,
    phase_periapsis,
)
from afmaths.physics.space.celestial_mechanics import (
    apoapsis_radius,
    orbital_period,
    periapsis_radius,
)
from afmaths.types import DeltaV
from afmaths.visualisations.base import (
    coordinates_for_elements,
    eccentric_anomaly,
    eccentric_anomaly_from_true_anomaly,
    normalise_angle_rad,
    plotted_radius_for_eccentric_anomaly,
    scale_orbital_elements_for_plot,
    true_anomaly,
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
    plot_origin,
    plot_max,
    plot_min,
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
)

AHEAD_BEHIND_CUTOFF_RAD = math.pi


def forward_true_anomaly_delta_rad(
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
) -> float:
    """
    Return the forward prograde true-anomaly separation in radians.

    Example:
        initial = 1 rad, desired = 2 rad -> 1 rad
        initial = 1 rad, desired = 5 rad -> 4 rad
    """
    return normalise_angle_rad(desired_true_anomaly - initial_true_anomaly)


def phase_true_anomaly_delta(
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
) -> TrueAnomaly:
    """
    Return the signed phase true-anomaly delta.

    If the forward separation is <= 3.14 rad, the target is treated as ahead.
    The phase orbit should have a shorter period, so the delta is positive.

    If the forward separation is > 3.14 rad, the target is treated as behind.
    The phase orbit should have a longer period, so the delta is negative.
    """
    forward_delta = forward_true_anomaly_delta_rad(
        initial_true_anomaly,
        desired_true_anomaly,
    )

    if forward_delta <= AHEAD_BEHIND_CUTOFF_RAD:
        signed_delta = forward_delta
    else:
        signed_delta = -(2 * math.pi - forward_delta)

    return true_anomaly(signed_delta)


def phase_direction_label(
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
) -> str:
    forward_delta = forward_true_anomaly_delta_rad(
        initial_true_anomaly,
        desired_true_anomaly,
    )

    if forward_delta <= AHEAD_BEHIND_CUTOFF_RAD:
        return "ahead"

    return "behind"


def true_anomaly_plot_node(
    name: str,
    label: str,
    primary_focus_plot_coordinate: Coordinate2D,
    orbital_elements: OrbitalElements,
    true_anomaly_value: TrueAnomaly,
    colour: str,
    symbol: str,
) -> PlotNode:
    E = eccentric_anomaly_from_true_anomaly(
        orbital_elements.eccentricity,
        true_anomaly_value,
    )

    return PlotNode(
        name=name,
        coordinate=coordinates_for_elements(
            primary_focus_plot_coordinate,
            orbital_elements,
            E,
        ),
        text=(f"{label}<br>" f"ν = {true_anomaly_value:.3f} rad"),
        colour=colour,
        symbol=symbol,
    )


def phase_is_higher_than_original(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
) -> bool:
    return phase_orbit_elements.semi_major_axis > original_orbit.semi_major_axis


def align_phase_poi_to_initial_true_anomaly(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
    initial_true_anomaly: TrueAnomaly,
) -> OrbitalElements:
    """Rotate the phase orbit so its burn/return apsis is at the selected POI."""
    phase_poi_true_anomaly = (
        0.0
        if phase_is_higher_than_original(phase_orbit_elements, original_orbit)
        else math.pi
    )
    poi_direction = original_orbit.argument_of_periapsis + initial_true_anomaly
    phase_argument_of_periapsis = normalise_angle_rad(
        poi_direction - phase_poi_true_anomaly
    )

    return replace(
        phase_orbit_elements,
        argument_of_periapsis=ArgumentOfPeriapsis(
            Radians(Scalar(phase_argument_of_periapsis))
        ),
    )


def expected_shared_apsis_radius(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
) -> Distance:
    """
    Return the original-orbit apsis radius that should be shared with the phase orbit.

    Higher phase orbit:
        phase periapsis = original periapsis

    Lower phase orbit:
        phase apoapsis = original apoapsis
    """
    if phase_is_higher_than_original(phase_orbit_elements, original_orbit):
        return periapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )

    return apoapsis_radius(
        original_orbit.semi_major_axis,
        original_orbit.eccentricity,
    )


def phase_poi_label(
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
) -> tuple[str, str]:
    if phase_is_higher_than_original(phase_orbit_elements, original_orbit):
        return "shared periapsis", "higher phase orbit"

    return "shared apoapsis", "lower phase orbit"


def phase_poi_eccentric_anomaly_for_plot(
    primary_focus_plot_coordinate: Coordinate2D,
    phase_orbit_for_plot: OrbitalElements,
    expected_shared_apsis_radius_for_plot: Distance,
) -> EccentricAnomaly:
    """
    Pick the plotted phase-orbit endpoint that is actually the shared apsis.

    This avoids assuming that E=0 is visually the right endpoint. It chooses the
    endpoint whose plotted radius from the primary focus matches the expected
    shared original-orbit apsis radius.
    """
    endpoint_a = eccentric_anomaly(0.0)
    endpoint_b = eccentric_anomaly(math.pi)

    endpoint_a_radius = plotted_radius_for_eccentric_anomaly(
        primary_focus_plot_coordinate,
        phase_orbit_for_plot,
        endpoint_a,
    )

    endpoint_b_radius = plotted_radius_for_eccentric_anomaly(
        primary_focus_plot_coordinate,
        phase_orbit_for_plot,
        endpoint_b,
    )

    endpoint_a_error = abs(endpoint_a_radius - expected_shared_apsis_radius_for_plot)
    endpoint_b_error = abs(endpoint_b_radius - expected_shared_apsis_radius_for_plot)

    if endpoint_a_error <= endpoint_b_error:
        return endpoint_a

    return endpoint_b


def poi_plot_node(
    name: str,
    primary_focus_plot_coordinate: Coordinate2D,
    phase_orbit_for_plot: OrbitalElements,
    phase_orbit_elements: OrbitalElements,
    original_orbit: OrbitalElements,
    distance_scale: Distance,
    delta_v: DeltaV,
    phase_period: Second,
) -> PlotNode:
    shared_apsis_label, phase_orbit_label = phase_poi_label(
        phase_orbit_elements,
        original_orbit,
    )

    shared_apsis_radius_for_plot = distance_to_scale_distance(
        expected_shared_apsis_radius(
            phase_orbit_elements,
            original_orbit,
        ),
        distance_scale,
    )

    poi_E = phase_poi_eccentric_anomaly_for_plot(
        primary_focus_plot_coordinate,
        phase_orbit_for_plot,
        shared_apsis_radius_for_plot,
    )

    return PlotNode(
        name=name,
        coordinate=coordinates_for_elements(
            primary_focus_plot_coordinate,
            phase_orbit_for_plot,
            poi_E,
        ),
        text=(
            "POI<br>"
            f"{shared_apsis_label}<br>"
            f"{phase_orbit_label}<br>"
            f"Δv = {delta_v:.4f} m/s<br>"
            f"T₂ = {phase_period:.2f} s"
        ),
        colour="red",
        symbol="x",
    )


def build_phase_orbit_2d_perifocal_figure(
    settings: PlotOrbital2DSettings,
    original_orbit: OrbitalElements,
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
    gravitational_parameter: GravitationalParameter,
    central_body_name: str = "Earth",
    central_body_radius: Distance = EARTH_RADIUS,
    title_prefix: str = "Phasing orbit in the perifocal frame",
) -> go.Figure:
    """
    Build a phase-orbit visualisation.

    `original_orbit` must be supplied in SI physical units (metres), because
    the astrodynamics functions use it with μ in m³/s².

    The plotting copies of the orbits are scaled internally.
    """
    primary_focus_plot_coordinate = plot_origin()

    signed_phase_delta = phase_true_anomaly_delta(
        initial_true_anomaly,
        desired_true_anomaly,
    )

    delta_v, _, phase_orbit_elements = phase_orbit(
        original_orbit,
        signed_phase_delta,
        gravitational_parameter,
    )
    phase_orbit_elements = align_phase_poi_to_initial_true_anomaly(
        phase_orbit_elements,
        original_orbit,
        initial_true_anomaly,
    )

    calculated_phase_period = orbital_period(
        phase_orbit_elements.semi_major_axis,
        gravitational_parameter,
    )

    original_orbit_for_plot = scale_orbital_elements_for_plot(
        original_orbit,
        Distance(Scalar(settings.distance_scale)),
    )

    phase_orbit_for_plot = scale_orbital_elements_for_plot(
        phase_orbit_elements,
        Distance(Scalar(settings.distance_scale)),
    )

    return add_plot_centre(
        figure_layout(
            figure_planetary_body(
                add_perifocal_orbit_line(
                    add_perifocal_orbit_line(
                        add_plot_node(
                            add_plot_node(
                                add_plot_node(
                                    go.Figure(),
                                    true_anomaly_plot_node(
                                        name="Initial reference anomaly",
                                        label="Initial reference",
                                        primary_focus_plot_coordinate=primary_focus_plot_coordinate,
                                        orbital_elements=original_orbit_for_plot,
                                        true_anomaly_value=initial_true_anomaly,
                                        colour="blue",
                                        symbol="circle",
                                    ),
                                ),
                                true_anomaly_plot_node(
                                    name="Desired reference anomaly",
                                    label="Desired reference",
                                    primary_focus_plot_coordinate=primary_focus_plot_coordinate,
                                    orbital_elements=original_orbit_for_plot,
                                    true_anomaly_value=desired_true_anomaly,
                                    colour="green",
                                    symbol="diamond",
                                ),
                            ),
                            poi_plot_node(
                                name="POI at shared apsis",
                                primary_focus_plot_coordinate=primary_focus_plot_coordinate,
                                phase_orbit_for_plot=phase_orbit_for_plot,
                                phase_orbit_elements=phase_orbit_elements,
                                original_orbit=original_orbit,
                                distance_scale=Distance(
                                    Scalar(settings.distance_scale)
                                ),
                                delta_v=delta_v,
                                phase_period=calculated_phase_period,
                            ),
                        ),
                        primary_focus_plot_coordinate,
                        PlotPerifocalOrbitLine(
                            name="Original orbit",
                            orbital_elements=original_orbit_for_plot,
                            colour="grey",
                        ),
                    ),
                    primary_focus_plot_coordinate,
                    PlotPerifocalOrbitLine(
                        name="Phase orbit",
                        orbital_elements=phase_orbit_for_plot,
                        colour="orange",
                        show_secondary_focus=True,
                    ),
                ),
                primary_focus_plot_coordinate,
                central_body_radius_plot(
                    central_body_radius,
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
                f"Initial ta = {initial_true_anomaly:.3f} rad, "
                f"desired ta = {desired_true_anomaly:.3f} rad, "
                f"forward Δta = {forward_true_anomaly_delta_rad(
                    initial_true_anomaly,
                    desired_true_anomaly,
                ):.3f} rad<br>"
                f"Signed phase Δta = {signed_phase_delta:.3f} rad "
                f"({phase_direction_label(
                        initial_true_anomaly,
                        desired_true_anomaly,
                    )
                }), cutoff = {AHEAD_BEHIND_CUTOFF_RAD:.2f} rad<br>"
                f"Original period = {orbital_period( original_orbit.semi_major_axis, gravitational_parameter,):.2f} s, "
                f"phase period = {calculated_phase_period:.2f} s<br>"
                f"Phase periapsis = {phase_periapsis(
                    phase_orbit_elements.semi_major_axis,
                    original_orbit,
                ):.2f} m, "
                f"phase apoapsis = {phase_apoapsis(
                    phase_orbit_elements.semi_major_axis,
                    original_orbit,
                ):.2f} m, "
                f"Δv = {delta_v:.4f} m/s"
            ),
        ),
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )


DISTANCE_SCALE = 12_824.9333333 * 1000
INITIAL_ALTITUDE_M = Distance(Scalar(200_000_000))


if __name__ == "__main__":
    original_orbit = OrbitalElements(
        Inclination(Radians(Scalar(0))),
        RightAscension(Radians(Scalar(0))),
        ArgumentOfPeriapsis(Radians(Scalar(0.0))),
        SemiMajorAxis(Distance(Scalar(EARTH_RADIUS + INITIAL_ALTITUDE_M))),
        Eccentricity(Ratio(Scalar(0.0))),
        TrueAnomaly(Anomaly(Radians(Scalar(0.0)))),
    )

    build_phase_orbit_2d_perifocal_figure(
        settings=PlotOrbital2DSettings(
            distance_scale=DISTANCE_SCALE,
            plot_width=1000,
            plot_height=1000,
        ),
        original_orbit=original_orbit,
        # 1 rad -> 5 rad has forward Δν = 4 rad.
        # Since 4 > 3.14, it is treated as "behind" and uses a higher phase orbit.
        initial_true_anomaly=TrueAnomaly(Anomaly(Radians(Scalar(0.5)))),
        desired_true_anomaly=TrueAnomaly(Anomaly(Radians(Scalar(1.0)))),
        gravitational_parameter=EARTH_MU,
    ).show()
