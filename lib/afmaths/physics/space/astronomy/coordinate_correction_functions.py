import math

from afmaths.physics.space.astronomy.type_conversion_helpers import (
    decimal_time_to_time,
    degrees_to_radians,
)
from afmaths.physics.space.astronomy.time_functions import (
    greenwich_sidereal_to_universal_time,
    greenwich_to_julian_date,
    julian_date_to_epoch,
    local_sidereal_to_greenwich_sidereal_time,
)
from .sun_functions import sun_longitude
from astronomy_types import (
    Azimuth,
    Date,
    DecimalTime,
    Declination,
    Degrees,
    EclipticCoordinates,
    EquatorialCoordinates,
    FullDate,
    GeographicCoordinates,
    Longitude,
    NutationAndObliquity,
    Obliquity,
    RightAscension,
    RisingAndSetting,
    Scalar,
    Time,
    Epoch,
    Latitude,
    Second,
)


def angle_difference(
    object1_coordinates: EquatorialCoordinates,
    object2_coordinates: EquatorialCoordinates,
) -> Degrees:
    declination1 = float(object1_coordinates.declination)
    right_ascension1 = float(object1_coordinates.right_ascension)

    declination2 = float(object2_coordinates.declination)
    right_ascension2 = float(object2_coordinates.right_ascension)

    difference = right_ascension1 - right_ascension2

    cos_d = math.sin(declination1) * math.sin(declination2) + math.cos(
        declination1
    ) * math.cos(declination2) * math.cos(difference)

    cos_d = max(-1.0, min(1.0, cos_d))

    return Degrees(Scalar(math.degrees(math.acos(cos_d))))


def rising_and_setting(
    target_coordinates: EquatorialCoordinates,
    observer_coordinates: GeographicCoordinates,
    greenwich_date: Date,
    vertical_shift: Degrees,
) -> RisingAndSetting:
    """
    Calculates the target's rising time, setting time, rise azimuth and set azimuth.
    """
    declination = float(target_coordinates.declination)
    right_ascension_hours = math.degrees(float(target_coordinates.right_ascension)) / 15

    latitude = float(observer_coordinates.latitude)
    longitude = observer_coordinates.longitude

    vertical_shift_radians = degrees_to_radians(vertical_shift)

    cosine_ha = -(
        math.sin(vertical_shift_radians) + math.sin(latitude) * math.sin(declination)
    ) / (math.cos(latitude) * math.cos(declination))

    clamped_cosine_ha = max(-1.0, min(1.0, cosine_ha))

    hour_angle_degrees = math.degrees(math.acos(clamped_cosine_ha))
    hour_angle_hours = hour_angle_degrees / 15

    rise_lst = (right_ascension_hours - hour_angle_hours) % 24
    set_lst = (right_ascension_hours + hour_angle_hours) % 24

    azimuth_argument = (
        math.sin(declination) + math.sin(vertical_shift_radians) * math.sin(latitude)
    ) / (math.cos(vertical_shift_radians) * math.cos(latitude))

    azimuth_argument = max(-1.0, min(1.0, azimuth_argument))

    azimuth_angle_degrees = math.degrees(math.acos(azimuth_argument))

    rise_azimuth = Azimuth(
        degrees_to_radians(Degrees(Scalar(azimuth_angle_degrees % 360)))
    )
    set_azimuth = Azimuth(
        degrees_to_radians(Degrees(Scalar((360 - azimuth_angle_degrees) % 360)))
    )

    rise_greenwich_sidereal_time = local_sidereal_to_greenwich_sidereal_time(
        decimal_time_to_time(DecimalTime(Scalar(rise_lst))),
        longitude,
    )

    set_greenwich_sidereal_time = local_sidereal_to_greenwich_sidereal_time(
        decimal_time_to_time(DecimalTime(Scalar(set_lst))),
        longitude,
    )

    rise_full_date = FullDate(
        date=greenwich_date,
        time=rise_greenwich_sidereal_time,
    )

    set_full_date = FullDate(
        date=greenwich_date,
        time=set_greenwich_sidereal_time,
    )

    rise_ut = greenwich_sidereal_to_universal_time(rise_full_date).time
    set_ut = greenwich_sidereal_to_universal_time(set_full_date).time

    rise_time_adjusted = Time(
        rise_ut.hour,
        rise_ut.minute,
        Second(Scalar(rise_ut.second + 0.008333)),
    )

    set_time_adjusted = Time(
        set_ut.hour,
        set_ut.minute,
        Second(Scalar(set_ut.second + 0.008333)),
    )

    circumpolar = cosine_ha < -1

    return RisingAndSetting(
        circumpolar=circumpolar,
        rise_time=rise_time_adjusted,
        set_time=set_time_adjusted,
        rise_azimuth=rise_azimuth,
        set_azimuth=set_azimuth,
    )


