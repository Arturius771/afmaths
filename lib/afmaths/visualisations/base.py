from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import datetime
import math

import plotly.graph_objects as go

from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVectors,
    TrueAnomaly,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.constants import DeltaV, Mass
from afmaths.geometry import (
    calculate_foci,
    semi_minor_axis,
    translate_ellipse_coordinate,
)
from afmaths.physics.space.astrodynamics import (
    transfer_eccentricity,
    transfer_semi_major_axis,
)
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    apoapsis_radius,
    gravitational_parameter,
    orbital_elements_from_state_vectors,
    orbital_period,
    periapsis_radius,
    vis_viva,
)
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    python_datetime_to_fulldate,
    python_timedelta_to_seconds,
    vector3d,
)
from afmaths.physics.space.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)
from afmaths.physics.space.orbit_propagation import (
    eccentric_anomaly_at_time,
    generate_all_orbit_positions,
    orbit_state_vector_prediction_from_orbital_elements,
)

from afmaths.visualisations.helpers import (
    OrbitPlot2DSettings,
    plot_centre,
)


# Subject: orbital mechanics / Hohmann-transfer modelling.
# Defines which apsis of an orbit is being used as a transfer point.
# This is not Plotly/visualisation logic; it is domain vocabulary for transfer-orbit calculations.
class TransferApsis(Enum):
    PERIAPSIS = "periapsis"
    APOAPSIS = "apoapsis"


# Subject: astrodynamics / manoeuvre modelling.
# Classifies a burn by whether the target orbital speed is higher or lower than the current speed.
# This is not visualisation logic; it belongs with transfer / delta-v helpers if reused.
class BurnDirection(Enum):
    PROGRADE = "prograde"
    RETROGRADE = "retrograde"


# Subject: visualisation configuration, with astronomy-specific target metadata.
# Stores the plotting/display inputs for a body: label, Horizons target or elements, physical radius, and visual radius scale.
# This is mostly visualisation config, but it depends on Horizons/orbital concepts.
@dataclass(frozen=True)
class BodyPlotConfig:
    name: str
    target: HorizonsCommandTarget | OrbitalElements
    radius_km: float
    radius_scale: float


# Subject: visualisation configuration, with time/orbit-propagation settings.
# Stores the 3D orbit plot setup: centre body, gravitational parameter, scale, orbit sample count, and time interval.
# The time_offset_seconds property is a unit conversion for propagation, so the class straddles plotting config and orbital simulation config.
@dataclass(frozen=True)
class OrbitPlotSettings:
    centre: HorizonsCommandTarget
    gravitational_parameter: GravitationalParameter
    distance_scale_km: float
    orbit_points: int
    start_time: datetime.datetime
    time_offset: datetime.timedelta
    add_prediction_to_orbit: bool = True

    # Subject: time interval convenience for ephemeris/orbit propagation.
    # Computes the stop datetime by adding the configured time offset to the start time.
    # Not visualisation-specific.
    @property
    def stop_time(self) -> datetime.datetime:
        return self.start_time + self.time_offset

    # Subject: unit conversion for propagation.
    # Converts the configured datetime.timedelta into the astronomy_types Second wrapper.
    # This is a unit adapter for physics/orbit-propagation calls.
    @property
    def time_offset_seconds(self) -> Second:
        return Second(Scalar(python_timedelta_to_seconds(self.time_offset)))


# Subject: planar geometry / coordinate transform.
# Rotates an absolute 2D point about an absolute centre by angle radians using the standard 2D rotation matrix.
# This is generic geometry, not celestial mechanics, and could live in a geometry/coordinate-transform module.
def rotate_around_point(
    point: Coordinate2D,
    centre: Coordinate2D,
    angle: float,
) -> Coordinate2D:
    dx = point.x - centre.x
    dy = point.y - centre.y

    return Coordinate2D(
        centre.x + dx * math.cos(angle) - dy * math.sin(angle),
        centre.y + dx * math.sin(angle) + dy * math.cos(angle),
    )


