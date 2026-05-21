import math
import unittest

from astronomy_types import (
    Date,
    Day,
    FullDate,
    Hour,
    Minute,
    Month,
    Scalar,
    Second,
    Time,
    Year,
)

from afmaths.astronomy.sun_functions import sun_position_approximate


def make_date(year: int, month: int, day: float) -> Date:
    return Date(year=Year(year), month=Month(month), day=Day(Scalar(day)))


def make_time(hour: int, minute: int, second: float) -> Time:
    return Time(hour=Hour(hour), minute=Minute(minute), second=Second(Scalar(second)))


def hms_to_decimal_hours(hours: int, minutes: int, seconds: float) -> float:
    return hours + minutes / 60 + seconds / 3600


def dms_to_decimal_degrees(degrees: int, minutes: int, seconds: float) -> float:
    sign = -1 if degrees < 0 else 1
    return sign * (abs(degrees) + minutes / 60 + seconds / 3600)


class SunTestMethods(unittest.TestCase):
    def test_sun_position_approximate(self):
        local_date = FullDate(
            date=make_date(2003, 7, 27),
            time=make_time(0, 0, 0),
        )

        result = sun_position_approximate(local_date, 0, 0)

        self.assertAlmostEqual(
            math.degrees(float(result.declination)),
            dms_to_decimal_degrees(19, 21, 13.81),
            places=2,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.right_ascension)) / 15,
            hms_to_decimal_hours(8, 23, 33.72),
            places=2,
        )


if __name__ == "__main__":
    unittest.main()
