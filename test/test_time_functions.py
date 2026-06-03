import unittest

from astronomy_types import (
    Date,
    Day,
    DaysOfWeek,
    DecimalTime,
    Degrees,
    FullDate,
    Hour,
    JulianDate,
    Longitude,
    Minute,
    Month,
    Radians,
    Scalar,
    Second,
    Time,
    Year,
)

from afmaths.physics.space.astronomy.conversion_helpers import degrees_to_radians
from afmaths.physics.space.astronomy.time_functions import (
    date_of_easter,
    date_to_day_number,
    decimal_hours_to_hours_minutes_seconds,
    finding_day_of_week,
    greenwich_sidereal_to_local_sidereal_time,
    greenwich_sidereal_to_universal_time,
    greenwich_to_julian_date,
    hours_minutes_seconds_to_decimal_time,
    julian_date_to_j2000,
    julian_to_greenwich_date,
    local_civil_to_universal_time,
    local_sidereal_to_greenwich_sidereal_time,
    universal_to_greenwich_sidereal_time,
    universal_to_local_civil_time,
    year_is_leap,
)


def make_date(year: int, month: int, day: float) -> Date:
    return Date(year=Year(year), month=Month(month), day=Day(Scalar(day)))


def make_time(hour: int, minute: int, second: float) -> Time:
    return Time(hour=Hour(hour), minute=Minute(minute), second=Second(Scalar(second)))


def make_full_date(
    year: int,
    month: int,
    day: float,
    hour: int,
    minute: int,
    second: float,
) -> FullDate:
    return FullDate(
        date=make_date(year, month, day),
        time=make_time(hour, minute, second),
    )


def assert_date_equal(
    test_case: unittest.TestCase,
    actual: Date,
    expected_year: int,
    expected_month: int,
    expected_day: float,
    places: int = 8,
) -> None:
    test_case.assertEqual(int(actual.year), expected_year)
    test_case.assertEqual(int(actual.month), expected_month)
    test_case.assertAlmostEqual(float(actual.day), expected_day, places=places)


def assert_time_equal(
    test_case: unittest.TestCase,
    actual: Time,
    expected_hour: int,
    expected_minute: int,
    expected_second: float,
    places: int = 2,
) -> None:
    test_case.assertEqual(int(actual.hour), expected_hour)
    test_case.assertEqual(int(actual.minute), expected_minute)
    test_case.assertAlmostEqual(float(actual.second), expected_second, places=places)


def assert_full_date_equal(
    test_case: unittest.TestCase,
    actual: FullDate,
    expected_year: int,
    expected_month: int,
    expected_day: float,
    expected_hour: int,
    expected_minute: int,
    expected_second: float,
    date_places: int = 8,
    time_places: int = 2,
) -> None:
    assert_date_equal(
        test_case,
        actual.date,
        expected_year,
        expected_month,
        expected_day,
        places=date_places,
    )
    assert_time_equal(
        test_case,
        actual.time,
        expected_hour,
        expected_minute,
        expected_second,
        places=time_places,
    )


