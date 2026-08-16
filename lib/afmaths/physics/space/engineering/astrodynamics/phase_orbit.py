from dataclasses import replace

from astronomy_types import (
    Anomaly,
    Distance,
    EccentricAnomaly,
    Eccentricity,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Ratio,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
)
from afmaths.constants import (
    EARTH_MU,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    eccentric_anomaly_from_true_anomaly,
    eccentricity_from_apsides,
    semi_major_axis_from_period,
)
from afmaths.physics.space.celestial_mechanics.time import (
    orbital_period,
    time_to_eccentric_anomaly,
)
from afmaths.physics.space.engineering.astrodynamics.maneuvers import delta_v
from afmaths.afmath_types import DeltaV

from afmaths.operation import (
    DOUBLE,
    subtract,
)

from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    apoapsis_radius,
    periapsis_radius,
    vis_viva,
)


def phase_period(original_period: Second, phase_angle_time: Second) -> Second:
    """
    Return the phase orbit period.

    Positive phase_angle_time means move ahead, so the phase period is shorter.
    Negative phase_angle_time means fall behind, so the phase period is longer.
    """
    return subtract(phase_angle_time)(original_period)


def phase_orbit_semi_major_axis(
    original_orbit: OrbitalElements,
    target_true_anomaly: TrueAnomaly,
    mu: GravitationalParameter,
) -> SemiMajorAxis:
    """Returns the semi-major axis of the phase orbit."""
    return semi_major_axis_from_period(
        phase_period(
            orbital_period(original_orbit.semi_major_axis, mu),
            time_to_eccentric_anomaly(
                eccentric_anomaly_from_true_anomaly(
                    phase_true_anomaly_delta(
                        original_orbit.true_anomaly, target_true_anomaly
                    ),
                    original_orbit.eccentricity,
                ),
                original_orbit,
                mu,
            ),
        ),
        mu,
    )


def phase_orbit_apsides(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> tuple[Distance, Distance]:
    """Return phase orbit periapsis and apoapsis."""
    two_a = DOUBLE(phase_semi_major_axis)

    if phase_semi_major_axis > original_orbit.semi_major_axis:
        # Higher / longer-period phase orbit:
        # original periapsis is shared with phase periapsis.
        periapsis = periapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )
        apoapsis = subtract(periapsis)(two_a)  # 2a - rp
    else:
        # Lower / shorter-period phase orbit:
        # original apoapsis is shared with phase apoapsis.
        apoapsis = apoapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )
        periapsis = subtract(apoapsis)(two_a)  # 2a - ra

    return periapsis, apoapsis


def phase_orbit_periapsis(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    """Returns the periapsis of the phase orbit."""
    periapsis, _ = phase_orbit_apsides(phase_semi_major_axis, original_orbit)
    return periapsis


def phase_orbit_apoapsis(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    """Returns the apoapsis of the phase orbit."""
    _, apoapsis = phase_orbit_apsides(phase_semi_major_axis, original_orbit)
    return apoapsis


def phase_orbit_eccentricity(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Eccentricity:
    """Returns the eccentricity of the phase orbit."""

    periapsis, apoapsis = phase_orbit_apsides(phase_semi_major_axis, original_orbit)

    return Eccentricity(
        Ratio(Scalar(abs(eccentricity_from_apsides(periapsis, apoapsis))))
    )


def phase_orbit_poi_radius(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    """Returns the Point of Impulse (POI), which is either the apoapsis or periapsis of the original orbit."""
    if phase_semi_major_axis > original_orbit.semi_major_axis:
        return periapsis_radius(
            original_orbit.semi_major_axis,
            original_orbit.eccentricity,
        )

    return apoapsis_radius(
        original_orbit.semi_major_axis,
        original_orbit.eccentricity,
    )


def phase_orbit_delta_v(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
    mu: GravitationalParameter,
) -> DeltaV:
    """Returns the Point of Impulse (POI) DeltaV required to transfer from the original orbit to the phase orbit."""
    poi = phase_orbit_poi_radius(phase_semi_major_axis, original_orbit)

    original_velocity = vis_viva(
        mu,
        poi,
        original_orbit.semi_major_axis,
    )

    phase_velocity = vis_viva(
        mu,
        poi,
        phase_semi_major_axis,
    )

    return delta_v(original_velocity, phase_velocity)


def phase_true_anomaly_delta(
    initial_true_anomaly: TrueAnomaly,
    desired_true_anomaly: TrueAnomaly,
) -> TrueAnomaly:
    """
    Return the signed phase true-anomaly delta.
    """
    delta = desired_true_anomaly - initial_true_anomaly
    if delta < Radians(Scalar(0.0)):
        delta -= Radians(Scalar(2 * 3.141592653589793))

    return TrueAnomaly(Anomaly(Radians(Scalar(delta))))


def phase_orbit_parameters(
    original_orbit: OrbitalElements,
    target_true_anomaly: TrueAnomaly,
    mu: GravitationalParameter = EARTH_MU,
) -> tuple[DeltaV, DeltaV, OrbitalElements]:
    """Returns the Point of Impulse (POI) DeltaV, total DeltaV, and phase orbital elements."""

    p_a = phase_orbit_semi_major_axis(original_orbit, target_true_anomaly, mu)

    # This is the delta v to get from one orbit to the other, so half of the total required.
    poi_delta_v = phase_orbit_delta_v(p_a, original_orbit, mu)

    return (
        poi_delta_v,  # DeltaV to move orbit
        DOUBLE(poi_delta_v),  # Total DeltaV
        replace(
            original_orbit,
            semi_major_axis=p_a,
            eccentricity=phase_orbit_eccentricity(p_a, original_orbit),
        ),
    )
