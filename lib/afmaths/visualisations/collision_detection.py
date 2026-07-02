from astronomy_types import Coordinate2D
import plotly.graph_objects as go

from afmaths.physics.kinematics import detect_collision, propagate_vector
from afmaths.physics.space.type_conversion_helpers import make_vector2d


OBJECT_A_COORDINATES = Coordinate2D[float](5, 10)
OBJECT_A_VECTOR = make_vector2d(0, -1)
OBJECT_B_COORDINATES = Coordinate2D[float](0, 5)
OBJECT_B_VECTOR = make_vector2d(1, 0)
STEPS = 10


def build_collision_detection_figure() -> go.Figure:
    vector_a = propagate_vector(OBJECT_A_COORDINATES, OBJECT_A_VECTOR, STEPS)
    vector_b = propagate_vector(OBJECT_B_COORDINATES, OBJECT_B_VECTOR, STEPS)

    collided, collision = detect_collision(
        OBJECT_A_COORDINATES,
        OBJECT_B_COORDINATES,
        OBJECT_A_VECTOR,
        OBJECT_B_VECTOR,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[point.x for point in vector_a],
            y=[point.y for point in vector_a],
            mode="lines+markers",
            name="Object A",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[point.x for point in vector_b],
            y=[point.y for point in vector_b],
            mode="lines+markers",
            name="Object B",
        )
    )
    fig.update_layout(
        title=f"Object trajectory collision {collided} at ({collision.x}, {collision.y})",
        xaxis_title="X position",
        yaxis_title="Y position",
    )

    return fig


def main() -> None:
    build_collision_detection_figure().show()


if __name__ == "__main__":
    main()
