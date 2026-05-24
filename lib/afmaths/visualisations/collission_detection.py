import math

from afmaths.astrodynamics import (
    eccentric_anomaly_solved,
    newton_iteration,
)

from astronomy_types import (
    Coordinate2D,
    MeanAnomaly,
    Anomaly,
    Radians,
    Scalar,
    Vector2D,
)

# true_anomaly_from_mean_anomaly()

# def true_anomaly_from_mean_anomaly(
#     eccentricity: Eccentricity, mean_anomaly: float
# ) -> TrueAnomaly:
#     eccentric_anomaly, _ = eccentric_anomaly_solved(
#         newton_iteration, eccentricity, mean_anomaly
#     )

#     return true_anomaly_from_eccentric_anomaly(eccentric_anomaly, eccentricity)

# eccentric_anomaly_solved()

# def eccentric_anomaly_solved(
#     iteration_func,
#     eccentricity: Eccentricity,
#     mean_anomaly: float,
#     tolerance=1e-6,
#     max_iterations=100,
# ) -> tuple[EccentricAnomaly, list]:
#     history = []

#     E_i = mean_anomaly
#     delta_E = float("inf")

#     iteration = 0
#     history.append((iteration, E_i, math.degrees(E_i), None))

#     while iteration < max_iterations and abs(delta_E) > tolerance:
#         E_next = iteration_func(E_i, eccentricity, mean_anomaly)
#         delta_E = E_next - E_i
#         iteration += 1

#         history.append((iteration, E_next, math.degrees(E_next), delta_E))
#         E_i = E_next

#     return EccentricAnomaly(Radians(Scalar(E_i))), history

# newton_iteration()

# def newton_iteration(
#     E_i: EccentricAnomaly, eccentricity: Eccentricity, mean_anomaly: float
# ):
#     # E_i - (E_i - e * np.sin(E_i) - M) / (1 - e * np.cos(E_i))
#     # E_i - (E_i - eccentricity * math.sin(E_i) - mean_anomaly)
#     # M = E - e * np.sin(E)
#     return subtract(
#         divide(subtract(multiply(eccentricity)(math.cos(E_i)))(1))(
#             subtract(mean_anomaly)(mean_anomaly_from_kepler_equation(E_i, eccentricity))
#         )
#     )(E_i)


from afmaths.physics import detect_collision, propogate_vector
from afmaths.visualisations.helpers import EXAMPLE_ELEMENTS
import plotly.graph_objects as go

object_a_coordinates = Coordinate2D(0, 0)
object_a_vector = Vector2D(1, 1)
object_b_coordinates = Coordinate2D(10, 10)
object_b_vector = Vector2D(-1, -1)

vector_a = propogate_vector(object_a_coordinates, object_a_vector)
vector_b = propogate_vector(object_b_coordinates, object_b_vector)

a_x = [index.x for index in vector_a]
a_y = [index.y for index in vector_a]
b_x = [index.x for index in vector_b]
b_y = [index.y for index in vector_b]

collided, collission = detect_collision(
    object_a_coordinates, object_b_coordinates, object_a_vector, object_b_vector
)

fig = go.Figure()
fig.add_trace(go.Scatter(x=a_x, y=a_y, mode="lines+markers", name="Object A"))
fig.add_trace(go.Scatter(x=b_x, y=b_y, mode="lines+markers", name="Object B"))
fig.update_layout(
    title=f"Object trajectory plot collission {collided} at {collission.x}, {collission.y}",
    xaxis_title="X position",
    yaxis_title="Y position",
)
fig.show()