class TimeTestMethods(unittest.TestCase):
    def test_date_of_easter(self):
        assert_date_equal(self, date_of_easter(Year(2009)), 2009, 4, 12)
        assert_date_equal(self, date_of_easter(Year(2010)), 2010, 4, 4)
        assert_date_equal(self, date_of_easter(Year(2024)), 2024, 3, 31)

    def test_date_to_day_number(self):
        self.assertEqual(date_to_day_number(make_date(2000, 1, 1)), 1)
        self.assertEqual(
            date_to_day_number(make_date(2000, 12, 31)),
            366,
        )
        self.assertEqual(
            date_to_day_number(make_date(1900, 12, 31)),
            365,
        )

    def test_greenwich_to_julian_date(self):
        self.assertEqual(
            greenwich_to_julian_date(make_date(2009, 6, 19.75)),
            JulianDate(Scalar(2455002.25)),
        )
        self.assertEqual(
            greenwich_to_julian_date(make_date(1969, 1, 5)),
            JulianDate(Scalar(2440226.5)),
        )

    def test_julian_date_to_j2000(self):
        self.assertEqual(
            julian_date_to_j2000(JulianDate(Scalar(2440227.54513888889))),
            -11317.454861111008,
        )

    def test_julian_to_greenwich_date(self):
        assert_date_equal(
            self,
            julian_to_greenwich_date(JulianDate(Scalar(2455002.25))),
            2009,
            6,
            19.75,
        )
        assert_date_equal(
            self,
            julian_to_greenwich_date(JulianDate(Scalar(2440588))),
            1970,
            1,
            1.5,
        )

    def test_finding_day_of_week(self):
        self.assertEqual(
            finding_day_of_week(JulianDate(Scalar(2455001.5))),
            DaysOfWeek.Friday,
        )
        self.assertEqual(
            finding_day_of_week(greenwich_to_julian_date(make_date(2024, 4, 7))),
            DaysOfWeek.Sunday,
        )

    def test_hours_minutes_seconds_to_decimal_time(self):
        self.assertEqual(
            hours_minutes_seconds_to_decimal_time(make_time(18, 31, 27)),
            DecimalTime(Scalar(18.524166666666666)),
        )
        self.assertEqual(
            hours_minutes_seconds_to_decimal_time(
                make_time(18, 31, 27),
                False,
            ),
            DecimalTime(Scalar(6.524166666666666)),
        )
        self.assertEqual(
            hours_minutes_seconds_to_decimal_time(
                make_time(11, 31, 5),
                False,
            ),
            DecimalTime(Scalar(11.518055555555556)),
        )
        self.assertEqual(
            hours_minutes_seconds_to_decimal_time(
                make_time(12, 0, 0),
                False,
            ),
            DecimalTime(Scalar(12)),
        )
        self.assertEqual(
            hours_minutes_seconds_to_decimal_time(make_time(12, 0, 0)),
            DecimalTime(Scalar(12)),
        )

    def test_decimal_hours_to_hours_minutes_seconds(self):
        assert_time_equal(
            self,
            decimal_hours_to_hours_minutes_seconds(DecimalTime(Scalar(18.52416667))),
            18,
            31,
            27,
        )

    def test_local_civil_to_universal_time(self):
        lct = make_full_date(2013, 7, 1, 3, 37, 5)

        assert_full_date_equal(
            self,
            local_civil_to_universal_time(lct, 1, 4),
            2013,
            6,
            30,
            22,
            37,
            5.0,
        )

    def test_universal_to_local_civil_time(self):
        utc = make_full_date(2013, 6, 30, 22, 37, 0)

        assert_full_date_equal(
            self,
            universal_to_local_civil_time(utc, 4, 1),
            2013,
            7,
            1,
            3,
            37,
            0,
        )

    def test_universal_to_greenwich_sidereal_time(self):
        utc = make_full_date(1980, 4, 22, 14, 36, 51.67)

        assert_time_equal(
            self,
            universal_to_greenwich_sidereal_time(utc),
            4,
            40,
            5.23,
        )

    def test_greenwich_sidereal_to_universal_time(self):
        full_date = make_full_date(1980, 4, 22, 4, 40, 5.23)

        assert_full_date_equal(
            self,
            greenwich_sidereal_to_universal_time(full_date),
            1980,
            4,
            22,
            14,
            36,
            51.67,
        )

    def test_greenwich_sidereal_to_local_sidereal_time(self):
        assert_time_equal(
            self,
            greenwich_sidereal_to_local_sidereal_time(
                make_time(4, 40, 5.23),
                Longitude(Radians(degrees_to_radians(Degrees(Scalar(-64))))),
            ),
            0,
            24,
            5.23,
        )

    def test_local_sidereal_to_greenwich_sidereal_time(self):
        assert_time_equal(
            self,
            local_sidereal_to_greenwich_sidereal_time(
                make_time(0, 24, 5.23),
                Longitude(Radians(degrees_to_radians(Degrees(Scalar(-64))))),
            ),
            4,
            40,
            5.23,
        )

    def test_year_is_leap(self):
        self.assertTrue(year_is_leap(Year(1600)))
        self.assertFalse(year_is_leap(Year(1900)))
        self.assertTrue(year_is_leap(Year(1992)))
        self.assertTrue(year_is_leap(Year(2000)))
        self.assertFalse(year_is_leap(Year(2023)))
        self.assertTrue(year_is_leap(Year(2024)))
        self.assertTrue(year_is_leap(Year(2048)))


if __name__ == "__main__":
    unittest.main()
