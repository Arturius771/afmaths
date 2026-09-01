from __future__ import annotations

import argparse
import datetime
from dataclasses import dataclass, replace
from enum import StrEnum

from afmaths.constants import EARTH_MU
from afmaths.physics.space.astronomy.time_functions import (
    julian_date_delta,
    julian_date_now,
    seconds_from_julian_date_delta,
)
from afmaths.physics.space.celestial_mechanics.orbital_elements import (
    orbital_elements_from_state_vectors,
    state_vector_at_time,
)
from afmaths.physics.space.celestial_mechanics.time import orbital_period
from afmaths.physics.space.engineering.astrodynamics.ground_track import orbits_per_day
from afmaths.physics.space.engineering.two_line_elements import (
    orbital_elements_from_tle,
    parse_julian_date,
    parse_norad_id,
)
from afmaths.physics.space.external.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
)
from afmaths.physics.space.external.space_track_api import (
    get_tle_from_norad_id,
    refresh_tle_cache,
)
from afmaths.physics.space.type_conversion_helpers import fulldate_from_python_datetime
from astronomy_types import Epoch, GravitationalParameter, OrbitalElements


class OrbitSource(StrEnum):
    TLE = "tle"
    HORIZONS = "horizons"
    ELEMENTS = "elements"


@dataclass(frozen=True)
class Orbit:
    name: str
    elements: OrbitalElements
    epoch: Epoch
    source: OrbitSource
    tle: str | None = None


def parse_orbit_source(value: str) -> OrbitSource:
    normalised = value.strip().lower().replace("-", "_")

    aliases = {
        "tle": OrbitSource.TLE,
        "horizon": OrbitSource.HORIZONS,
        "horizons": OrbitSource.HORIZONS,
        "element": OrbitSource.ELEMENTS,
        "elements": OrbitSource.ELEMENTS,
        "custom": OrbitSource.ELEMENTS,
        "orbital_elements": OrbitSource.ELEMENTS,
    }

    try:
        return aliases[normalised]
    except KeyError as error:
        available = "tle, horizon, elements"
        raise argparse.ArgumentTypeError(
            f"Unknown orbit source '{value}'. Expected one of: {available}."
        ) from error


def parse_horizons_target(value: str) -> HorizonsCommandTarget:
    normalised = value.strip().lower().replace("-", "_").replace(" ", "_")

    for target in HorizonsCommandTarget:
        if target.name.lower() == normalised:
            return target

        if str(target.value).lower() == normalised:
            return target

    available = ", ".join(target.name.lower() for target in HorizonsCommandTarget)
    raise ValueError(
        f"Unknown Horizons target '{value}'. Available targets: {available}"
    )


def orbit_from_tle(tle: str) -> Orbit:
    return Orbit(
        name=f"NORAD {parse_norad_id(tle)}",
        elements=orbital_elements_from_tle(tle),
        epoch=Epoch(parse_julian_date(tle)),
        source=OrbitSource.TLE,
        tle=tle,
    )


def orbit_from_horizons(
    target: HorizonsCommandTarget,
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> Orbit:
    start_time = datetime.datetime.now()
    stop_time = start_time + datetime.timedelta(minutes=1)

    state_vectors = get_object_state_vectors_from_horizon(
        target=target,
        centre=centre,
        start_time=fulldate_from_python_datetime(start_time),
        stop_time=fulldate_from_python_datetime(stop_time),
    )

    if not state_vectors:
        raise ValueError(f"No Horizons state vectors returned for {target.name}.")

    return Orbit(
        name=target.name.title().replace("_", " "),
        elements=orbital_elements_from_state_vectors(
            state_vectors[0],
            mu=gravitational_parameter,
        ),
        epoch=Epoch(julian_date_now()),
        source=OrbitSource.HORIZONS,
    )


def orbit_from_elements(
    elements: OrbitalElements,
    name: str = "Custom orbit",
    epoch: Epoch | None = None,
) -> Orbit:
    return Orbit(
        name=name,
        elements=elements,
        epoch=epoch or Epoch(julian_date_now()),
        source=OrbitSource.ELEMENTS,
    )


def orbit_at_current_epoch(
    orbit: Orbit,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> Orbit:
    return replace(
        orbit,
        elements=orbital_elements_from_state_vectors(
            state_vector_at_time(
                orbit.elements,
                seconds_from_julian_date_delta(julian_date_delta(orbit.epoch)),
                gravitational_parameter,
            ),
            mu=gravitational_parameter,
        ),
        epoch=Epoch(julian_date_now()),
    )


def default_orbit_count(orbit: Orbit) -> int:
    return max(
        1,
        round(
            orbits_per_day(
                orbital_period(orbit.elements.semi_major_axis),
            )
        ),
    )


def resolve_orbits(
    source: OrbitSource,
    norad_ids: list[int] | None = None,
    horizons_targets: list[str] | None = None,
    elements: OrbitalElements | None = None,
    centre: HorizonsCommandTarget = HorizonsCommandTarget.EARTH,
    gravitational_parameter: GravitationalParameter = EARTH_MU,
) -> list[Orbit]:
    match source:
        case OrbitSource.TLE:
            if not norad_ids:
                raise ValueError("--norad-id is required for --source tle.")

            refresh_tle_cache()

            return [
                orbit_from_tle(get_tle_from_norad_id(norad_id))
                for norad_id in norad_ids
            ]

        case OrbitSource.HORIZONS:
            if not horizons_targets:
                raise ValueError("--target is required for --source horizon.")

            return [
                orbit_from_horizons(
                    parse_horizons_target(target),
                    centre=centre,
                    gravitational_parameter=gravitational_parameter,
                )
                for target in horizons_targets
            ]

        case OrbitSource.ELEMENTS:
            if elements is None:
                raise ValueError("Orbital elements are required for --source elements.")

            return [orbit_from_elements(elements)]

    raise ValueError(f"Unsupported orbit source: {source}")
