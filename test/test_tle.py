import unittest

from afmaths.constants import ISS_NORAD_ID, ISS_TLE_EXAMPLE
from afmaths.physics.space.engineering.two_line_elements import (
    parse_argument_of_periapsis,
    parse_eccentricity,
    parse_full_date,
    parse_inclination,
    parse_mean_anomaly,
    parse_mean_motion_per_day,
    parse_right_ascension_ascending_node,
)
from afmaths.physics.space.external.space_track_api import get_tle_from_norad_id
from afmaths.physics.space.type_conversion_helpers import degrees_from_radians
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


class TLETestMethods(unittest.TestCase):

    def test_parse_full_date(self):
        self.assertEqual(
            parse_full_date(ISS_TLE_EXAMPLE),
            FullDate(
                Date(
                    Year(int(2026)),
                    Month(int(7)),
                    Day(Scalar(10)),
                ),
                Time(
                    hour=Hour(int(8)),
                    minute=Minute(int(19)),
                    second=Second(Scalar(50.60121599999911)),
                ),
            ),
        )

    def test_parse_inclination(self):
        self.assertEqual(
            degrees_from_radians(parse_inclination(ISS_TLE_EXAMPLE)), 51.6302
        )

    def test_parse_right_ascension_ascending_node(self):
        self.assertEqual(
            degrees_from_radians(parse_right_ascension_ascending_node(ISS_TLE_EXAMPLE)),
            185.4700,
        )

    def test_parse_eccentricity(self):
        self.assertEqual(parse_eccentricity(ISS_TLE_EXAMPLE), 0.0006688)

    def test_parse_argument_of_periapsis(self):
        self.assertEqual(
            degrees_from_radians(parse_argument_of_periapsis(ISS_TLE_EXAMPLE)), 278.6359
        )

    def test_parse_mean_anomaly(self):
        self.assertEqual(
            degrees_from_radians(parse_mean_anomaly(ISS_TLE_EXAMPLE)), 81.3872
        )

    def test_parse_mean_motionn(self):
        self.assertEqual(parse_mean_motion_per_day(ISS_TLE_EXAMPLE), 15.48968037)

    # Don't run this test frequently, and the eccentricity will change
    # def test_space_track(self):
    #     self.assertEqual(
    #         parse_eccentricity(get_tle_from_norad_id(ISS_NORAD_ID)), 0.0006688
    #     )


if __name__ == "__main__":
    unittest.main()
