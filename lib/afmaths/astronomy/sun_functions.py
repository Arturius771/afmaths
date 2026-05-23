import math

from afmaths.astronomy.conversion_helpers import degrees_to_radians
from afmaths.astronomy.coordinate_functions import ecliptic_to_equatorial_coordinates
from afmaths.astronomy.time_functions import (
    greenwich_to_julian_date,
    local_civil_to_universal_time,
)
from astronomy_types import (
    Date,
    Day,
    Degrees,
    Eccentricity,
    EclipticCoordinates,
    EquatorialCoordinates,
    FullDate,
    Latitude,
    Longitude,
    Month,
    Radians,
    Ratio,
    Scalar,
    Year,
)


def sun_longitude(
    local_date: FullDate,
    daylight_savings_correction: int,
    timezone_correction: int,
) -> Longitude:
    def sun_mean_anomaly_2010(degrees: Degrees) -> float:
        ecliptic_longitude = 279.557208
        ecliptic_longitude_of_perigee = 283.112438

        return degrees + ecliptic_longitude - ecliptic_longitude_of_perigee

    def sun_true_anomaly_2010(mean_anomaly: Degrees) -> float:
        eccentricity = Eccentricity(Ratio(Scalar(0.016705)))

        return mean_anomaly + (
            (360 / math.pi) * eccentricity * math.sin(degrees_to_radians(mean_anomaly))
        )

    def sun_longitude_2010(true_anomaly_degrees: float) -> float:
        ecliptic_longitude_of_perigee = 283.112438

        return true_anomaly_degrees + ecliptic_longitude_of_perigee

    greenwich_date = local_civil_to_universal_time(
        local_date,
        daylight_savings_correction,
        timezone_correction,
    ).date

    julian_date = greenwich_to_julian_date(greenwich_date)

    epoch_date = greenwich_to_julian_date(
        Date(
            Year(2010),
            Month(1),
            Day(Scalar(0)),
        )
    )

    days_since_epoch = julian_date - epoch_date

    mean_longitude_degrees = Degrees(Scalar(360 * days_since_epoch / 365.242191))

    mean_anomaly = sun_mean_anomaly_2010(mean_longitude_degrees)
    mean_anomaly_corrected = Degrees(Scalar(mean_anomaly % 360))

    true_anomaly = sun_true_anomaly_2010(mean_anomaly_corrected)

    longitude_degrees = sun_longitude_2010(true_anomaly)
    longitude_degrees_corrected = Degrees(Scalar(longitude_degrees % 360))

    return Longitude(Radians(degrees_to_radians(longitude_degrees_corrected)))


def sun_position_approximate(
    local_date: FullDate,
    daylight_savings_correction: int,
    timezone_correction: int,
) -> EquatorialCoordinates:
    greenwich_date = local_civil_to_universal_time(
        local_date,
        daylight_savings_correction,
        timezone_correction,
    ).date

    longitude = sun_longitude(
        local_date,
        daylight_savings_correction,
        timezone_correction,
    )

    return ecliptic_to_equatorial_coordinates(
        EclipticCoordinates(
            Latitude(Radians(Scalar(0.0))),
            longitude,
        ),
        greenwich_date,
    )