def precession_low_precision(
    equatorial_coordinates: EquatorialCoordinates,
    original_epoch: Epoch,
    new_epoch: Epoch,
) -> EquatorialCoordinates:
    """
    Calculates low-precision precession between two epochs.
    """
    declination1 = float(equatorial_coordinates.declination)
    right_ascension1 = float(equatorial_coordinates.right_ascension)

    t_centuries = float(julian_date_to_epoch(original_epoch, -2415020.5)) / 36525

    m = 3.07234 + (0.00186 * t_centuries)
    n = 20.0468 - (0.0085 * t_centuries)

    n_years = float(julian_date_to_epoch(new_epoch, -float(original_epoch))) / 365.25

    right_ascension_hours = math.degrees(right_ascension1) / 15
    right_ascension_degrees = math.degrees(right_ascension1)
    declination_degrees = math.degrees(declination1)

    s1 = (
        (m + (n * math.sin(right_ascension1) * math.tan(declination1) / 15)) * n_years
    ) / 3600

    s2 = (n * math.cos(right_ascension1) * n_years) / 3600

    new_right_ascension_degrees = Degrees(
        Scalar((right_ascension_degrees + s1 * 15) % 360)
    )
    new_declination_degrees = Degrees(Scalar(declination_degrees + s2))

    return EquatorialCoordinates(
        Declination(degrees_to_radians(new_declination_degrees)),
        RightAscension(degrees_to_radians(new_right_ascension_degrees)),
    )


def nutation_from_date(greenwich_date: Date) -> NutationAndObliquity:
    """
    Calculates nutation in longitude and nutation in obliquity for a Greenwich date.
    """
    julian_date = greenwich_to_julian_date(greenwich_date)
    t_centuries = float(julian_date_to_epoch(julian_date, -2415020)) / 36525

    a = 100.0021358 * t_centuries
    l1 = 279.6967 + (0.000303 * t_centuries**2)
    l2 = l1 + 360 * (a - math.floor(a))
    l3 = l2 % 360
    l4 = degrees_to_radians(Degrees(Scalar(l3)))

    b = 5.372617 * t_centuries
    n1 = 259.1833 - 360 * (b - math.floor(b))
    n2 = n1 % 360
    n3 = degrees_to_radians(Degrees(Scalar(n2)))

    nutation_longitude_degrees = Degrees(
        Scalar((-17.2 * math.sin(n3) - 1.3 * math.sin(2 * l4)) / 3600)
    )

    nutation_obliquity_degrees = Degrees(
        Scalar((9.2 * math.cos(n3) + 0.5 * math.cos(2 * l4)) / 3600)
    )

    return NutationAndObliquity(
        nutation_longitude=Longitude(degrees_to_radians(nutation_longitude_degrees)),
        nutation_obliquity=Obliquity(degrees_to_radians(nutation_obliquity_degrees)),
    )


def aberration_from_date(
    ut_date: FullDate,
    true_ecliptic_coordinates: EclipticCoordinates,
) -> EclipticCoordinates:
    """
    Calculates apparent ecliptic coordinates after applying annual aberration.
    """
    true_latitude = float(true_ecliptic_coordinates.latitude)
    true_longitude = float(true_ecliptic_coordinates.longitude)

    true_latitude_degrees = Degrees(Scalar(math.degrees(true_latitude)))
    true_longitude_degrees = Degrees(Scalar(math.degrees(true_longitude)))

    sun_longitude_degrees = Degrees(
        Scalar(math.degrees(float(sun_longitude(ut_date, 0, 0))))
    )

    delta_longitude_arcseconds = (
        -20.5
        * math.cos(
            degrees_to_radians(
                Degrees(Scalar(sun_longitude_degrees - true_longitude_degrees))
            )
        )
        / math.cos(degrees_to_radians(Degrees(true_latitude_degrees)))
    )

    delta_latitude_arcseconds = (
        -20.5
        * math.sin(
            degrees_to_radians(
                Degrees(Scalar(sun_longitude_degrees - true_longitude_degrees))
            )
        )
        * math.sin(degrees_to_radians(Degrees(true_latitude_degrees)))
    )

    apparent_longitude_degrees = Degrees(
        Scalar((true_longitude_degrees + delta_longitude_arcseconds / 3600))
    )

    apparent_latitude_degrees = Degrees(
        Scalar(true_latitude_degrees + delta_latitude_arcseconds / 3600)
    )

    return EclipticCoordinates(
        Latitude(degrees_to_radians(apparent_latitude_degrees)),
        Longitude(degrees_to_radians(apparent_longitude_degrees)),
    )
