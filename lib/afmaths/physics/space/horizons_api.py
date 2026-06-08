from __future__ import annotations

from dataclasses import dataclass
import datetime
from enum import Enum
from typing import Literal

import requests

from astronomy_types import (
    DMS,
    HMS,
    Declination,
    EquatorialCoordinates,
    FullDate,
    Position,
    RightAscension,
    Scalar,
    StateVectors,
    Vector3D,
    Velocity,
)

from afmaths.physics.space.astronomy.type_conversion_helpers import (
    dms_to_radians,
    fulldate_to_string,
    hms_to_radians,
    python_datetime_to_fulldate,
)


class HorizonsFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class HorizonsCommandTarget(str, Enum):
    SUN = "10"
    MERCURY = "199"
    VENUS = "299"
    EARTH = "399"
    MOON = "301"
    MARS = "499"
    JUPITER = "599"
    SATURN = "699"
    URANUS = "799"
    NEPTUNE = "899"


class HorizonsEphemerisType(str, Enum):
    OBSERVER = "OBSERVER"
    ELEMENTS = "ELEMENTS"
    VECTORS = "VECTORS"
    APPROACH = "APPROACH"
    SPK = "SPK"


class HorizonsQuantity(str, Enum):
    RA_DEC = "1"


CoordinateType = Literal["astrometric", "apparent"]


@dataclass(frozen=True)
class HorizonsObserverQuery:
    # The target body for which to retrieve ephemeris data. Can be a planet, moon, asteroid, comet, spacecraft, or other solar system object supported by the Horizons system.
    target: HorizonsCommandTarget
    # The start time for the ephemeris data retrieval, specified in the format "YYYY-MM-DD HH:MM:SS" or as a Julian date.
    start_time: FullDate
    # The stop time for the ephemeris data retrieval, specified in the format "YYYY-MM-DD HH:MM:SS" or as a Julian date.
    stop_time: FullDate
    # The time step size for the ephemeris data retrieval, specified as a string (e.g., "1h" for 1 hour, "30m" for 30 minutes).
    step_size: str = "1h"
    # The center of motion for the ephemeris data retrieval, specified as a HorizonsCommandTarget (e.g., EARTH, SUN).
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH
    # The desired response format for the ephemeris data, specified as a HorizonsFormat (e.g., JSON or TEXT).
    response_format: HorizonsFormat = HorizonsFormat.JSON
    # The type of ephemeris data to retrieve, specified as a HorizonsEphemerisType (e.g., OBSERVER, ELEMENTS, VECTORS).
    ephemeris_type: HorizonsEphemerisType = HorizonsEphemerisType.OBSERVER
    # The specific quantities to retrieve for the ephemeris data, specified as a tuple of HorizonsQuantity (e.g., RA_DEC for right ascension and declination). The default is to retrieve RA and DEC.
    quantities: tuple[HorizonsQuantity, ...] = (HorizonsQuantity.RA_DEC,)


def build_horizons_url(query: HorizonsObserverQuery) -> str:
    quantities = ",".join(quantity.value for quantity in query.quantities)

    request = requests.Request(
        "GET",
        "https://ssd.jpl.nasa.gov/api/horizons.api",
        params={
            "format": query.response_format.value,
            "COMMAND": quote_horizons(query.target.value),
            "EPHEM_TYPE": quote_horizons(query.ephemeris_type.value),
            "CENTER": quote_horizons(f"500@{query.centre.value}"),
            "START_TIME": quote_horizons(fulldate_to_string(query.start_time)),
            "STOP_TIME": quote_horizons(fulldate_to_string(query.stop_time)),
            "STEP_SIZE": quote_horizons(query.step_size),
            "QUANTITIES": quote_horizons(quantities),
        },
    ).prepare()

    if request.url is None:
        raise ValueError("Failed to build Horizons URL")

    return request.url


def fetch_horizons_result(query: HorizonsObserverQuery) -> str:
    url = build_horizons_url(query)
    print(url)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    if query.response_format == HorizonsFormat.JSON:
        data = response.json()

        if "error" in data:
            raise ValueError(data["error"])

        if "result" not in data:
            raise ValueError(f"Horizons JSON response did not contain result: {data}")

        return data["result"]

    return response.text


def extract_ephemeris_rows(result: str) -> list[str]:
    if "$$SOE" not in result or "$$EOE" not in result:
        raise ValueError(
            f"Horizons result did not contain ephemeris markers:\n{result}"
        )

    table = result.split("$$SOE", 1)[1].split("$$EOE", 1)[0]

    return [row.strip() for row in table.splitlines() if row.strip()]


def parse_hms(parts: list[str]) -> HMS:
    if len(parts) != 3:
        raise ValueError(f"Expected HMS parts [HH, MM, SS], got: {parts}")

    return HMS(
        hours=int(parts[0]),
        minutes=int(parts[1]),
        seconds=float(parts[2]),
    )


