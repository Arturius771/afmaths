import plotly.graph_objects as go
from astronomy_types import Coordinate2D

from afmaths.physics.kinematics import velocity_time_total_displacement


VELOCITY_POINTS = [
    Coordinate2D(4.8, 2.3),
    Coordinate2D(6.6, 3.25),
]


def sorted_velocity_points(points: list[Coordinate2D]) -> list[Coordinate2D]:
    return [
        Coordinate2D(time, velocity)
        for time, velocity in sorted((point.x, point.y) for point in points)
    ]


def build_velocity_time_figure(
    velocity_points: list[Coordinate2D] | None = None,
) -> go.Figure:
    points = sorted_velocity_points(velocity_points or VELOCITY_POINTS)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[point.x for point in points],
            y=[point.y for point in points],
            mode="lines",
            name="Velocity",
        )
    )
    fig.update_layout(
        title=(
            "Velocity over time "
            f"(displacement: {velocity_time_total_displacement(points)})"
        ),
        xaxis_title="Time",
        yaxis_title="Velocity",
    )

    return fig


def main() -> None:
    build_velocity_time_figure().show()


if __name__ == "__main__":
    main()
