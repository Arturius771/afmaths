import math

from afmaths.physics.space.astrodynamics import (
    eccentric_anomaly_solved,
    newton_iteration,
)

from astronomy_types import MeanAnomaly, Anomaly, Radians, Scalar

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


from afmaths.visualisations.helpers import EXAMPLE_ELEMENTS
import plotly.graph_objects as go

_, history = eccentric_anomaly_solved(
    newton_iteration,
    EXAMPLE_ELEMENTS.eccentricity,
    MeanAnomaly(Anomaly(Radians(Scalar(1.8 * math.pi)))),
)

values = [row[1] for row in history]
iterations = [row[0] for row in history]

fig = go.Figure()
fig.add_trace(
    go.Scatter(x=iterations, y=values, mode="lines+markers", name="Eccentric anomaly")
)
fig.update_layout(
    title="Newton iteration convergence",
    xaxis_title="Iteration",
    yaxis_title="Eccentric anomaly E [rad]",
)
fig.show()
