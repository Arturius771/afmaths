import math

from afmaths.space.astronomy.conversion_helpers import (
    degrees_to_radians,
    time_to_decimal_time,
)
from afmaths.space.astronomy.time_functions import (
    greenwich_sidereal_to_local_sidereal_time,
    greenwich_to_julian_date,
    julian_date_to_j2000,
    local_civil_to_universal_time,
    universal_to_greenwich_sidereal_time,
)
from astronomy_types import (
    Altitude,
    Azimuth,
    Date,
    Declination,
    Degrees,
    EclipticCoordinates,
    EquatorialCoordinates,
    EquatorialCoordinatesHourAngle,
    FullDate,
    GalacticCoordinates,
    HorizontalCoordinates,
    HourAngle,
    Latitude,
    Longitude,
    Obliquity,
    Radians,
    RightAscension,
    Scalar,
)


def right_ascension_to_hour_angle(
    right_ascension: RightAscension,
    local_date_and_time: FullDate,
    daylight_savings: int,
    zone_correction: int,
    longitude: Longitude,
) -> HourAngle:
    utc = local_civil_to_universal_time(
        local_date_and_time,
        daylight_savings,
        zone_correction,
    )

    gst = universal_to_greenwich_sidereal_time(utc)
    local_sidereal_time = greenwich_sidereal_to_local_sidereal_time(gst, longitude)

    lst_decimal = time_to_decimal_time(local_sidereal_time)
    right_ascension_hours = math.degrees(float(right_ascension)) / 15

    hour_angle_hours = (float(lst_decimal) - right_ascension_hours) % 24
    hour_angle_degrees = Degrees(Scalar(hour_angle_hours * 15))

    return HourAngle(degrees_to_radians(hour_angle_degrees))


def hour_angle_to_right_ascension(
    hour_angle: HourAngle,
    full_date: FullDate,
    daylight_savings: int,
    zone_correction: int,
    longitude: Longitude,
) -> RightAscension:
    utc = local_civil_to_universal_time(full_date, daylight_savings, zone_correction)
    gst = universal_to_greenwich_sidereal_time(utc)
    local_sidereal_time = greenwich_sidereal_to_local_sidereal_time(gst, longitude)

    lst_decimal = time_to_decimal_time(local_sidereal_time)
    hour_angle_hours = math.degrees(float(hour_angle)) / 15

    right_ascension_hours = (float(lst_decimal) - hour_angle_hours) % 24
    right_ascension_degrees = Degrees(Scalar(right_ascension_hours * 15))

    return RightAscension(Radians(degrees_to_radians(right_ascension_degrees)))


def equatorial_to_horizon_coordinates(
    equatorial_coordinates: EquatorialCoordinatesHourAngle,
    latitude: Latitude,
) -> HorizontalCoordinates:
    declination = float(equatorial_coordinates.declination)
    hour_angle = float(equatorial_coordinates.hour_angle)
    latitude_radians = float(latitude)

    sin_altitude = math.sin(declination) * math.sin(latitude_radians) + math.cos(
        declination
    ) * math.cos(latitude_radians) * math.cos(hour_angle)

    sin_altitude = max(-1.0, min(1.0, sin_altitude))

    altitude = math.asin(sin_altitude)

    y = -math.cos(declination) * math.cos(latitude_radians) * math.sin(hour_angle)
    x = math.sin(declination) - math.sin(latitude_radians) * sin_altitude

    azimuth = math.atan2(y, x) % (2 * math.pi)

    return HorizontalCoordinates(
        Altitude(Radians(Scalar(altitude))),
        Azimuth(Radians(Scalar(azimuth))),
    )


def horizon_to_equatorial_coordinates(
    horizontal_coordinates: HorizontalCoordinates,
    observer_latitude: Latitude,
) -> EquatorialCoordinatesHourAngle:
    sin_declination = math.sin(horizontal_coordinates.altitude) * math.sin(
        observer_latitude
    ) + math.cos(horizontal_coordinates.altitude) * math.cos(
        observer_latitude
    ) * math.cos(
        horizontal_coordinates.azimuth
    )

    sin_declination = max(-1.0, min(1.0, sin_declination))

    declination = math.asin(sin_declination)

    y = (
        -math.cos(horizontal_coordinates.altitude)
        * math.cos(observer_latitude)
        * math.sin(horizontal_coordinates.azimuth)
    )
    x = (
        math.sin(horizontal_coordinates.altitude)
        - math.sin(observer_latitude) * sin_declination
    )

    hour_angle = math.atan2(y, x) % (2 * math.pi)

    return EquatorialCoordinatesHourAngle(
        Declination(Radians(Scalar(declination))),
        HourAngle(Radians(Scalar(hour_angle))),
    )


def mean_obliquity_ecliptic(greenwich_date: Date) -> Obliquity:
    julian_date = greenwich_to_julian_date(greenwich_date)
    j2000 = julian_date_to_j2000(julian_date)

    t = float(j2000) / 36525
    de = (t * (46.815 + t * (0.0006 - (t * 0.00181)))) / 3600

    obliquity_degrees = Degrees(Scalar(23.439292 - de))

    return Obliquity(Radians(degrees_to_radians(obliquity_degrees)))


