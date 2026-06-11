from dataclasses import dataclass, replace
import datetime
import math

import plotly.graph_objects as go

from astronomy_types import (
    Anomaly,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    PositionVector,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    SemiMinorAxis,
    StateVectors,
    Vector2D,
    Vector3D,
)

from afmaths.geometry import (
    calculate_distance,
    calculate_foci,
    circle_bounding_box,
    ellipse_bounding_box,
)
from afmaths.operation import interval
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    generate_all_orbit_positions,
    generate_angles_on_circle,
    translate_ellipse_coordinate,
    kepler_equation,
    orbit_state_vector_prediction_from_orbital_elements,
    orbital_elements_from_state_vectors,
    time_since_periapsis,
    true_anomaly_from_eccentric_anomaly,
    vis_viva,
)
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    python_datetime_to_fulldate,
    python_timedelta_to_seconds,
)
from afmaths.physics.space.horizons_api import (
    HorizonsCommandTarget,
    get_object_state_vectors_from_horizon,
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
    bounding_box = circle_bounding_box(
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
    moveable: bool = False,
) -> go.Figure:

    if moveable:
        return figure.add_trace(
            go.Scatter(
                x=[coordinates.x],
                y=[coordinates.y],
                mode="markers+text",
                text=[text],
                textposition="top center",
                marker=dict(
                    size=radius + 5,
                    color=fill_colour,
                    line=dict(color=line_colour, width=2),
                ),
                hovertext=[text],
                hoverinfo="text",
            )
        )

    return figure_circle(
        figure, coordinates, radius, fill_colour, line_colour
    ).add_annotation(
        x=coordinates.x,
        y=coordinates.y - radius - 1,
        text=text,
        showarrow=False,
        font=dict(color=text_colour),
    )


def figure_orbit_line(
    figure: go.Figure, ellipse_centre: Coordinate2D, orbital_elements: OrbitalElements
) -> go.Figure:
    ellipse = ellipse_bounding_box(
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


def figure_slider(figure: go.Figure, slider_steps: list[dict]) -> go.Figure:
    return figure.update_layout(sliders=[dict(steps=slider_steps)])


def generate_orbital_slider_data(
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

        eccentric_anomaly_obj = EccentricAnomaly(
            Anomaly(Radians(Scalar(eccentric_anomaly)))
        )

        true_anomaly = true_anomaly_from_eccentric_anomaly(
            eccentric_anomaly_obj,
            elements.eccentricity,
        )
        coordinates = translate_ellipse_coordinate(
            plot_central_point,
            elements.semi_major_axis,
            b,
            eccentric_anomaly_obj,
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
        )

        time = time_since_periapsis(
            SemiMajorAxis(Distance(Scalar(elements.semi_major_axis * plot_scale))),
            g,
            kepler_equation(
                eccentric_anomaly_obj,
                elements.eccentricity,
            ),
        )

        steps.append(
            dict(
                method="restyle",
                args=[
                    {
                        "x": [[coordinates.x]],
                        "y": [[coordinates.y]],
                        "text": [
                            [
                                f"r = {distance:.2f} km <br>"
                                f"v = {velocity:.2f} km/s <br>"
                                f"ta = {true_anomaly:.2f} rad <br>"
                                f"t = {time:.2f} s"
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


def scale_value(value: float | int, distance_scale_km: float) -> float:
    return float(value) / distance_scale_km


def scale_position(position, distance_scale_km: float) -> Vector3D:
    return Vector3D(
        x=scale_value(position.x, distance_scale_km),
        y=scale_value(position.y, distance_scale_km),
        z=scale_value(position.z, distance_scale_km),
    )


def scaled_radius(
    radius_km: float,
    radius_scale: float,
    distance_scale_km: float,
) -> Distance:
    return Distance(Scalar((radius_km * radius_scale) / distance_scale_km))


def add_body_surface(
    name: str,
    radius_km: float,
    radius_scale: float,
    distance_scale_km: float,
    position: PositionVector | None = None,
    opacity: float = 0.9,
) -> go.Surface:
    surface = plot_sphere_surface(
        scaled_radius(radius_km, radius_scale, distance_scale_km),
        position,
    )

    return go.Surface(
        x=surface.x,
        y=surface.y,
        z=surface.z,
        name=name,
        opacity=opacity,
        showscale=False,
    )


def add_orbit_line_trace(
    name: str,
    orbital_elements: OrbitalElements,
    distance_scale_km: float,
    orbit_points: int,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> go.Scatter3d:
    x = []
    y = []
    z = []

    for position in generate_all_orbit_positions(
        orbital_elements, orbit_points, gravitational_parameter
    ):
        scaled = scale_position(position, distance_scale_km)

        x.append(scaled.x)
        y.append(scaled.y)
        z.append(scaled.z)

    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        name=f"{name} orbit",
    )


def make_3d_orbit_figure(
    traces: list,
    title: str,
    distance_scale_km: float,
) -> go.Figure:
    fig = go.Figure(data=traces)

    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=f"X ({distance_scale_km:,} km units)",
            yaxis_title=f"Y ({distance_scale_km:,} km units)",
            zaxis_title=f"Z ({distance_scale_km:,} km units)",
            aspectmode="data",
        ),
    )

    return fig


@dataclass(frozen=True)
class BodyPlotConfig:
    name: str
    target: HorizonsCommandTarget | OrbitalElements
    radius_km: float
    radius_scale: float


@dataclass(frozen=True)
class OrbitPlotSettings:
    centre: HorizonsCommandTarget
    gravitational_parameter: GravitationalParameter
    distance_scale_km: float
    orbit_points: int
    start_time: datetime.datetime
    time_offset: datetime.timedelta
    add_prediction_to_orbit: bool = True

    @property
    def stop_time(self) -> datetime.datetime:
        return self.start_time + self.time_offset

    @property
    def time_offset_seconds(self) -> Second:
        return Second(Scalar(python_timedelta_to_seconds(self.time_offset)))


def get_horizon_state_vectors(
    target: HorizonsCommandTarget,
    settings: OrbitPlotSettings,
) -> list[StateVectors]:
    return get_object_state_vectors_from_horizon(
        target=target,
        centre=settings.centre,
        start_time=python_datetime_to_fulldate(settings.start_time),
        stop_time=python_datetime_to_fulldate(settings.stop_time),
    )


def add_orbiting_body_to_traces(
    traces: list,
    body: BodyPlotConfig,
    settings: OrbitPlotSettings,
    opacity: float = 0.9,
) -> None:
    horizon_state_vectors = get_horizon_state_vectors(
        HorizonsCommandTarget(body.target), settings
    )

    if len(horizon_state_vectors) < 1:
        raise ValueError(f"No Horizons state vectors returned for {body.name}")

    orbital_elements = orbital_elements_from_state_vectors(
        horizon_state_vectors[0],  # horizon state vectors
        gravitational_parameter=settings.gravitational_parameter,
    )

    # For internal consistency, we predict the current state from the orbital elements rather than using the Horizons state vector directly. This ensures that the position used for the body surface and the orbit line are based on the same model.
    model_current_state = orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements,
        Second(Scalar(0)),
        settings.gravitational_parameter,
    )

    traces.append(
        add_orbit_line_trace(
            body.name,
            orbital_elements,
            settings.distance_scale_km,
            settings.orbit_points,
            settings.gravitational_parameter,
        )
    )

    traces.append(
        add_body_surface(
            body.name,
            body.radius_km,
            body.radius_scale,
            settings.distance_scale_km,
            position=scale_position(
                model_current_state.position,
                settings.distance_scale_km,
            ),
            opacity=opacity,
        )
    )

    if not settings.add_prediction_to_orbit:
        return

    model_prediction_state = orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements,
        settings.time_offset_seconds,
        settings.gravitational_parameter,
    )

    traces.append(
        add_body_surface(
            body.name + " prediction",
            body.radius_km,
            body.radius_scale,
            settings.distance_scale_km,
            position=scale_position(
                model_prediction_state.position,
                settings.distance_scale_km,
            ),
            opacity=opacity,
        )
    )