# Subject: planar geometry / coordinate transform.
# Rotates a 2D vector/relative coordinate about the origin by angle radians using the standard 2D rotation matrix.
# Generic coordinate transform; not specifically visualisation or orbital mechanics.
def rotate_relative_coordinate(
    coordinate: Coordinate2D,
    angle: float,
) -> Coordinate2D:
    return Coordinate2D(
        coordinate.x * math.cos(angle) - coordinate.y * math.sin(angle),
        coordinate.x * math.sin(angle) + coordinate.y * math.cos(angle),
    )


# Subject: planar geometry / coordinate transform.
# Translates a local 2D coordinate by adding an origin offset.
# Generic geometry helper; not celestial mechanics and not Plotly-specific.
def translate_coordinate(
    origin: Coordinate2D,
    coordinate: Coordinate2D,
) -> Coordinate2D:
    return Coordinate2D(
        origin.x + coordinate.x,
        origin.y + coordinate.y,
    )


# Subject: conic geometry / orbital-elements geometry.
# Uses semi-major axis and eccentricity from OrbitalElements to compute the ellipse foci, then returns the primary focus in local perifocal ellipse coordinates.
# This is celestial/orbital geometry through the back door; it wraps calculate_foci and probably belongs near orbital-element geometry helpers.
def local_primary_focus_for_elements(elements: OrbitalElements) -> Coordinate2D:
    primary_focus, _ = calculate_foci(
        elements.semi_major_axis,
        elements.eccentricity,
    )

    return primary_focus


# Subject: conic geometry / orbital-elements geometry.
# Uses semi-major axis and eccentricity from OrbitalElements to compute the ellipse foci, then returns the secondary focus in local perifocal ellipse coordinates.
# This is orbital geometry, not visualisation; it wraps calculate_foci.
def local_secondary_focus_for_elements(elements: OrbitalElements) -> Coordinate2D:
    _, secondary_focus = calculate_foci(
        elements.semi_major_axis,
        elements.eccentricity,
    )

    return secondary_focus


# Subject: coordinate transform between orbital/perifocal coordinates and plot coordinates.
# Converts a local ellipse coordinate into the plot frame by: shifting it relative to the primary focus, rotating by argument of periapsis, then translating to the plotted primary focus.
# This mixes orbital frame semantics with generic 2D transforms; likely belongs in an orbit-coordinate-transform helper rather than visualisation helpers.
def local_to_plot_coordinate_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    local_coordinate: Coordinate2D,
) -> Coordinate2D:
    local_primary_focus = local_primary_focus_for_elements(elements)

    local_relative_to_primary_focus = Coordinate2D(
        local_coordinate.x - local_primary_focus.x,
        local_coordinate.y - local_primary_focus.y,
    )

    rotated = rotate_relative_coordinate(
        local_relative_to_primary_focus,
        elements.argument_of_periapsis,
    )

    return translate_coordinate(
        primary_focus_plot_coordinate,
        rotated,
    )


# Subject: orbital geometry projected into plot coordinates.
# Computes where the primary focus of an orbit should appear on the plot by mapping the local primary focus to the plot centre.
# This is mostly a visualisation adapter around orbital geometry.
def primary_focus_coordinates_for_elements(
    settings: OrbitPlot2DSettings,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        plot_centre(settings),
        elements,
        local_primary_focus_for_elements(elements),
    )


# Subject: orbital geometry projected into plot coordinates.
# Computes the plotted location of the secondary focus by transforming the local secondary focus into the plot frame.
# This is visualisation-adapter logic over celestial/conic geometry.
def secondary_focus_coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        local_secondary_focus_for_elements(elements),
    )


# Subject: orbital geometry projected into plot coordinates.
# Computes the plotted centre of the orbital ellipse by transforming the local ellipse origin into the plot frame.
# This is conic/orbit geometry plus a plotting-frame transform, not pure Plotly logic.
def ellipse_centre_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
) -> Coordinate2D:
    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        Coordinate2D(Scalar(0), Scalar(0)),
    )


