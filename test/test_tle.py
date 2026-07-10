import unittest

from afmaths.constants import ISS_TLE_EXAMPLE
from afmaths.physics.space.engineering.two_line_elements import (
    parse_argument_of_periapsis,
    parse_eccentricity,
    parse_epoch,
    parse_inclinatition,
    parse_mean_anomaly,
    parse_mean_motion,
    parse_right_ascension_ascending_node,
)
from afmaths.physics.space.type_conversion_helpers import degrees_from_radians


class TLETestMethods(unittest.TestCase):

    def test_parse_epoch(self):
        self.assertEqual(parse_epoch(ISS_TLE_EXAMPLE), 26191.34711344)

        # self.assertEqual() # TODO: add date/hms test

    def test_parse_inclination(self):
        self.assertEqual(
            degrees_from_radians(parse_inclinatition(ISS_TLE_EXAMPLE)), 51.6302
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
        self.assertEqual(parse_mean_motion(ISS_TLE_EXAMPLE), 15.48968037575346)


if __name__ == "__main__":
    unittest.main()
