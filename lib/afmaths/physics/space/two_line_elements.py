import math

from afmaths.physics.space.celestial_mechanics import mean_motion
from afmaths.physics.space.astronomy.type_conversion_helpers import degrees_to_radians
from afmaths.physics.space.astronomy.time_functions import (
    date_to_day_number,
    julian_to_greenwich_date,
)
from astronomy_types import (
    Anomaly,
    Epoch,
    JulianDate,
    MeanMotion,
    OrbitalElements,
    Radians,
    RightAscension,
    Inclination,
    ArgumentOfPerigee,
    SemiMajorAxis,
    Eccentricity,
    TrueAnomaly,
    Scalar,
    Ratio,
    Degrees,
    Distance,
)


def format_tle_exponent(value: float) -> str:
    if value == 0:
        return "00000-0"

    exponent = math.floor(math.log10(abs(value))) + 1
    mantissa = value / (10**exponent)

    return f"{mantissa*1e5:05.0f}{exponent:+d}".replace("+", "")


def first_derivative_mean_motion(mean_motion: MeanMotion) -> float:
    """
    First derivative of mean motion [rev/day²].

    Cannot be derived from a single orbital state.
    TLEs commonly use 0 when no propagation fit exists.
    """
    return 0.0


def second_derivative_mean_motion(mean_motion: MeanMotion) -> float:
    """
    Second derivative of mean motion [rev/day³].

    Usually negligible and often represented as zero.
    """
    return 0.0


def calculate_checksum(line: str) -> int:
    """Calculates the checksum for one TLE line."""
    total = 0

    for char in line:
        if char.isdigit():
            total += int(char)
        elif char == "-":
            total += 1

    return total % 10


def julian_date_to_tle_epoch(julian_date: JulianDate) -> str:
    """Converts a JulianDate to TLE epoch format YYDDD.FFFFFFFF."""

    date = julian_to_greenwich_date(julian_date)

    year = int(date.year)

    day_float = float(date.day)
    whole_day = math.floor(day_float)
    fractional_day = day_float - whole_day

    tle_year = year % 100
    tle_day = date_to_day_number(date) + fractional_day

    return f"{tle_year:02d}{tle_day:012.8f}"


def two_line_element_from_orbital_elements(
    orbital_elements: OrbitalElements,
    catalog_number: int,
    classification: str,
    international_designator: str,
    epoch: Epoch,
    drag_term: float,
    ephemeris: str,
    revolution_number: int,
) -> str:
    """Converts orbital elements to a two line element set string."""

    mean_motion_rad = mean_motion(orbital_elements.semi_major_axis)
    mean_motion_rev_day = mean_motion_rad * 86400 / (2 * math.pi)

    first_derivative = first_derivative_mean_motion(mean_motion_rad)
    second_derivative = second_derivative_mean_motion(mean_motion_rad)

    eccentricity = orbital_elements.eccentricity
    true_anomaly = orbital_elements.true_anomaly

    eccentric_anomaly = 2 * math.atan2(
        math.sqrt(1 - eccentricity) * math.sin(true_anomaly / 2),
        math.sqrt(1 + eccentricity) * math.cos(true_anomaly / 2),
    )

    mean_anomaly = eccentric_anomaly - eccentricity * math.sin(eccentric_anomaly)
    mean_anomaly_deg = math.degrees(mean_anomaly) % 360

    tle_epoch = julian_date_to_tle_epoch(epoch)

    ecc = f"{eccentricity:.7f}".split(".")[1]
    first_derivative_str = f"{first_derivative:.8f}".replace("0.", ".").replace(
        "-0.", "-."
    )

    line1 = (
        f"1 {catalog_number:05d}{classification} "
        f"{international_designator} "
        f"{tle_epoch} "
        f"{first_derivative_str} "
        f"{format_tle_exponent(second_derivative)} "
        f"{format_tle_exponent(drag_term)} "
        f"{ephemeris} "
    )

    line2 = (
        f"2 {catalog_number:05d} "
        f"{math.degrees(orbital_elements.inclination):8.4f} "
        f"{math.degrees(orbital_elements.right_ascension_of_ascending_node):8.4f} "
        f"{ecc} "
        f"{math.degrees(orbital_elements.argument_of_perigee):8.4f} "
        f"{mean_anomaly_deg:8.4f} "
        f"{mean_motion_rev_day:11.8f} "
        f"{revolution_number:05d}"
    )

    return f"{line1}{calculate_checksum(line1)}\n" f"{line2}{calculate_checksum(line2)}"


# TODO: implement parsing of TLE to orbital elements
# def orbital_elements_from_two_line_element(tle_line1: str, tle_line2: str) -> OrbitalElements:
#     """Converts a two line element set to orbital elements."""
#     return


if __name__ == "__main__":

    print(
        two_line_element_from_orbital_elements(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(51.6416)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(247.4627)))),
                ArgumentOfPerigee(degrees_to_radians(Degrees(Scalar(130.5360)))),
                SemiMajorAxis(Distance(Scalar(6796.0))),
                Eccentricity(Ratio(Scalar(0.0006703))),
                TrueAnomaly(Anomaly(Radians(Scalar(5.6728)))),
            ),
            catalog_number=25544,
            classification="U",
            international_designator="98067A",
            epoch=Epoch(JulianDate(Scalar(2460468.0))),
            drag_term=0.0001027,
            ephemeris="0",
            revolution_number=43217,
        )
    )
