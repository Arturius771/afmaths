import math
import unittest

from astronomy_types import (
    Date,
    Day,
    Declination,
    Degrees,
    EclipticCoordinates,
    Epoch,
    EquatorialCoordinates,
    FullDate,
    GeographicCoordinates,
    HMS,
    Hour,
    JulianDate,
    Minute,
    Month,
    Radians,
    RightAscension,
    Scalar,
    Second,
    Time,
    Year,
    DMS,
)

from afmaths.physics.space.type_conversion_helpers import (
    radians_from_degrees,
    radians_from_dms,
    radians_from_hms,
)
from afmaths.physics.space.astronomy.coordinate_correction_functions import (
    aberration_from_date,
    angle_difference,
    nutation_from_date,
    precession_low_precision,
    rising_and_setting,
)


def assert_degrees_almost_equal(
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


def assert_time_almost_equal(
    test_case: unittest.TestCase,
    actual: Time,
    expected_hour: int,
    expected_minute: int,
    expected_second: float,
    places: int = 2,
) -> None:
    test_case.assertEqual(int(actual.hour), expected_hour)
    test_case.assertEqual(int(actual.minute), expected_minute)
    test_case.assertAlmostEqual(actual.second, expected_second, places=places)


class CoordinateCorrectionTestMethods(unittest.TestCase):
    def test_angle_difference(self):
        coordinates1 = EquatorialCoordinates(
            RightAscension(radians_from_hms(HMS(5, 13, 31.7))),
            Declination(radians_from_dms(DMS(-8, 13, 30))),
        )

        coordinates2 = EquatorialCoordinates(
            RightAscension(radians_from_hms(HMS(6, 44, 13.4))),
            Declination(radians_from_dms(DMS(-16, 41, 11))),
        )

        result = angle_difference(
            coordinates1,
            coordinates2,
        )

        self.assertAlmostEqual(float(result), 23.67385, places=2)

    def test_rising_and_setting(self):
        coordinates = EquatorialCoordinates(
            RightAscension(radians_from_hms(HMS(23, 39, 20))),
            Declination(radians_from_dms(DMS(21, 42, 0))),
        )

        location = GeographicCoordinates(
            Radians(radians_from_degrees(Degrees(Scalar(30)))),
            Radians(radians_from_degrees(Degrees(Scalar(64)))),
        )

        greenwich_date = Date(
            year=Year(2010),
            month=Month(8),
            day=Day(Scalar(24)),
        )

        result = rising_and_setting(
            coordinates,
            location,
            greenwich_date,
            Degrees(Scalar(0.5667)),
        )

        # TODO: Check this in book
        self.assertFalse(result.circumpolar)

        assert_time_almost_equal(
            self,
            result.rise_time,
            expected_hour=13,
            expected_minute=39,
            expected_second=47.14,
        )

        assert_time_almost_equal(
            self,
            result.set_time,
            expected_hour=9,
            expected_minute=17,
            expected_second=47.48,
        )
        assert_degrees_almost_equal(
            self,
            result.rise_azimuth,
            expected_degrees=30.25665473779737,
        )

        assert_degrees_almost_equal(
            self,
            result.set_azimuth,
            expected_degrees=329.7433452622026,
        )

    def test_precession_low_precision(self):
        coordinates = EquatorialCoordinates(
            RightAscension(radians_from_hms(HMS(9, 10, 43))),
            Declination(radians_from_dms(DMS(14, 23, 25))),
        )

        result = precession_low_precision(
            coordinates,
            Epoch(JulianDate(Scalar(2433282.423))),
            Epoch(JulianDate(Scalar(2444025.5))),
        )

        self.assertAlmostEqual(
            math.degrees(float(result.declination)),
            14.2692,
            places=3,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.right_ascension)) / 15,
            9.2056,
            places=3,
        )

    def test_nutation_from_date(self):
        result = nutation_from_date(
            Date(
                year=Year(1988),
                month=Month(9),
                day=Day(Scalar(1)),
            )
        )

        self.assertAlmostEqual(
            math.degrees(float(result.nutation_longitude)),
            0.0015258083552917808,
            places=8,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.nutation_obliquity)),
            0.0025671004471993584,
            places=8,
        )

    def test_aberration_from_date(self):
        full_date = FullDate(
            date=Date(
                year=Year(1988),
                month=Month(9),
                day=Day(Scalar(8)),
            ),
            time=Time(
                hour=Hour(0),
                minute=Minute(0),
                second=Second(Scalar(0)),
            ),
        )

        coordinates = EclipticCoordinates(
            radians_from_dms(DMS(352, 37, 10.1)),
            radians_from_dms(DMS(-1, 32, 56.4)),
        )

        result = aberration_from_date(
            full_date,
            coordinates,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.latitude)),
            -1.54898,
            places=2,
        )

        self.assertAlmostEqual(
            math.degrees(float(result.longitude)),
            352.62513,
            places=3,
        )


if __name__ == "__main__":
    unittest.main()
