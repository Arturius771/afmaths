import math
import unittest

from astronomy_types import (
    Altitude,
    Azimuth,
    Date,
    Day,
    Declination,
    Degrees,
    DMS,
    EclipticCoordinates,
    EquatorialCoordinates,
    EquatorialCoordinatesHourAngle,
    FullDate,
    GalacticCoordinates,
    HMS,
    HorizontalCoordinates,
    Hour,
    HourAngle,
    Minute,
    Month,
    Radians,
    RightAscension,
    Scalar,
    Second,
    Time,
    Year,
)

from afmaths.physics.space.type_conversion_helpers import (
    radians_from_degrees,
    radians_from_dms,
    radians_from_hms,
)
from afmaths.physics.space.astronomy.coordinate_functions import (
    equatorial_coordinates_from_ecliptic,
    ecliptic_coordinates_from_equatorial,
    galactic_coordinates_from_equatorial,
    horizontal_coordinates_from_equatorial,
    equatorial_coordinates_from_galactic,
    equatorial_coordinates_from_horizontal,
    right_ascension,
    mean_obliquity_ecliptic,
    hour_angle,
)


def make_date(year: int, month: int, day: float) -> Date:
    return Date(year=Year(year), month=Month(month), day=Day(Scalar(day)))


def make_time(hour: int, minute: int, second: float) -> Time:
    return Time(hour=Hour(hour), minute=Minute(minute), second=Second(Scalar(second)))


def assert_angle_degrees(
    test_case: unittest.TestCase,
    actual_radians: float,
    expected_degrees: float,
    places: int = 2,
) -> None:
    test_case.assertAlmostEqual(
        math.degrees(float(actual_radians)),
        expected_degrees,
        places=places,
    )


def dms_to_decimal(degrees: int, minutes: int, seconds: float) -> float:
    sign = -1 if degrees < 0 else 1
    return sign * (abs(degrees) + minutes / 60 + seconds / 3600)


def hms_to_decimal_hours(hours: int, minutes: int, seconds: float) -> float:
    return hours + minutes / 60 + seconds / 3600


class CoordinateTestMethods(unittest.TestCase):
    def test_decimal_degrees_to_degrees_minutes_seconds(self):
        result = Degrees(Scalar(182.52416666666667))

        self.assertAlmostEqual(result, 182.52416666666667, places=10)

    def test_degrees_minutes_seconds_to_decimal_degrees(self):
        degrees = Degrees(Scalar(182.52416666666667))

        self.assertAlmostEqual(
            float(degrees),
            182.52416666666667,
            places=10,
        )

    def test_right_ascension_to_hour_angle(self):
        full_date = FullDate(
            date=make_date(1980, 4, 22),
            time=make_time(14, 36, 51.67),
        )

        result = hour_angle(
            RightAscension(radians_from_hms(HMS(18, 32, 21))),
            full_date,
            0,
            -4,
            Radians(radians_from_degrees(Degrees(Scalar(-64)))),
        )

        self.assertAlmostEqual(
            math.degrees(float(result)) / 15,
            hms_to_decimal_hours(9, 52, 23.66),
            places=2,
        )

    def test_hour_angle_to_right_ascension(self):
        full_date = FullDate(
            date=make_date(1980, 4, 22),
            time=make_time(14, 36, 51.67),
        )

        result = right_ascension(
            HourAngle(radians_from_hms(HMS(9, 52, 23.66))),
            full_date,
            0,
            -4,
            Radians(radians_from_degrees(Degrees(Scalar(-64)))),
        )

        self.assertAlmostEqual(
            math.degrees(float(result)) / 15,
            hms_to_decimal_hours(18, 32, 21.0),
            places=2,
        )

    def test_equatorial_to_horizon_coordinates(self):
        coordinates = EquatorialCoordinatesHourAngle(
            Declination(radians_from_dms(DMS(23, 13, 10))),
            HourAngle(radians_from_hms(HMS(5, 51, 44))),
        )

        result = horizontal_coordinates_from_equatorial(
            coordinates,
            Radians(radians_from_degrees(Degrees(Scalar(52)))),
        )

        assert_angle_degrees(
            self,
            result.altitude,
            dms_to_decimal(19, 20, 3.64),
        )

        assert_angle_degrees(
            self,
            result.azimuth,
            dms_to_decimal(283, 16, 15.7),
        )

    def test_horizon_to_equatorial_coordinates(self):
        coordinates = HorizontalCoordinates(
            Altitude(radians_from_dms(DMS(19, 20, 3.64))),
            Azimuth(radians_from_dms(DMS(283, 16, 15.76))),
        )

        result = equatorial_coordinates_from_horizontal(
            coordinates,
            Radians(radians_from_degrees(Degrees(Scalar(52)))),
        )

        assert_angle_degrees(
            self,
            result.declination,
            dms_to_decimal(23, 13, 10.04),
        )

        self.assertAlmostEqual(
            math.degrees(float(result.hour_angle)) / 15,
            hms_to_decimal_hours(5, 51, 44.0),
            places=2,
        )

    def test_mean_obliquity_ecliptic(self):
        result = mean_obliquity_ecliptic(make_date(2009, 7, 6))

        assert_angle_degrees(self, result, 23.438055312466062, places=8)

    def test_ecliptic_to_equatorial_coordinates(self):
        coordinates = EclipticCoordinates(
            radians_from_dms(DMS(4, 52, 31)),
            radians_from_dms(DMS(139, 41, 10)),
        )

        result = equatorial_coordinates_from_ecliptic(
            coordinates,
            make_date(2009, 7, 6),
        )

        assert_angle_degrees(
            self,
            result.declination,
            dms_to_decimal(19, 32, 8.52),
        )

        self.assertAlmostEqual(
            math.degrees(float(result.right_ascension)) / 15,
            hms_to_decimal_hours(9, 34, 53.4),
            places=2,
        )

    def test_equatorial_to_ecliptic_coordinates(self):
        coordinates = EquatorialCoordinates(
            Declination(radians_from_dms(DMS(19, 32, 8.52))),
            RightAscension(radians_from_hms(HMS(9, 34, 53.4))),
        )

        result = ecliptic_coordinates_from_equatorial(
            coordinates,
            make_date(2009, 7, 6),
        )

        assert_angle_degrees(
            self,
            result.latitude,
            dms_to_decimal(4, 52, 30.99),
        )

        assert_angle_degrees(
            self,
            result.longitude,
            dms_to_decimal(139, 41, 10.25),
        )

    def test_equatorial_to_galactic_coordinates(self):
        coordinates = EquatorialCoordinates(
            Declination(radians_from_dms(DMS(10, 3, 11))),
            RightAscension(radians_from_hms(HMS(10, 21, 0))),
        )

        result = galactic_coordinates_from_equatorial(coordinates)

        assert_angle_degrees(
            self,
            result.latitude,
            dms_to_decimal(51, 7, 20.16),
        )

        assert_angle_degrees(
            self,
            result.longitude,
            dms_to_decimal(232, 14, 52.38),
        )

    def test_galactic_to_equatorial_coordinates(self):
        coordinates = GalacticCoordinates(
            radians_from_dms(DMS(51, 7, 20.16)),
            radians_from_dms(DMS(232, 14, 52.38)),
        )

        result = equatorial_coordinates_from_galactic(coordinates)

        assert_angle_degrees(
            self,
            result.declination,
            dms_to_decimal(10, 3, 11.0),
        )

        self.assertAlmostEqual(
            math.degrees(float(result.right_ascension)) / 15,
            hms_to_decimal_hours(10, 21, 0),
            places=2,
        )


if __name__ == "__main__":
    unittest.main()
