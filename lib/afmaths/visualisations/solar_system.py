from dataclasses import dataclass

from astronomy_types import GravitationalParameter, Scalar, Second

from afmaths.space.astrodynamics import (
    orbit_state_vector_prediction_from_orbital_elements,
    orbital_elements_from_state_vectors,
)

from afmaths.space.horizons_api import (
    HorizonsCommandTarget,
    get_planet_state_vectors,
)

from afmaths.visualisations.helpers import (
    add_body_surface,
    add_orbit_line_trace,
    make_3d_orbit_figure,
    scale_position,
)

DISTANCE_SCALE_KM = 1_000_000
PLANET_RADIUS_SCALE = 1000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 500

START_TIME = "2026-May-27 00:00"
STOP_TIME = "2026-May-28 00:00"
STEP_SIZE = "1h"
TIME_OFFSET = 0

SUN_RADIUS_KM = 696_340.0
SUN_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(132_712_440_018.0))


@dataclass(frozen=True)
class PlanetPlotConfig:
    name: str
    target: HorizonsCommandTarget
    radius_km: float
    radius_scale: float = PLANET_RADIUS_SCALE


PLANETS = [
    PlanetPlotConfig("Mercury", HorizonsCommandTarget.MERCURY, 2_439.7),
    PlanetPlotConfig("Venus", HorizonsCommandTarget.VENUS, 6_051.8),
    PlanetPlotConfig("Earth", HorizonsCommandTarget.EARTH, 6_371.0),
    PlanetPlotConfig("Mars", HorizonsCommandTarget.MARS, 3_389.5),
    PlanetPlotConfig("Jupiter", HorizonsCommandTarget.JUPITER, 69_911.0, 80.0),
    PlanetPlotConfig("Saturn", HorizonsCommandTarget.SATURN, 58_232.0, 80.0),
    PlanetPlotConfig("Uranus", HorizonsCommandTarget.URANUS, 25_362.0, 150.0),
    PlanetPlotConfig("Neptune", HorizonsCommandTarget.NEPTUNE, 24_622.0, 150.0),
]


def get_heliocentric_orbital_elements(target: HorizonsCommandTarget):
    state_vector = get_planet_state_vectors(
        target=target,
        centre=HorizonsCommandTarget.SUN,
        start_time=START_TIME,
        stop_time=STOP_TIME,
        step_size=STEP_SIZE,
    )[0]

    return orbital_elements_from_state_vectors(
        state_vector,
        gravitational_parameter=SUN_GRAVITATIONAL_PARAMETER,
    )


def add_planet(traces: list, planet: PlanetPlotConfig) -> None:
    orbital_elements = get_heliocentric_orbital_elements(planet.target)

    add_orbit_line_trace(
        traces,
        planet.name,
        orbital_elements,
        DISTANCE_SCALE_KM,
        ORBIT_POINTS,
    )

    current_state = orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements,
        Second(Scalar(TIME_OFFSET)),
    )

    current_position = scale_position(current_state.position, DISTANCE_SCALE_KM)

    add_body_surface(
        traces,
        planet.name,
        planet.radius_km,
        planet.radius_scale,
        DISTANCE_SCALE_KM,
        current_position,
    )


def main() -> None:
    traces = []

    add_body_surface(
        traces,
        "Sun",
        SUN_RADIUS_KM,
        SUN_RADIUS_SCALE,
        DISTANCE_SCALE_KM,
        opacity=0.6,
    )

    for planet in PLANETS:
        add_planet(traces, planet)

    fig = make_3d_orbit_figure(
        traces,
        "Heliocentric solar system model",
        DISTANCE_SCALE_KM,
    )

    fig.show()


if __name__ == "__main__":
    main()