# Subject: orbital geometry / perifocal coordinate conversion.
# Converts an eccentric anomaly into a local ellipse coordinate using semi-major/minor axes, then maps that coordinate into the plot frame.
# This is a core orbital-coordinate helper; the underlying calculation should probably reuse a celestial-mechanics/orbit-position helper if one exists.
def coordinates_for_elements(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    eccentric_anomaly: EccentricAnomaly,
) -> Coordinate2D:
    local_coordinate = translate_ellipse_coordinate(
        Coordinate2D(Scalar(0), Scalar(0)),
        elements.semi_major_axis,
        semi_minor_axis(elements.semi_major_axis, elements.eccentricity),
        eccentric_anomaly,
    )

    return local_to_plot_coordinate_for_elements(
        primary_focus_plot_coordinate,
        elements,
        local_coordinate,
    )


# Subject: unit/scale conversion for orbital elements.
# Converts plot-scaled OrbitalElements back to physical-ish units by multiplying semi-major axis by distance_scale_km.
# This is not visualisation rendering; it is a scale adapter and is risky because the unit semantics are easy to confuse.
def elements_scaled_to_plot(
    elements: OrbitalElements,
    distance_scale_km: float,
) -> OrbitalElements:
    return replace(
        elements,
        semi_major_axis=SemiMajorAxis(
            Distance(Scalar(elements.semi_major_axis / distance_scale_km))
        ),
    )


# Subject: unit conversion / orbital mechanics input preparation.
# Converts a plot-scaled semi-major axis into metres using distance_scale_km * 1000.
# This should probably be replaced with explicit unit conversion utilities or avoided by keeping physical units separate from plot units.
def semi_major_axis_metres(
    elements: OrbitalElements,
    distance_scale_km: float,
) -> SemiMajorAxis:
    return SemiMajorAxis(
        Distance(Scalar(elements.semi_major_axis * distance_scale_km * 1000))
    )


# Subject: thin alias for orbital-coordinate calculation.
# Simply delegates to coordinates_for_elements for an orbiting body's plotted coordinate at a given eccentric anomaly.
# This adds little value and probably does not need to exist.
def orbiting_body_coordinates(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    eccentric_anomaly: EccentricAnomaly,
) -> Coordinate2D:
    return coordinates_for_elements(
        primary_focus_plot_coordinate,
        elements,
        eccentric_anomaly,
    )


def tangent_vector_for_plot(
    primary_focus_plot_coordinate: Coordinate2D,
    plot_elements: OrbitalElements,
    eccentric_anomaly: EccentricAnomaly,
) -> VelocityVector:
    delta = 0.001

    current = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        plot_elements,
        eccentric_anomaly,
    )

    next_point = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        plot_elements,
        EccentricAnomaly(Anomaly(Radians(Scalar(float(eccentric_anomaly) + delta)))),
    )

    return VelocityVector(
        Velocity(Scalar(next_point.x - current.x)),
        Velocity(Scalar(next_point.y - current.y)),
        Velocity(Scalar(0)),
    )


# Subject: kinematics / numerical orbital velocity approximation.
# Estimates a 2D velocity vector by finite-differencing two plotted positions separated by period/10000 seconds.
# This is physics/kinematics and should likely use an existing state-vector/orbit-propagation velocity function instead of deriving velocity from plot coordinates.
def velocity_vector_at_time(
    primary_focus_plot_coordinate: Coordinate2D,
    elements: OrbitalElements,
    elapsed_time: float,
    distance_scale_km: float,
    mu: GravitationalParameter,
) -> VelocityVector:
    period = orbital_period(
        semi_major_axis_metres(elements, distance_scale_km),
        mu,
    )

    delta_time = period / 10000
    scaled_elements = elements_scaled_to_plot(elements, distance_scale_km)

    current_coordinates = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        elements,
        eccentric_anomaly_at_time(
            scaled_elements,
            Second(Scalar(elapsed_time)),
        ),
    )

    next_coordinates = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        elements,
        eccentric_anomaly_at_time(
            scaled_elements,
            Second(Scalar(elapsed_time + delta_time)),
        ),
    )

    return VelocityVector(
        Velocity(Scalar((next_coordinates.x - current_coordinates.x) / delta_time)),
        Velocity(Scalar((next_coordinates.y - current_coordinates.y) / delta_time)),
        Velocity(Scalar(0)),
    )


