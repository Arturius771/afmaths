import plotly.graph_objects as go
from astronomy_types import Coordinate2D

from afmaths.physics.kinematics import velocity_time_total_displacement

# velocity_points = [
#     Coordinate2D(0, 0),
#     # Coordinate2D(1, 5),
#     Coordinate2D(10, 5),
#     # Coordinate2D(2, 0),
# ]

velocity_points = [
    Coordinate2D(4.8, 2.3),
    # Coordinate2D(1, 5),
    Coordinate2D(6.6, 3.25),
    # Coordinate2D(2, 0),
]


values = [v.y for v in velocity_points]
time = [v.x for v in velocity_points]

sorted_pairs = sorted(zip(time, values))
time_sorted, values_sorted = zip(*sorted_pairs)

sorted_vals = []

for pair in sorted_pairs:
    sorted_vals.append(Coordinate2D(pair[0], pair[1]))

fig = go.Figure()
fig.add_trace(go.Scatter(x=time_sorted, y=values_sorted, mode="lines", name="Velocity"))
fig.update_layout(
    title=f"Velocity over time (displacement: {velocity_time_total_displacement(sorted_vals)})",
    xaxis_title="Time",
    yaxis_title="Velocity",
)
fig.show()
