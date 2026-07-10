import math
from astronomy_types import (
    Date,
    Day,
    DaysOfWeek,
    DecimalTime,
    Epoch,
    FullDate,
    Hour,
    JulianDate,
    Longitude,
    Minute,
    Month,
    Scalar,
    Second,
    Time,
    Year,
)

from afmaths.operation import is_divisible
from afmaths.physics.space.type_conversion_helpers import (
    time_from_decimal_time,
    decimal_time_from_time,
)


def date_of_easter(year: Year) -> Date:
    year_int = int(year)

    a = year_int % 19
    b = math.floor(year_int / 100)
    c = year_int % 100
    d = math.floor(b / 4)
    e = b % 4
    f = math.floor((b + 8) / 25)
    g = math.floor((b - f - 1) / 3)
    h = ((19 * a) + b - d - g + 15) % 30
    i = math.floor(c / 4)
    k = c % 4
    l = (32 + (2 * e) + (2 * i) - h - k) % 7
    m = math.floor((a + (11 * h) + (22 * l)) / 451)

    month = math.floor((h + l - (7 * m) + 114) / 31)
    day = ((h + l - (7 * m) + 114) % 31) + 1

    return Date(
        year=year,
        month=Month(month),
        day=Day(Scalar(day)),
    )


def day_number_from_date(date: Date) -> int:
    """Converts a date to the day number of the year."""
    year = date.year
    month = int(date.month)
    day = float(date.day)

    if month > 2:
        j = math.floor((month + 1) * 30.6)
        k = j - 62 if year_is_leap(year) else j - 63

        return int(k + day)

    d = (month - 1) * 62 if year_is_leap(year) else (month - 1) * 63
    f = math.floor(d / 2)

    return int(f + day)


def year_is_leap(year: Year) -> bool:
    """Determines if a given year is a leap year."""
    year_int = int(year)

    return is_divisible(year_int, 4) and (
        not is_divisible(year_int, 100) or is_divisible(year_int, 400)
    )


def julian_date_from_greenwich(date: Date) -> JulianDate:
    # TODO: update to take h:m:s
    year = int(date.year)
    month = int(date.month)
    day = float(date.day)

    if month in (1, 2):
        y = year - 1
        m = month + 12
    else:
        y = year
        m = month

    if (
        year > 1582
        or (year == 1582 and month > 10)
        or (year == 1582 and month == 10 and day > 15)
    ):
        a = math.floor(y / 100)
        b = 2 - a + math.floor(a / 4)
    else:
        b = 0

    c = math.floor((365.25 * y) - 0.75) if y < 0 else math.floor(365.25 * y)
    d = math.floor(30.6001 * (m + 1))

    return JulianDate(Scalar(b + c + d + day + 1720994.5))


def greenwich_date_from_julian(julian_date: JulianDate) -> Date:
    jd = float(julian_date) + 0.5
    i = math.floor(jd)
    f = jd - i

    if i > 2299160:
        a = math.floor((i - 1867216.25) / 36524.25)
        b = i + a - math.floor(a / 4) + 1
    else:
        b = i

    c = b + 1524
    d = math.floor((c - 122.1) / 365.25)
    e = math.floor(365.25 * d)
    g = math.floor((c - e) / 30.6001)

    day = c - e + f - math.floor(30.6001 * g)
    month = g - 1 if g < 13.5 else g - 13
    year = d - 4716 if month > 2.5 else d - 4715

    return Date(
        year=Year(year),
        month=Month(month),
        day=Day(Scalar(day)),
    )


def j200_from_julian_Date(julian_date: JulianDate) -> Epoch:
    return epoch_from_julian_date(julian_date, -2451545.0)


def epoch_from_julian_date(julian_date: JulianDate, adjustment: float) -> Epoch:
    return Epoch(JulianDate(Scalar(julian_date + adjustment)))


def finding_day_of_week(julian_date: JulianDate) -> DaysOfWeek:
    julian_day = (float(julian_date) + 1.5) % 7
    day_number = math.floor(julian_day)

    days = [
        DaysOfWeek.Sunday,
        DaysOfWeek.Monday,
        DaysOfWeek.Tuesday,
        DaysOfWeek.Wednesday,
        DaysOfWeek.Thursday,
        DaysOfWeek.Friday,
        DaysOfWeek.Saturday,
    ]

    return days[day_number]


def decimal_time_from_hms(
    time: Time,
    twenty_four_hour_clock: bool = True,
) -> DecimalTime:
    decimal_time = decimal_time_from_time(time)

    if twenty_four_hour_clock or decimal_time <= 12:
        return DecimalTime(decimal_time)

    return DecimalTime(Scalar(decimal_time - 12))