# Subject: Hohmann-transfer/orbital mechanics utility.
# Returns apoapsis for periapsis and periapsis for apoapsis, used to choose the other end of a transfer.
# This is domain logic, not visualisation.
def opposite_apsis(apsis: TransferApsis) -> TransferApsis:
    if apsis == TransferApsis.PERIAPSIS:
        return TransferApsis.APOAPSIS

    return TransferApsis.PERIAPSIS


# Subject: celestial mechanics / conic orbit geometry.
# Returns periapsis_radius or apoapsis_radius for an orbit depending on the requested apsis.
# This is a small selector over existing celestial_mechanics helpers.
def apsis_radius(
    orbit: OrbitalElements,
    apsis: TransferApsis,
) -> Distance:
    if apsis == TransferApsis.PERIAPSIS:
        return periapsis_radius(
            orbit.semi_major_axis,
            orbit.eccentricity,
        )

    return apoapsis_radius(
        orbit.semi_major_axis,
        orbit.eccentricity,
    )


# Subject: orbital geometry / argument of periapsis.
# Returns the inertial/perifocal plot angle of the selected apsis: argument_of_periapsis for periapsis, plus pi for apoapsis.
# This is orbital geometry, not plotting, though it is used to orient plotted transfer ellipses.
def apsis_angle(
    orbit: OrbitalElements,
    apsis: TransferApsis,
) -> float:
    if apsis == TransferApsis.PERIAPSIS:
        return orbit.argument_of_periapsis

    return orbit.argument_of_periapsis + math.pi


# Subject: Hohmann-transfer geometry / eccentric anomaly selection.
# Maps a transfer-burn radius to eccentric anomaly 0 at periapsis or pi at apoapsis.
# This only handles apsidal transfers and belongs with transfer-specific astrodynamics logic.
def eccentric_anomaly_for_transfer_radius(
    radius: Distance,
    transfer_periapsis_radius: Distance,
    transfer_apoapsis_radius: Distance,
) -> EccentricAnomaly:
    if radius == transfer_periapsis_radius:
        return EccentricAnomaly(Anomaly(Radians(Scalar(0))))

    if radius == transfer_apoapsis_radius:
        return EccentricAnomaly(Anomaly(Radians(Scalar(math.pi))))

    raise ValueError(
        "Transfer burn radius must be either transfer periapsis or apoapsis."
    )


