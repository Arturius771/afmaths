from astronomy_types import GravitationalParameter, Scalar, Second

from afmaths.physics.space.astrodynamics import (
    orbit_state_vector_prediction_from_orbital_elements,
    orbital_elements_from_state_vectors,
)

from afmaths.physics.space.horizons_api import (
    HorizonsCommandTarget,
    get_planet_state_vectors,
)

from afmaths.visualisations.helpers import (
    add_body_surface,
    add_orbit_line_trace,
    make_3d_orbit_figure,
    scale_position,
)

DISTANCE_SCALE_KM = 10_000
BODY_RADIUS_SCALE = 20.0
ORBIT_POINTS = 500

START_TIME = "2026-May-27 00:00"
STOP_TIME = "2026-May-28 00:00"
STEP_SIZE = "1h"
TIME_OFFSET = 0

EARTH_RADIUS_KM = 6_371.0
MOON_RADIUS_KM = 1_737.4
EARTH_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398_600.4418))


def get_moon_geocentric_orbital_elements():
    state_vector = get_planet_state_vectors(
        target=HorizonsCommandTarget.MOON,
        centre=HorizonsCommandTarget.EARTH,
        start_time=START_TIME,
        stop_time=STOP_TIME,
        step_size=STEP_SIZE,
    )[0]

    return orbital_elements_from_state_vectors(
        state_vector,
        gravitational_parameter=EARTH_GRAVITATIONAL_PARAMETER,
    )


def main() -> None:
    traces = []

    add_body_surface(
        traces,
        "Earth",
        EARTH_RADIUS_KM,
        BODY_RADIUS_SCALE,
        DISTANCE_SCALE_KM,
        opacity=0.7,
    )

    moon_orbital_elements = get_moon_geocentric_orbital_elements()

    add_orbit_line_trace(
        traces,
        "Moon",
        moon_orbital_elements,
        DISTANCE_SCALE_KM,
        ORBIT_POINTS,
    )

    current_moon_state = orbit_state_vector_prediction_from_orbital_elements(
        moon_orbital_elements,
        Second(Scalar(TIME_OFFSET)),
    )

    current_moon_position = scale_position(
        current_moon_state.position,
        DISTANCE_SCALE_KM,
    )

    add_body_surface(
        traces,
        "Moon",
        MOON_RADIUS_KM,
        BODY_RADIUS_SCALE,
        DISTANCE_SCALE_KM,
        current_moon_position,
        opacity=0.9,
    )

    fig = make_3d_orbit_figure(
        traces,
        "Earth-Moon system",
        DISTANCE_SCALE_KM,
    )

    fig.show()


if __name__ == "__main__":
    main()
