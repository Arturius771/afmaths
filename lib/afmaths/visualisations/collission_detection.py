from astronomy_types import (
    Coordinate2D,
    Vector2D,
)

import plotly.graph_objects as go

from afmaths.physics.kinematics import detect_collision, propagate_vector

object_a_coordinates = Coordinate2D[float](5, 10)
object_a_vector = Vector2D(0, -1)
object_b_coordinates = Coordinate2D[float](0, 5)
object_b_vector = Vector2D(1, 0)

vector_a = propagate_vector(object_a_coordinates, object_a_vector, 10)
vector_b = propagate_vector(object_b_coordinates, object_b_vector, 10)

a_x = [index.x for index in vector_a]
a_y = [index.y for index in vector_a]
b_x = [index.x for index in vector_b]
b_y = [index.y for index in vector_b]

collided, collision = detect_collision(
    object_a_coordinates, object_b_coordinates, object_a_vector, object_b_vector
)

fig = go.Figure()
fig.add_trace(go.Scatter(x=a_x, y=a_y, mode="lines+markers", name="Object A"))
fig.add_trace(go.Scatter(x=b_x, y=b_y, mode="lines+markers", name="Object B"))
fig.update_layout(
    title=f"Object trajectory collision {collided} at ({collision.x}, {collision.y})",
    xaxis_title="X position",
    yaxis_title="Y position",
)
fig.show()
