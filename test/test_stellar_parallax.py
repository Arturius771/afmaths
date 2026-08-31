import unittest
from astronomy_types import (
    Distance,
    Scalar,
)

from afmaths.physics.space.astronomy.utils import (
    degrees_from_arcsecond,
    parsec_from_metres,
)
from afmaths.physics.space.astronomy.stellar_parallax import (
    distance_from_stellar_parallax,
    distance_from_stellar_parallax_full_angular_displacement,
)


class StellarParallaxTestMethods(unittest.TestCase):

    def test_distance_from_stellar_parallax(self):
        self.assertAlmostEqual(
            parsec_from_metres(
                distance_from_stellar_parallax(
                    degrees_from_arcsecond(0.7685),
                )
            ),
            Distance(Scalar(1.301)),
            places=3,
        )

        self.assertAlmostEqual(
            parsec_from_metres(
                distance_from_stellar_parallax_full_angular_displacement(
                    degrees_from_arcsecond(1.537)
                )
            ),
            Distance(Scalar(1.301)),
            places=3,
        )


if __name__ == "__main__":
    unittest.main()
