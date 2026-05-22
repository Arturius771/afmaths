from astronomy_types import (
    Distance,
    Scalar,
    Second,
)
from afmaths.visualisations.helpers import (
    EXAMPLE_ELEMENTS,
    plot_sphere_surface,
)
import plotly.graph_objects as go
from afmaths.astrodynamics import (
    generate_all_orbit_positions,
    orbit_state_vector_prediction_from_orbital_elements,
)

CENTRAL_BODY_RADIUS_KM = 6378.0
CENTRAL_BODY_SCALE = 1.0

SECOND_BODY_RADIUS_KM = 1737.0
SECOND_BODY_SCALE = 2.0

PREDICTION_TIME_OFFSET = 1_000_000

# orbital_elements = orbital_elements_from_state_vectors(
#     [10000, 40000, -5000], [-1.5, 1, -0.1]
# )


central_body_radius = CENTRAL_BODY_RADIUS_KM * CENTRAL_BODY_SCALE


central_body_surface = plot_sphere_surface(Distance(Scalar(central_body_radius)))

second_body_surface = plot_sphere_surface(
    Distance(Scalar(SECOND_BODY_RADIUS_KM * SECOND_BODY_SCALE)),
    orbit_state_vector_prediction_from_orbital_elements(
        EXAMPLE_ELEMENTS,
    ).position,
)

predicted_body_surface = plot_sphere_surface(
    Distance(Scalar(SECOND_BODY_RADIUS_KM * SECOND_BODY_SCALE)),
    orbit_state_vector_prediction_from_orbital_elements(
        EXAMPLE_ELEMENTS,
        time_offset_s=Second(Scalar(PREDICTION_TIME_OFFSET)),
    ).position,
)

x = []
y = []
z = []

for position in generate_all_orbit_positions(EXAMPLE_ELEMENTS, 51):
    x.append(position.x)
    y.append(position.y)
    z.append(position.z)


fig = go.Figure(
    data=[
        go.Surface(
            x=central_body_surface.x,
            y=central_body_surface.y,
            z=central_body_surface.z,
            name="Central body",
            opacity=0.5,
            showscale=False,
        ),
        go.Surface(
            x=second_body_surface.x,
            y=second_body_surface.y,
            z=second_body_surface.z,
            name="Orbiting body",
            opacity=0.8,
            showscale=False,
        ),
        go.Surface(
            x=predicted_body_surface.x,
            y=predicted_body_surface.y,
            z=predicted_body_surface.z,
            name="Prediction",
            opacity=0.8,
            showscale=False,
        ),
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines",
            name="Orbit",
        ),
    ]
)

fig.update_layout(
    scene=dict(
        xaxis_title="X (km)",
        yaxis_title="Y (km)",
        zaxis_title="Z (km)",
        aspectmode="data",
    )
)

fig.show()
