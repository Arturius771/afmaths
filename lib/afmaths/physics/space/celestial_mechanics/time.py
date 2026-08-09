import math

from astronomy_types import (
    Distance,
    GravitationalParameter,
    MeanAnomaly,
    MeanMotion,
    OrbitalElements,
    Rate,
    Scalar,
    SemiMajorAxis,
    SemiLatusRectum,
    Second,
    TrueAnomaly,
)

from afmaths.constants import EARTH_MU, SECONDS_PER_DAY
from afmaths.geometry.geometry import normalise_angle
from afmaths.operation import (
    CUBE,
    DOUBLE,
    SQUARE,
    divide_by,
    multiply,
    ratio,
    square_root,
)
from afmaths.physics.space.celestial_mechanics.celestial_mechanics import (
    kepler_equation,
    mean_motion,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    eccentric_anomaly_from_true_anomaly,
)
from afmaths.physics.space.type_conversion_helpers import make_radians


def orbital_period(a: SemiMajorAxis, mu: GravitationalParameter = EARTH_MU) -> Second:
    """Calculates the orbital period of an orbit from the semi major axis in seconds"""
    return DOUBLE(multiply(math.pi)(square_root(divide_by(mu)(CUBE(a)))))


def orbital_period_from_mean_motion(mean_motion_per_day: MeanMotion) -> Second:
    """Calculates the orbital period of an orbit from the mean motion in seconds"""
    return Second(Scalar(divide_by(mean_motion_per_day)(SECONDS_PER_DAY)))


def current_orbital_elapsed_period_from_epoch(
    epoch_elapsed_seconds: Second, orbital_period: Second
) -> Second:
    """Calculates the current orbital period elapsed from the epoch time and the orbital period."""
    return Second(Scalar(epoch_elapsed_seconds % orbital_period))


def time_to_true_anomaly(
    current_position: OrbitalElements,
    target_true_anomaly: TrueAnomaly,
) -> Second:
    """Calculates the time delta to reach a target true anomaly from the current position in the orbit."""

    # Mean anomaly at the target true anomaly
    M_delta = normalise_angle(
        make_radians(
            (
                float(
                    kepler_equation(
                        eccentric_anomaly_from_true_anomaly(
                            target_true_anomaly,
                            current_position.eccentricity,
                        ),
                        current_position.eccentricity,
                    )
                )
                - float(
                    kepler_equation(
                        eccentric_anomaly_from_true_anomaly(
                            current_position.true_anomaly,
                            current_position.eccentricity,
                        ),
                        current_position.eccentricity,
                    )
                )
            )
        )
    )

    return Second(
        Scalar(M_delta / float(mean_motion(current_position.semi_major_axis)))
    )


def rate_of_change_true_anomaly(
    p: SemiLatusRectum, mu: GravitationalParameter, r: Distance
) -> Rate:
    """Calculates the rate of change of the true anomaly for a given radius from periapsis. This is expressed in radians per second."""
    # MSE Excercise 1: dtheta/dt = (p/r^2) * sqrt(mu/p)

    return Rate(Scalar(multiply(divide_by(SQUARE(r))(1))(square_root(multiply(p)(mu)))))


def time_since_periapsis_from_mean_anomaly(
    a: SemiMajorAxis, mu: GravitationalParameter, mean_anomaly: MeanAnomaly
) -> Second:
    """Calculates the time delta for a given mean anomaly."""
    return Second(
        Scalar(
            multiply(orbital_period(a, mu))(ratio(float(mean_anomaly))(DOUBLE(math.pi)))
        )
    )
