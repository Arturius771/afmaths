import math

from afmaths.operation import interval
from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Distance,
    Eccentricity,
    Inclination,
    OrbitalElements,
    PositionVector,
    Ratio,
    RightAscension,
    Scalar,
    Second,
    SemiMajorAxis,
    TrueAnomaly,
    Vector2D,
    Vector3D,
    Coordinate2D,
    EccentricAnomaly,
    Radians,
    Distance,
    GravitationalParameter,
    SemiMinorAxis,
)
import plotly.graph_objects as go
from afmaths.astrodynamics import (
    orbit_state_vector_prediction_from_orbital_elements,
    generate_angles_on_circle,
    generate_relative_coordinate_from_eccentric_anomaly,
    true_anomaly_from_eccentric_anomaly,
    vis_viva,
)
from afmaths.geometry import (
    calculate_distance,
    calculate_foci,
    draw_circle_bounding_box,
    draw_ellipse,
)

EXAMPLE_ELEMENTS = OrbitalElements(
    Inclination(Radians(Scalar(math.radians(5.145)))),
    RightAscension(Radians(Scalar(3.024483909022929))),
    ArgumentOfPerigee(Radians(Scalar(8.8))),
    SemiMajorAxis(Distance(Scalar(384748))),
    Eccentricity(Ratio(Scalar(0.0549006))),
    TrueAnomaly(Anomaly(Radians(Scalar(2.987554518980773)))),
)


def figure_layout(
    figure: go.Figure,
    width_px: float,
    height_px: float,
    plot_start: Vector2D,
    plot_end: Vector2D,
    zeroline: bool = False,
) -> go.Figure:
    return (
        figure.update_layout(width=width_px, height=height_px)
        .update_xaxes(range=[plot_start.x, plot_end.x], zeroline=zeroline)
        .update_yaxes(
            range=[plot_start.y, plot_end.y],
            scaleanchor="x",
            scaleratio=1,
        )
    )


def figure_circle(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance,
    fill_colour: str = "blue",
    line_colour: str = "blue",
) -> go.Figure:
    bounding_box = draw_circle_bounding_box(
        coordinates,
        radius,
    )
    return figure.add_shape(
        type="circle",
        x0=bounding_box[0].x,
        y0=bounding_box[0].y,
        x1=bounding_box[1].x,
        y1=bounding_box[1].y,
        fillcolor=fill_colour,
        line_color=line_colour,
    )


def figure_plot_centre(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance = Distance(Scalar(1)),
    fill_colour: str = "red",
    line_colour: str = "red",
) -> go.Figure:
    return figure_circle(figure, coordinates, radius, fill_colour, line_colour)


def figure_planetary_body(
    figure: go.Figure,
    coordinates: Coordinate2D,
    radius: Distance,
    text: str = "Planet",
    text_colour: str = "Black",
    fill_colour: str = "blue",
    line_colour: str = "blue",
) -> go.Figure:
    return figure_circle(
        figure, coordinates, radius, fill_colour, line_colour
    ).add_annotation(
        x=coordinates.x,
        y=coordinates.y - radius - 1,
        text=text,
        showarrow=False,
        font=dict(color=text_colour),
    )


def figure_moveable_planetary_body(
    figure: go.Figure,
    initial_coordinates: Coordinate2D,
    text: str = "",
    fill_colour: str = "",
    line_colour: str = "",
) -> go.Figure:

    return figure.add_trace(
        go.Scatter(
            x=[initial_coordinates.x],
            y=[initial_coordinates.y],
            mode="markers+text",
            text=[text],
            textposition="top center",
            marker=dict(
                size=18,
                color=fill_colour,
                line=dict(color=line_colour, width=2),
            ),
            hovertext=["Moon"],
            hoverinfo="text",
        )
    )


def figure_orbit_line(
    figure: go.Figure, ellipse_centre: Coordinate2D, orbital_elements: OrbitalElements
) -> go.Figure:
    ellipse = draw_ellipse(
        ellipse_centre,
        orbital_elements.semi_major_axis,
        orbital_elements.eccentricity,
    )
    return figure.add_shape(
        type="circle",
        x0=ellipse[0].x,
        y0=ellipse[0].y,
        x1=ellipse[1].x,
        y1=ellipse[1].y,
        line_color="grey",
    )


def figure_slider(figure: go.Figure, slider: list[dict]) -> go.Figure:
    return figure.update_layout(sliders=[dict(steps=slider)])


def generate_orbital_slider(
    step_n: int,
    plot_central_point: Coordinate2D,
    primary_body_coordinates: Coordinate2D,
    elements: OrbitalElements,
    b: SemiMinorAxis,
    plot_scale: float,
    g: GravitationalParameter,
) -> list[dict]:
    steps = []

    for eccentric_anomaly in generate_angles_on_circle(step_n):

        true_anomaly = true_anomaly_from_eccentric_anomaly(
            EccentricAnomaly(Anomaly(Radians(Scalar(eccentric_anomaly)))),
            elements.eccentricity,
        )
        coordinates = generate_relative_coordinate_from_eccentric_anomaly(
            plot_central_point,
            elements.semi_major_axis,
            b,
            EccentricAnomaly(Anomaly(Radians(Scalar(eccentric_anomaly)))),
        )

        distance = (
            calculate_distance(
                Coordinate2D(coordinates.x, coordinates.y),
                primary_body_coordinates,
            )
            * plot_scale
        )

        velocity = vis_viva(
            orbit_radius=Distance(Scalar(distance)),
            semi_major_axis=SemiMajorAxis(
                Distance(Scalar(elements.semi_major_axis * plot_scale))
            ),
            gravitational_parameter=g,
        )  # vis-viva equation

        steps.append(
            dict(
                method="restyle",
                args=[
                    {
                        "x": [[coordinates.x]],
                        "y": [[coordinates.y]],
                        "text": [
                            [
                                f"r = {distance:.2f} km <br>v = {velocity:.2f} km/s <br>ta = {true_anomaly:.2f} rad"
                            ]
                        ],
                    },
                    [0],  # update only secondary trace
                ],
            )
        )
    return steps


def plot_foci_positions(
    plot_centre: Coordinate2D, elements: OrbitalElements, focus: int = 0
) -> Coordinate2D:
    # Primary body sits at focus
    return Coordinate2D(
        plot_centre.x
        - calculate_foci(elements.semi_major_axis, elements.eccentricity)[focus].x,
        plot_centre.y,
    )


def plot_sphere_surface(
    radius: Distance,
    centre: PositionVector | None = None,
    resolution: int = 50,
) -> Vector3D:
    u = interval(0, 2 * math.pi, resolution)
    v = interval(0, math.pi, resolution)

    centre_x = 0 if centre is None else centre.x
    centre_y = 0 if centre is None else centre.y
    centre_z = 0 if centre is None else centre.z

    sphere_x = [
        [centre_x + radius * math.cos(u_i) * math.sin(v_j) for v_j in v] for u_i in u
    ]

    sphere_y = [
        [centre_y + radius * math.sin(u_i) * math.sin(v_j) for v_j in v] for u_i in u
    ]

    sphere_z = [[centre_z + radius * math.cos(v_j) for v_j in v] for _ in u]

    return Vector3D(sphere_x, sphere_y, sphere_z)
