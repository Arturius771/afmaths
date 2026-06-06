import datetime
import math

from astronomy_types import (
    DMS,
    HMS,
    Date,
    Day,
    DecimalTime,
    Degrees,
    FullDate,
    Hour,
    Minute,
    Month,
    Radians,
    Scalar,
    Second,
    Time,
    Year,
)


def degrees_to_radians(value: Degrees) -> Radians:
    return Radians(Scalar(math.radians(float(value))))


def dms_to_degrees(value: DMS) -> Degrees:
    sign = -1 if value.degrees < 0 else 1
    return Degrees(
        Scalar(sign * (abs(value.degrees) + value.minutes / 60 + value.seconds / 3600))
    )


def dms_to_radians(value: DMS) -> Radians:
    return degrees_to_radians(dms_to_degrees(value))


def hms_to_degrees(value: HMS) -> Degrees:
    return Degrees(
        Scalar(15 * (value.hours + value.minutes / 60 + value.seconds / 3600))
    )


def hms_to_radians(value: HMS) -> Radians:
    return degrees_to_radians(hms_to_degrees(value))


def hours_to_degrees(hours: DecimalTime) -> Degrees:
    return Degrees(Scalar(float(hours) * 15))


def degrees_to_hours(degrees: Degrees) -> DecimalTime:
    return DecimalTime(Scalar(float(degrees) / 15))


def time_to_decimal_time(time: Time) -> DecimalTime:
    unsigned_decimal = (
        int(time.hour) + int(time.minute) / 60 + float(time.second) / 3600
    )

    return DecimalTime(Scalar(unsigned_decimal))


def decimal_time_to_time(decimal_value: DecimalTime) -> Time:
    unsigned_decimal = abs(float(decimal_value))

    total_seconds = unsigned_decimal * 3600
    rounded_seconds = round(total_seconds % 60, 2)

    seconds = 0 if rounded_seconds == 60 else rounded_seconds
    remainder = total_seconds + 60 if rounded_seconds == 60 else total_seconds

    minutes = math.floor(remainder / 60) % 60
    hours = math.floor(remainder / 3600)

    return Time(
        Hour(hours),
        Minute(minutes),
        Second(Scalar(seconds)),
    )


def make_date(year: Year, month: Month, day: Day) -> Date:
    return Date(year=Year(year), month=Month(month), day=Day(Scalar(day)))


def make_time(hms: HMS) -> Time:
    return Time(
        hour=Hour(hms.hours),
        minute=Minute(hms.minutes),
        second=Second(Scalar(hms.seconds)),
    )


def python_datetime_to_fulldate(date: datetime.datetime) -> FullDate:
    return FullDate(
        date=make_date(
            year=Year(date.year), month=Month(date.month), day=Day(Scalar(date.day))
        ),
        time=make_time(HMS(hours=date.hour, minutes=date.minute, seconds=date.second)),
    )


def fulldate_to_string(date: FullDate) -> str:
    return f"{date.date.year:04d}-{date.date.month:02d}-{date.date.day:02d} {date.time.hour:02d}:{date.time.minute:02d}:{date.time.second:02d}"


def python_timedelta_to_seconds(delta: datetime.timedelta) -> Second:
    return Second(Scalar(delta.total_seconds()))


def seconds_to_hours(seconds: Second) -> Hour:
    return Hour(int(round(float(seconds) / 3600)))


def hour_to_hour_string(hour: Hour) -> str:
    return f"{hour:02d}h"
