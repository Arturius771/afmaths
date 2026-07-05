from dataclasses import replace

from astronomy_types import (
    Distance,
    EccentricAnomaly,
    Eccentricity,
    GravitationalParameter,
    OrbitalElements,
    Ratio,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
)
from afmaths.constants import (
    EARTH_MU_KM_CUBED,
)
from afmaths.physics.space.engineering.astrodynamics.maneuvers import delta_v
from afmaths.types import OrbitalDirection, DeltaV

from afmaths.operation import (
    DOUBLE,
    subtract,
)

from afmaths.physics.space.celestial_mechanics import (
    apoapsis_radius,
    eccentric_anomaly_from_true_anomaly,
    eccentricity_from_apsides,
    kepler_equation,
    orbital_period,
    periapsis_radius,
    semi_major_axis_from_period,
    time_since_periapsis,
    vis_viva,
)


def phase_angle_time(
    E_phase_orbit: EccentricAnomaly,
    original_orbit: OrbitalElements,
    mu: GravitationalParameter,
) -> Second:
    return time_since_periapsis(
        original_orbit.semi_major_axis,
        mu,
        kepler_equation(E_phase_orbit, original_orbit.eccentricity),
    )


def phase_period(original_period: Second, phase_angle_time: Second) -> Second:
    """
    Return the phase orbit period.

    Positive phase_angle_time means move ahead, so the phase period is shorter.
    Negative phase_angle_time means fall behind, so the phase period is longer.
    """
    return subtract(phase_angle_time)(original_period)


def phase_semi_major_axis(
    original_orbit: OrbitalElements,
    true_anomaly_delta: TrueAnomaly,
    mu: GravitationalParameter,
) -> SemiMajorAxis:
    return semi_major_axis_from_period(
        phase_period(
            orbital_period(original_orbit.semi_major_axis, mu),
            phase_angle_time(
                eccentric_anomaly_from_true_anomaly(
                    true_anomaly_delta,
                    original_orbit.eccentricity,
                ),
                original_orbit,
                mu,
            ),
        ),
        mu,
    )


def phase_apsides(
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


def phase_periapsis(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    periapsis, _ = phase_apsides(phase_semi_major_axis, original_orbit)
    return periapsis


def phase_apoapsis(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Distance:
    _, apoapsis = phase_apsides(phase_semi_major_axis, original_orbit)
    return apoapsis


def phase_eccentricity(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
) -> Eccentricity:

    periapsis, apoapsis = phase_apsides(phase_semi_major_axis, original_orbit)

    return Eccentricity(
        Ratio(Scalar(abs(eccentricity_from_apsides(periapsis, apoapsis))))
    )


def phase_poi_radius(
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


def phase_delta_v(
    phase_semi_major_axis: SemiMajorAxis,
    original_orbit: OrbitalElements,
    mu: GravitationalParameter,
) -> DeltaV:
    poi = phase_poi_radius(phase_semi_major_axis, original_orbit)

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


def phase_orbit(
    original_orbit: OrbitalElements,
    true_anomaly_delta: TrueAnomaly,
    mu: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, DeltaV, OrbitalElements]:
    """Returns the Point of Impulse (POI) DeltaV, total DeltaV, and phase orbital elements."""

    p_a = phase_semi_major_axis(original_orbit, true_anomaly_delta, mu)

    # This is the delta v to get from one orbit to the other, so half of the total required.
    poi_delta_v = phase_delta_v(p_a, original_orbit, mu)

    return (
        poi_delta_v,  # DeltaV to move orbit
        DOUBLE(poi_delta_v),  # Total DeltaV
        replace(
            original_orbit,
            semi_major_axis=p_a,
            eccentricity=phase_eccentricity(p_a, original_orbit),
        ),
    )
