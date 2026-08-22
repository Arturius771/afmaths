import math
import unittest

from astronomy_types import (
    DMS,
    HMS,
    Day,
    Degrees,
    FullDate,
    GeographicCoordinates,
    Hour,
    Latitude,
    Longitude,
    Minute,
    Month,
    Scalar,
    Second,
    Time,
    Year,
)

from afmaths.constants import KILCUMMIN_GROUND_STATION
from afmaths.physics.space.type_conversion_helpers import (
    degrees_from_dms,
    degrees_from_radians,
    make_date,
    make_time,
    decimal_time_from_time,
    radian_geographic_coordinates_from_degrees,
)
from afmaths.physics.space.astronomy.sun_functions import (
    sun_horizontal_coordinates,
    sun_equatorial_coordinates_approximate,
)


class SunTestMethods(unittest.TestCase):
    def test_sun_position_approximate(self):
        local_date = FullDate(
            date=make_date(Year(2003), Month(7), Day(Scalar(27))),
            time=make_time(HMS(Hour(0), Minute(0), Second(Scalar(0)))),
        )

        result = sun_equatorial_coordinates_approximate(local_date, Hour(0), Hour(0))

        self.assertAlmostEqual(
            math.degrees(float(result.declination)),
            degrees_from_dms(DMS(19, 21, 13.81)),
            places=2,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.right_ascension)) / 15,
            decimal_time_from_time(Time(Hour(8), Minute(23), Second(Scalar(33.72)))),
            places=2,
        )

    def test_sun_angle_at_local_time(self):

        local_date = FullDate(
            date=make_date(Year(2026), Month(8), Day(Scalar(22))),
            time=make_time(HMS(Hour(17), Minute(48), Second(Scalar(30)))),
        )
        result = sun_horizontal_coordinates(
            local_date,
            Hour(1),
            Hour(0),
            radian_geographic_coordinates_from_degrees(
                KILCUMMIN_GROUND_STATION.coordinates
            ),
        )

        self.assertAlmostEqual(
            degrees_from_radians(result.altitude),
            Degrees(Scalar(26.016421141391564)),
            places=2,
        )

        self.assertAlmostEqual(
            degrees_from_radians(result.azimuth),
            Degrees(Scalar(255.23537667354708)),
            places=2,
        )

        local_date = FullDate(
            date=make_date(Year(2026), Month(8), Day(Scalar(21))),
            time=make_time(HMS(Hour(11), Minute(30), Second(Scalar(30)))),
        )
        result = sun_horizontal_coordinates(
            local_date,
            Hour(1),
            Hour(0),
            radian_geographic_coordinates_from_degrees(
                KILCUMMIN_GROUND_STATION.coordinates
            ),
        )

        self.assertAlmostEqual(
            degrees_from_radians(result.altitude),
            Degrees(Scalar(42.42914751350768)),
            places=2,
        )

        self.assertAlmostEqual(
            degrees_from_radians(result.azimuth),
            Degrees(Scalar(135.10235215665736)),
            places=2,
        )


if __name__ == "__main__":
    unittest.main()
