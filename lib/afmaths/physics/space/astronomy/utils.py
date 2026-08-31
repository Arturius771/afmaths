from astronomy_types import Degrees, Distance, Scalar

from afmaths.constants import ASTRONOMICAL_UNIT


def astronomical_unit_from_metres(dist: Distance) -> Distance:

    return Distance(Scalar(dist / ASTRONOMICAL_UNIT))  # meters


def metres_from_astronomical_unit(dist: Distance) -> Distance:
    """
    Returns the value of one astronomical unit in meters.
    """
    return Distance(Scalar(dist * ASTRONOMICAL_UNIT))  # meters


def arcsecond_from_degrees(degrees: Distance) -> float:
    """
    Converts degrees to arcseconds.
    """
    return float(degrees * 3600)  # arcseconds


def degrees_from_arcsecond(arcseconds: float) -> Degrees:
    """
    Converts arcseconds to degrees.
    """
    return Degrees(Scalar(arcseconds / 3600))  # degrees


def parsec_from_metres(dist: Distance) -> Distance:
    """
    Converts a distance in meters to parsecs.
    """
    return Distance(Scalar(dist / 3.085677581491367e16))  # parsecs


def metres_from_parsec(dist: Distance) -> Distance:
    """
    Converts a distance in parsecs to meters.
    """
    return Distance(Scalar(dist * 3.085677581491367e16))  # meters
