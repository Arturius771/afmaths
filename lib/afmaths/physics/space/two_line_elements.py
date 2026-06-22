# import math

# from afmaths.operation import divide_by
# from afmaths.physics.space.celestial_mechanics import mean_motion
# from afmaths.physics.space.type_conversion_helpers import degrees_to_radians
# from afmaths.physics.space.astronomy.time_functions import (
#     date_to_day_number,
#     julian_to_greenwich_date,
# )
# from astronomy_types import (
#     Epoch,
#     JulianDate,
#     OrbitalElements,
#     Radians,
#     RightAscension,
#     Inclination,
#     ArgumentOfPeriapsis,
#     SemiMajorAxis,
#     Eccentricity,
#     TrueAnomaly,
#     Scalar,
#     Ratio,
#     Degrees,
#     Distance,
#     MeanMotion,
#     Anomaly
# )

# def mean_motion_from_tle(mean_motion_rev_d) -> MeanMotion:
#     return MeanMotion(mean_motion_rev_d * 2 * math.pi * divide_by(24 * 3600)(1))

# def two_line_element_from_orbital_elements(
#     orbital_elements: OrbitalElements,
#     catalog_number: int,
#     classification: str,
#     international_designator: str,
#     epoch: Epoch,
#     drag_term: float,
#     ephemeris: str,
#     revolution_number: int,
# ) -> str:
#     """Converts orbital elements to a two line element set string."""

#     tle_epoch = #mean julian data
#     mean_motion_rev_day = # mean motion in rev/d


#     line1 = (
#         f"1 {catalog_number:05d}{classification} "
#         f"{international_designator} "
#         f"{tle_epoch} "
#         f"{first_derivative_str} "
#         f"{format_tle_exponent(second_derivative)} "
#         f"{format_tle_exponent(drag_term)} "
#         f"{ephemeris} "
#     )

#     line2 = (
#         f"2 {catalog_number:05d} "
#         f"{math.degrees(orbital_elements.inclination):8.4f} "
#         f"{math.degrees(orbital_elements.right_ascension_of_ascending_node):8.4f} "
#         f"{ecc} "
#         f"{math.degrees(orbital_elements.argument_of_periapsis):8.4f} "
#         f"{mean_anomaly_deg:8.4f} "
#         f"{mean_motion_rev_day:11.8f} "
#         f"{revolution_number:05d}"
#     )

#     return f"{line1}{calculate_checksum(line1)}\n" f"{line2}{calculate_checksum(line2)}"


# # TODO: implement parsing of TLE to orbital elements
# # def orbital_elements_from_two_line_element(tle_line1: str, tle_line2: str) -> OrbitalElements:
# #     """Converts a two line element set to orbital elements."""
# #     return


# if __name__ == "__main__":

#     print(
#         two_line_element_from_orbital_elements(
#             OrbitalElements(
#                 Inclination(degrees_to_radians(Degrees(Scalar(51.6416)))),
#                 RightAscension(degrees_to_radians(Degrees(Scalar(247.4627)))),
#                 ArgumentOfPeriapsis(degrees_to_radians(Degrees(Scalar(130.5360)))),
#                 SemiMajorAxis(Distance(Scalar(6796.0))),
#                 Eccentricity(Ratio(Scalar(0.0006703))),
#                 TrueAnomaly(Anomaly(Radians(Scalar(5.6728)))),
#             ),
#             catalog_number=25544,
#             classification="U",
#             international_designator="98067A",
#             epoch=Epoch(JulianDate(Scalar(2460468.0))),
#             drag_term=0.0001027,
#             ephemeris="0",
#             revolution_number=43217,
#         )
#     )
