import math
import unittest

from astronomy_types import (
    DMS,
    HMS,
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

from afmaths.astronomy.conversion_helpers import (
    dms_to_degrees,
    make_date,
    make_time,
    time_to_decimal_time,
)
from afmaths.astronomy.sun_functions import sun_position_approximate


class SunTestMethods(unittest.TestCase):
    def test_sun_position_approximate(self):
        local_date = FullDate(
            date=make_date(Year(2003), Month(7), Day(Scalar(27))),
            time=make_time(HMS(Hour(0), Minute(0), Second(Scalar(0)))),
        )

        result = sun_position_approximate(local_date, 0, 0)

        self.assertAlmostEqual(
            math.degrees(float(result.declination)),
            dms_to_degrees(DMS(19, 21, 13.81)),
            places=2,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.right_ascension)) / 15,
            time_to_decimal_time(Time(Hour(8), Minute(23), Second(Scalar(33.72)))),
            places=2,
        )


if __name__ == "__main__":
    unittest.main()