def parse_dms(parts: list[str]) -> DMS:
    if len(parts) != 3:
        raise ValueError(f"Expected DMS parts [DD, MM, SS], got: {parts}")

    return DMS(
        degrees=int(parts[0]),
        minutes=int(parts[1]),
        seconds=float(parts[2]),
    )


def try_parse_equatorial_coordinates(
    row: str,
    coordinate_type: CoordinateType = "apparent",
) -> EquatorialCoordinates | None:
    parts = row.split()

    # QUANTITIES='1' usually gives:
    # date time RA(h m s) DEC(d m s)
    # => 8 parts total
    if len(parts) >= 8 and len(parts) < 14:
        ra_parts = parts[2:5]
        dec_parts = parts[5:8]

    # Larger/default tables can contain:
    # date time astrometric RA/DEC apparent RA/DEC ...
    elif len(parts) >= 14:
        if coordinate_type == "astrometric":
            ra_parts = parts[2:5]
            dec_parts = parts[5:8]
        else:
            ra_parts = parts[8:11]
            dec_parts = parts[11:14]
    else:
        return None

    try:
        right_ascension = RightAscension(hms_to_radians(parse_hms(ra_parts)))
        declination = Declination(dms_to_radians(parse_dms(dec_parts)))
    except ValueError:
        return None

    return EquatorialCoordinates(
        x=declination,
        y=right_ascension,
    )


def parse_equatorial_coordinates(
    rows: list[str],
    coordinate_type: CoordinateType = "apparent",
) -> list[EquatorialCoordinates]:
    coordinates = []

    for row in rows:
        coordinate = try_parse_equatorial_coordinates(row, coordinate_type)

        if coordinate is not None:
            coordinates.append(coordinate)

    return coordinates


def get_object_equatorial_coordinates(
    target: HorizonsCommandTarget,
    start_time: FullDate,
    stop_time: FullDate,
    step_size: str = "1h",
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    response_format: HorizonsFormat = HorizonsFormat.JSON,
    coordinate_type: CoordinateType = "apparent",
) -> list[EquatorialCoordinates]:
    query = HorizonsObserverQuery(
        target=target,
        start_time=start_time,
        stop_time=stop_time,
        step_size=step_size,
        centre=centre,
        response_format=response_format,
    )

    result = fetch_horizons_result(query)
    rows = extract_ephemeris_rows(result)

    return parse_equatorial_coordinates(rows, coordinate_type)


def quote_horizons(value: str) -> str:
    return f"'{value}'"


def parse_state_vector_rows(rows: list[str]) -> list[StateVectors]:
    state_vectors = []

    index = 0

    while index < len(rows):
        row = rows[index].strip()

        if row.startswith("X ="):
            position_parts = row.replace("=", " ").split()
            velocity_parts = rows[index + 1].replace("=", " ").split()

            x = Position(Scalar(float(position_parts[1])))
            y = Position(Scalar(float(position_parts[3])))
            z = Position(Scalar(float(position_parts[5])))

            vx = Velocity(Scalar(float(velocity_parts[1])))
            vy = Velocity(Scalar(float(velocity_parts[3])))
            vz = Velocity(Scalar(float(velocity_parts[5])))

            state_vectors.append(
                StateVectors(
                    position=Vector3D(x=x, y=y, z=z),
                    velocity=Vector3D(x=vx, y=vy, z=vz),
                )
            )

            index += 2
        else:
            index += 1

    return state_vectors


def get_object_state_vectors_from_horizon(
    target: HorizonsCommandTarget,
    start_time: FullDate,
    stop_time: FullDate,
    step_size: str = "1d",
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    response_format: HorizonsFormat = HorizonsFormat.JSON,
) -> list[StateVectors]:
    query = HorizonsObserverQuery(
        target=target,
        start_time=start_time,
        stop_time=stop_time,
        step_size=step_size,
        centre=centre,
        response_format=response_format,
        ephemeris_type=HorizonsEphemerisType.VECTORS,
        quantities=(),
    )

    result = fetch_horizons_result(query)
    rows = extract_ephemeris_rows(result)
    return parse_state_vector_rows(rows)


if __name__ == "__main__":
    coordinates = get_object_equatorial_coordinates(
        target=HorizonsCommandTarget.MARS,
        start_time=python_datetime_to_fulldate(datetime.datetime.now()),
        stop_time=python_datetime_to_fulldate(
            datetime.datetime.now() + datetime.timedelta(days=1)
        ),
        step_size="1h",
    )

    print(coordinates)
    for coordinate in coordinates:
        print(coordinate)

    state_vectors = get_object_state_vectors_from_horizon(
        target=HorizonsCommandTarget.MARS,
        start_time=python_datetime_to_fulldate(datetime.datetime(2026, 5, 27, 0, 0)),
        stop_time=python_datetime_to_fulldate(datetime.datetime(2026, 5, 28, 0, 0)),
        step_size="1h",
    )

    print(state_vectors)

    for state_vector in state_vectors:
        print(state_vector)
