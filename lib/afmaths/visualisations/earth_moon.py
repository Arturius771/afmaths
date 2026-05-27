from astronomy_types import (
    Distance,
    GravitationalParameter,
    Scalar,
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

DISTANCE_SCALE_KM = 10_000
BODY_RADIUS_SCALE = 20.0
ORBIT_POINTS = 500

START_TIME = "2026-May-27 00:00"
STOP_TIME = "2026-May-28 00:00"
STEP_SIZE = "1h"

# ---------------------------------------------------------------------
# Earth / Moon constants
# ---------------------------------------------------------------------

EARTH_RADIUS_KM = 6_371.0
MOON_RADIUS_KM = 1_737.4

EARTH_GRAVITATIONAL_PARAMETER = GravitationalParameter(Scalar(398_600.4418))


def scale_value(value: float | int) -> float:
    return float(value) / DISTANCE_SCALE_KM


def scale_position(position) -> Vector3D:
    return Vector3D(
        x=scale_value(position.x),
        y=scale_value(position.y),
        z=scale_value(position.z),
    )


def scaled_radius(radius_km: float, scale: float = BODY_RADIUS_SCALE) -> Distance:
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

    # Earth is the origin because the Moon state vector is Earth-centred.
    add_body_surface(
        traces,
        "Earth",
        EARTH_RADIUS_KM,
        BODY_RADIUS_SCALE,
        opacity=0.7,
    )

    moon_orbital_elements = get_moon_geocentric_orbital_elements()

    add_orbit_trace(
        traces,
        "Moon",
        moon_orbital_elements,
    )

    current_moon_state = orbit_state_vector_prediction_from_orbital_elements(
        moon_orbital_elements,
    )

    current_moon_position = scale_position(current_moon_state.position)

    add_body_surface(
        traces,
        "Moon",
        MOON_RADIUS_KM,
        BODY_RADIUS_SCALE,
        current_moon_position,
        opacity=0.9,
    )

    fig = go.Figure(data=traces)

    fig.update_layout(
        title="Earth-Moon system",
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