def ecliptic_to_equatorial_coordinates(
    ecliptic_coordinates: EclipticCoordinates,
    greenwich_date: Date,
) -> EquatorialCoordinates:
    ecliptic_latitude = float(ecliptic_coordinates.latitude)
    ecliptic_longitude = float(ecliptic_coordinates.longitude)

    obliquity = float(mean_obliquity_ecliptic(greenwich_date))

    # # TODO: CHECK Existing empirical correction retained from old code.
    obliquity += degrees_to_radians(Degrees(Scalar(0.001176447533936198)))

    sin_declination = math.sin(ecliptic_latitude) * math.cos(obliquity) + math.cos(
        ecliptic_latitude
    ) * math.sin(obliquity) * math.sin(ecliptic_longitude)

    sin_declination = max(-1.0, min(1.0, sin_declination))

    declination = Scalar(math.asin(sin_declination))

    y = math.sin(ecliptic_longitude) * math.cos(obliquity) - math.tan(
        ecliptic_latitude
    ) * math.sin(obliquity)
    x = math.cos(ecliptic_longitude)

    right_ascension = Scalar(math.atan2(y, x) % (2 * math.pi))

    return EquatorialCoordinates(
        Declination(Radians(declination)),
        RightAscension(Radians(right_ascension)),
    )


def equatorial_to_ecliptic_coordinates(
    equatorial_coordinates: EquatorialCoordinates,
    greenwich_date: Date,
) -> EclipticCoordinates:
    declination = float(equatorial_coordinates.declination)
    right_ascension = float(equatorial_coordinates.right_ascension)

    obliquity = float(mean_obliquity_ecliptic(greenwich_date))

    sin_ecliptic_latitude = math.sin(declination) * math.cos(obliquity) - math.cos(
        declination
    ) * math.sin(obliquity) * math.sin(right_ascension)

    sin_ecliptic_latitude = max(-1.0, min(1.0, sin_ecliptic_latitude))

    # Existing empirical correction retained from old code.
    ecliptic_latitude = math.asin(sin_ecliptic_latitude) - 1.3284561980173026e-05

    y = math.sin(right_ascension) * math.cos(obliquity) + math.tan(
        declination
    ) * math.sin(obliquity)
    x = math.cos(right_ascension)

    ecliptic_longitude = math.atan2(y, x) % (2 * math.pi)

    return EclipticCoordinates(
        Latitude(Radians(Scalar(ecliptic_latitude))),
        Longitude(Radians(Scalar(ecliptic_longitude))),
    )


def equatorial_to_galactic_coordinates(
    equatorial_coordinates: EquatorialCoordinates,
) -> GalacticCoordinates:
    declination = equatorial_coordinates.declination
    right_ascension = equatorial_coordinates.right_ascension

    pole_declination = degrees_to_radians(Degrees(Scalar(27.4)))
    pole_right_ascension = degrees_to_radians(Degrees(Scalar(192.25)))

    sin_galactic_latitude = math.cos(declination) * math.cos(
        pole_declination
    ) * math.cos(right_ascension - pole_right_ascension) + math.sin(
        declination
    ) * math.sin(
        pole_declination
    )

    sin_galactic_latitude = max(-1.0, min(1.0, sin_galactic_latitude))

    galactic_latitude = math.asin(sin_galactic_latitude)

    y = math.sin(declination) - (sin_galactic_latitude * math.sin(pole_declination))

    x = (
        math.cos(declination)
        * math.sin(right_ascension - pole_right_ascension)
        * math.cos(pole_declination)
    )

    galactic_longitude = degrees_to_radians(
        Degrees(Scalar((math.degrees(math.atan2(y, x)) + 33) % 360))
    )

    return GalacticCoordinates(
        Latitude(Radians(Scalar(galactic_latitude))),
        Longitude(Radians(Scalar(galactic_longitude))),
    )


def galactic_to_equatorial_coordinates(
    galactic_coordinates: GalacticCoordinates,
) -> EquatorialCoordinates:
    galactic_latitude = float(galactic_coordinates.latitude)
    galactic_longitude = float(galactic_coordinates.longitude)

    pole_declination = degrees_to_radians(Degrees(Scalar(27.4)))
    longitude_offset = degrees_to_radians(Degrees(Scalar(33)))

    sin_declination = math.cos(galactic_latitude) * math.cos(
        pole_declination
    ) * math.sin(galactic_longitude - longitude_offset) + math.sin(
        galactic_latitude
    ) * math.sin(
        pole_declination
    )

    sin_declination = max(-1.0, min(1.0, sin_declination))

    declination = math.asin(sin_declination)

    y = math.cos(galactic_latitude) * math.cos(galactic_longitude - longitude_offset)

    x = math.sin(galactic_latitude) * math.cos(pole_declination) - math.cos(
        galactic_latitude
    ) * math.sin(pole_declination) * math.sin(galactic_longitude - longitude_offset)

    right_ascension = degrees_to_radians(
        Degrees(Scalar((math.degrees(math.atan2(y, x)) + 192.25) % 360))
    )

    return EquatorialCoordinates(
        Declination(Radians(Scalar(declination))),
        RightAscension(right_ascension),
    )
