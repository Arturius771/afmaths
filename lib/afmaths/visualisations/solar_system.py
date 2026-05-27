from dataclasses import dataclass

from astronomy_types import (
    Distance,
    GravitationalParameter,
    Scalar,
    Second,
    Vector3D,
)

import plotly.graph_objects as go

from afmaths.space.astrodynamics import (
    generate_all_orbit_positions,
    orbit_state_vector_prediction_from_orbital_elements,
    orbital_elements_from_state_vectors,
)

from afmaths.space.horizons_api import (
    HorizonsCommandTarget,
    get_planet_state_vectors,
)

from afmaths.visualisations.helpers import plot_sphere_surface

# ---------------------------------------------------------------------
# Visualisation scaling
# ---------------------------------------------------------------------

DISTANCE_SCALE_KM = 1_000_000
PLANET_RADIUS_SCALE = 1000.0
SUN_RADIUS_SCALE = 10.0
ORBIT_POINTS = 500

START_TIME = "2026-May-27 00:00"
STOP_TIME = "2026-May-28 00:00"
STEP_SIZE = "1h"

PREDICTION_TIME_OFFSET_S = 1_000_000

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


def scale_value(value: float | int) -> float:
    return float(value) / DISTANCE_SCALE_KM


def scale_position(position) -> Vector3D:
    return Vector3D(
        x=scale_value(position.x),
        y=scale_value(position.y),
        z=scale_value(position.z),
    )


def scaled_radius(radius_km: float, scale: float) -> Distance:
    return Distance(Scalar((radius_km * scale) / DISTANCE_SCALE_KM))


def add_body_surface(
    traces: list,
    name: str,
    radius_km: float,
    radius_scale: float,
    position=None,
    opacity: float = 0.9,
) -> None:
    surface = plot_sphere_surface(
        scaled_radius(radius_km, radius_scale),
        position,
    )

    traces.append(
        go.Surface(
            x=surface.x,
            y=surface.y,
            z=surface.z,
            name=name,
            opacity=opacity,
            showscale=False,
        )
    )


def add_orbit_trace(traces: list, name: str, orbital_elements) -> None:
    x = []
    y = []
    z = []

    for position in generate_all_orbit_positions(orbital_elements, ORBIT_POINTS):
        scaled = scale_position(position)

        x.append(scaled.x)
        y.append(scaled.y)
        z.append(scaled.z)

    traces.append(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            name=f"{name} orbit",
        )
    )


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

    add_orbit_trace(
        traces,
        planet.name,
        orbital_elements,
    )

    current_state = orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements,
    )

    current_position = scale_position(current_state.position)

    add_body_surface(
        traces,
        planet.name,
        planet.radius_km,
        planet.radius_scale,
        current_position,
    )


def main() -> None:
    traces = []

    add_body_surface(
        traces,
        "Sun",
        SUN_RADIUS_KM,
        SUN_RADIUS_SCALE,
        opacity=0.6,
    )

    for planet in PLANETS:
        add_planet(traces, planet)

    fig = go.Figure(data=traces)

    fig.update_layout(
        title="Heliocentric solar system model",
        scene=dict(
            xaxis_title=f"X ({DISTANCE_SCALE_KM:,} km units)",
            yaxis_title=f"Y ({DISTANCE_SCALE_KM:,} km units)",
            zaxis_title=f"Z ({DISTANCE_SCALE_KM:,} km units)",
            aspectmode="data",
        ),
    )

    fig.show()


if __name__ == "__main__":
    main()