# Subject: astrodynamics / Hohmann-style transfer construction.
# Builds transfer OrbitalElements from the selected apsides of the initial and final orbits: computes radii, transfer semi-major axis/eccentricity, and argument of periapsis orientation.
# This is definitely not visualisation; it should live in astrodynamics/transfer mechanics if kept.
def transfer_orbit_from_apsides(
    initial_orbit: OrbitalElements,
    final_orbit: OrbitalElements,
    start_apsis: TransferApsis,
    final_apsis: TransferApsis,
) -> OrbitalElements:
    start_radius = apsis_radius(initial_orbit, start_apsis)
    final_radius = apsis_radius(final_orbit, final_apsis)

    transfer_periapsis_radius = min(start_radius, final_radius)
    transfer_apoapsis_radius = max(start_radius, final_radius)

    start_angle = apsis_angle(initial_orbit, start_apsis)
    transfer_starts_at_periapsis = start_radius == transfer_periapsis_radius

    transfer_argument_of_periapsis = (
        start_angle if transfer_starts_at_periapsis else start_angle + math.pi
    )

    return OrbitalElements(
        initial_orbit.inclination,
        initial_orbit.right_ascension_of_ascending_node,
        ArgumentOfPerigee(Radians(Scalar(transfer_argument_of_periapsis))),
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


# Subject: unit/scale conversion.
# Converts a plot-scaled Distance back into kilometres by multiplying by distance_scale_km.
# This is a scale adapter caused by mixing plot units and physical units.
def scaled_distance_km(
    distance: Distance,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar(distance * distance_scale_km))


# Subject: unit/scale conversion for orbital elements.
# Converts a plot-scaled orbit semi-major axis back into kilometres by multiplying by distance_scale_km.
# This should probably be replaced by keeping OrbitalElements in real units and scaling only at render time.
def scaled_semi_major_axis_km(
    orbit: OrbitalElements,
    distance_scale_km: float,
) -> SemiMajorAxis:
    return SemiMajorAxis(Distance(Scalar(orbit.semi_major_axis * distance_scale_km)))


# Subject: celestial mechanics / vis-viva equation.
# Computes orbital speed at a radius using vis-viva after converting plot-scaled radius and semi-major axis back to kilometre units.
# The physics is already in vis_viva; this wrapper is mostly unit/scale adaptation and should likely be removed or moved near transfer calculations.
def velocity_at_radius_km_s(
    orbit: OrbitalElements,
    radius: Distance,
    distance_scale_km: float,
    mu: GravitationalParameter,
) -> Velocity:
    return vis_viva(
        gravitational_parameter=mu,
        orbit_radius=scaled_distance_km(radius, distance_scale_km),
        semi_major_axis=scaled_semi_major_axis_km(
            orbit,
            distance_scale_km,
        ),
    )


# Subject: manoeuvre classification / astrodynamics.
# Compares current and target speeds: if the target speed is higher, label the burn prograde; otherwise retrograde.
# This is transfer/maneuver domain logic, not visualisation.
def burn_direction(
    current_speed: Velocity,
    target_speed: Velocity,
) -> BurnDirection:
    if target_speed >= current_speed:
        return BurnDirection.PROGRADE

    return BurnDirection.RETROGRADE


# Subject: kinematics / astrodynamics.
# Computes scalar delta-v as the absolute difference between two speeds.
# This is basic manoeuvre physics and should probably live with astrodynamics/delta-v helpers.
def delta_v_between_speeds(
    first_speed: Velocity,
    second_speed: Velocity,
) -> DeltaV:
    return DeltaV(Velocity(Scalar(abs(second_speed - first_speed))))


# Subject: plotting adapter for transfer arcs.
# Normalises start/end eccentric anomaly values so Plotly draws the intended arc across the 2π wrap boundary.
# This is visualisation-specific handling of orbital angle data.
def transfer_arc_angles(
    start_eccentric_anomaly: EccentricAnomaly,
    arrival_eccentric_anomaly: EccentricAnomaly,
) -> tuple[float, float]:
    start = float(start_eccentric_anomaly)
    end = float(arrival_eccentric_anomaly)

    if end <= start:
        return start, end + 2 * math.pi

    return start, end


# Subject: visualisation scale conversion.
# Divides a numeric coordinate by distance_scale_km to convert physical coordinates into plot units.
# This is generic plotting-scale logic.
def scale_value(value: float | int, distance_scale_km: float) -> float:
    return float(value) / distance_scale_km


# Subject: visualisation scale conversion for 3D vectors.
# Divides x/y/z position components by distance_scale_km and rebuilds a Vector3D.
# This is a render-time coordinate scaling helper, not celestial mechanics.
def scale_position(position, distance_scale_km: float) -> Vector3D:
    return vector3d(
        scale_value(position.x, distance_scale_km),
        scale_value(position.y, distance_scale_km),
        scale_value(position.z, distance_scale_km),
    )


# Subject: data access / ephemeris query adapter.
# Calls the Horizons API wrapper for a target, centre, start time, and stop time derived from OrbitPlotSettings.
# This is not visualisation or mechanics; it is an IO/data-fetching adapter.
def get_horizon_state_vectors(
    target: HorizonsCommandTarget,
    settings: OrbitPlotSettings,
) -> list[StateVectors]:
    return get_object_state_vectors_from_horizon(
        target=target,
        centre=settings.centre,
        start_time=python_datetime_to_fulldate(settings.start_time),
        stop_time=python_datetime_to_fulldate(settings.stop_time),
    )


# Subject: visualisation plus orbit propagation.
# Generates orbit positions from OrbitalElements, scales them to plot units, and returns a Plotly 3D line trace.
# This mixes orbital propagation with Plotly rendering; ideally propagation happens outside and this function only receives coordinates.
def add_orbit_line_trace(
    name: str,
    orbital_elements: OrbitalElements,
    distance_scale_km: float,
    orbit_points: int,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> go.Scatter3d:
    x = []
    y = []
    z = []

    for position in generate_all_orbit_positions(
        orbital_elements,
        orbit_points,
        gravitational_parameter,
    ):
        scaled = scale_position(position, distance_scale_km)

        x.append(scaled.x)
        y.append(scaled.y)
        z.append(scaled.z)

    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=f"{name} orbit",
    )


# Subject: high-level 3D orbit visualisation orchestration.
# Fetches Horizons state vectors, converts them to orbital elements, propagates current/predicted states, and appends orbit/body Plotly traces.
# This heavily mixes ephemeris IO, celestial mechanics, propagation, scaling, and rendering. It is not a base helper.
def add_orbiting_body_to_traces(
    traces: list,
    body: BodyPlotConfig,
    settings: OrbitPlotSettings,
    opacity: float = 0.9,
) -> None:
    from afmaths.visualisations.helpers import add_body_surface

    horizon_state_vectors = get_horizon_state_vectors(
        HorizonsCommandTarget(body.target),
        settings,
    )

    if len(horizon_state_vectors) < 1:
        raise ValueError(f"No Horizons state vectors returned for {body.name}")

    orbital_elements = orbital_elements_from_state_vectors(
        horizon_state_vectors[0],
        gravitational_parameter=settings.gravitational_parameter,
    )

    model_current_state = orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements,
        Second(Scalar(0)),
        settings.gravitational_parameter,
    )

    traces.append(
        add_orbit_line_trace(
            body.name,
            orbital_elements,
            settings.distance_scale_km,
            settings.orbit_points,
            settings.gravitational_parameter,
        )
    )

    traces.append(
        add_body_surface(
            body.name,
            body.radius_km,
            body.radius_scale,
            settings.distance_scale_km,
            position=scale_position(
                model_current_state.position,
                settings.distance_scale_km,
            ),
            opacity=opacity,
        )
    )

    if not settings.add_prediction_to_orbit:
        return

    model_prediction_state = orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements,
        settings.time_offset_seconds,
        settings.gravitational_parameter,
    )

    traces.append(
        add_body_surface(
            body.name + " prediction",
            body.radius_km,
            body.radius_scale,
            settings.distance_scale_km,
            position=scale_position(
                model_prediction_state.position,
                settings.distance_scale_km,
            ),
            opacity=opacity,
        )
    )


# Subject: high-level visualisation composition.
# Builds a complete 3D orbit figure by creating the central body trace, adding each orbiting body, and applying the final 3D layout.
# This is a demo/figure-builder function, not core physics; it could stay in a specific 3D visualiser module.
def build_3d_orbit_figure(
    settings: OrbitPlotSettings,
    title: str,
    central_body_name: str,
    central_body_radius_km: float,
    central_body_radius_scale: float,
    orbiting_bodies: list[BodyPlotConfig],
    central_body_opacity: float = 0.7,
) -> go.Figure:
    from afmaths.visualisations.helpers import add_body_surface, make_3d_orbit_figure

    traces = [
        add_body_surface(
            central_body_name,
            central_body_radius_km,
            central_body_radius_scale,
            settings.distance_scale_km,
            opacity=central_body_opacity,
        )
    ]

    for body in orbiting_bodies:
        add_orbiting_body_to_traces(traces, body, settings)

    return make_3d_orbit_figure(
        traces,
        title,
        settings.distance_scale_km,
    )