def hms_from_decimal(decimal_time: DecimalTime) -> Time:
    hours, minutes, seconds = (
        time_from_decimal_time(decimal_time).hour,
        time_from_decimal_time(decimal_time).minute,
        time_from_decimal_time(decimal_time).second,
    )

    if float(decimal_time) < 0:
        hours = -hours

    return Time(
        hour=Hour(hours),
        minute=Minute(minutes),
        second=Second(seconds),
    )


def universal_time_from_local_civil(
    local_time_and_date: FullDate,
    daylight_savings_correction: int = 0,
    timezone_offset_correction: int = 0,
) -> FullDate:
    local_date = local_time_and_date.date
    local_time = local_time_and_date.time

    zone_hour = int(local_time.hour) - daylight_savings_correction

    decimal_zone_time = decimal_time_from_hms(
        Time(
            hour=Hour(zone_hour),
            minute=local_time.minute,
            second=local_time.second,
        )
    )

    universal_time = float(decimal_zone_time) - timezone_offset_correction
    greenwich_calendar_day = float(local_date.day) + (universal_time / 24)

    julian_date = julian_date_from_greenwich(
        Date(
            local_date.year,
            local_date.month,
            Day(Scalar(greenwich_calendar_day)),
        )
    )

    greenwich_date = greenwich_date_from_julian(julian_date)

    utc = hms_from_decimal(
        DecimalTime(
            Scalar(24 * (greenwich_calendar_day - math.floor(greenwich_calendar_day)))
        )
    )

    return FullDate(
        date=Date(
            greenwich_date.year,
            greenwich_date.month,
            Day(Scalar(math.floor(greenwich_date.day))),
        ),
        time=utc,
    )


def universal_to_local_civil_time(
    universal_time_and_date: FullDate,
    timezone_offset_correction: int = 0,
    daylight_savings_correction: int = 0,
) -> FullDate:
    greenwich_date = universal_time_and_date.date
    utc = universal_time_and_date.time

    decimal_hours = decimal_time_from_hms(utc)
    local_civil_time = (
        float(decimal_hours) + timezone_offset_correction + daylight_savings_correction
    )

    julian_date = julian_date_from_greenwich(greenwich_date)
    local_julian_date = JulianDate(Scalar(julian_date + (local_civil_time / 24)))

    local_date = greenwich_date_from_julian(local_julian_date)
    integer_day = math.floor(local_date.day)

    local_time = hms_from_decimal(
        DecimalTime(Scalar((local_date.day - integer_day) * 24))
    )

    return FullDate(
        date=Date(
            year=local_date.year,
            month=local_date.month,
            day=Day(Scalar(integer_day)),
        ),
        time=local_time,
    )


def greenwich_sidereal_time_from_universal(universal_time_and_date: FullDate) -> Time:
    date = universal_time_and_date.date
    time = universal_time_and_date.time

    julian_date = julian_date_from_greenwich(date)
    s = j200_from_julian_Date(julian_date)
    t = float(s) / 36525.0

    t0 = 6.697374558 + (2400.051336 * t) + (0.000025862 * t**2)
    t1 = t0 % 24

    universal_time = decimal_time_from_hms(time)
    gst = (float(universal_time) * 1.002737909 + t1) % 24

    return hms_from_decimal(DecimalTime(Scalar(gst)))


def universal_time_from_greenwich(
    greenwich_date_and_sidereal_time: FullDate,
) -> FullDate:
    greenwich_date = greenwich_date_and_sidereal_time.date
    greenwich_sidereal_time = greenwich_date_and_sidereal_time.time

    julian_date = julian_date_from_greenwich(greenwich_date)
    s = j200_from_julian_Date(julian_date)
    t = s / 36525.0

    t0 = 6.697374558 + (2400.051336 * t) + (0.000025862 * t**2)
    t1 = t0 % 24

    gst_decimal = decimal_time_from_hms(greenwich_sidereal_time)
    universal_time = ((gst_decimal - t1) % 24) * 0.9972695663

    utc = hms_from_decimal(DecimalTime(Scalar(universal_time)))

    return FullDate(
        date=greenwich_date,
        time=utc,
    )


def local_sidereal_time_from_greenwich_sidereal(
    greenwich_sidereal_time: Time,
    longitude: Longitude,
) -> Time:
    gst_decimal = decimal_time_from_hms(greenwich_sidereal_time)

    longitude_degrees = math.degrees(float(longitude))
    offset_hours = longitude_degrees / 15

    local_sidereal_time = (float(gst_decimal) + offset_hours) % 24

    return hms_from_decimal(DecimalTime(Scalar(local_sidereal_time)))


def greenwich_sidereal_time_from_local_sidereal(
    local_sidereal_time: Time,
    longitude: Longitude,
) -> Time:
    lst_decimal = decimal_time_from_hms(local_sidereal_time)

    longitude_degrees = math.degrees(float(longitude))
    offset_hours = longitude_degrees / 15

    greenwich_sidereal_time = (float(lst_decimal) - offset_hours) % 24

    return hms_from_decimal(DecimalTime(Scalar(greenwich_sidereal_time)))
