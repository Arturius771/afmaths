from __future__ import annotations

from astronomy_types import (
    Anomaly,
    Coordinate2D,
    Coordinate3D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVectors,
    Velocity,
    VelocityVector,
)

import plotly.graph_objects as go

from afmaths.constants import OTHER_EXAMPLE_ELEMENTS, Mass
from afmaths.geometry.geometry import calculate_distance
from afmaths.physics.kinematics import position_vector_from_coordinates
from afmaths.physics.space.astrodynamics import (
    anti_normal,
    anti_radial,
    normal,
    prograde,
    radial,
    retrograde,
)
from afmaths.physics.space.celestial_mechanics import (
    gravitational_parameter,
    orbital_period,
    true_anomaly_from_eccentric_anomaly,
    vis_viva,
)
from afmaths.physics.space.orbit_propagation import eccentric_anomaly_at_time
from afmaths.physics.space.space_engineering import EXAMPLE_ELEMENTS
from afmaths.visualisations.base import (
    orbiting_body_coordinates,
    secondary_focus_coordinates_for_elements,
    tangent_vector_for_plot,
)
from afmaths.visualisations.helpers import (
    OrbitPlot2DSettings,
    PerifocalOrbitLine,
    add_perifocal_orbit_line,
    add_plot_centre,
    central_body_radius_plot,
    elements_scaled_to_plot,
    figure_circle,
    figure_layout,
    figure_planetary_body,
    figure_slider,
    plot_centre,
    plot_max,
    plot_min,
    scale_distance_to_distance,
    vector_line,
)


def add_satellite_direction_traces(
    fig: go.Figure,
    body_name: str,
    coordinates: Coordinate2D,
) -> list[int]:
    trace_indices = []

    for direction_name in [
        "Radial",
        "Anti-radial",
        "Prograde",
        "Retrograde",
        "Normal",
        "Anti-normal",
    ]:
        trace_indices.append(len(tuple(fig.data)))

        fig.add_trace(
            go.Scatter(
                x=[coordinates.x, coordinates.x],
                y=[coordinates.y, coordinates.y],
                mode="lines+markers",
                name=f"{body_name} {direction_name}",
                hoverinfo="name",
            )
        )

    return trace_indices


def add_orbiting_body_2d(
    fig: go.Figure,
    primary_focus_plot_coordinate: Coordinate2D,
    settings: OrbitPlot2DSettings,
    body_name: str,
    body_radius_km: float,
    elements: OrbitalElements,
    is_satellite: bool = False,
) -> tuple[go.Figure, int, int, list[int]]:
    body_trace_index = len(tuple(fig.data))

    plot_elements = elements_scaled_to_plot(
        elements,
        settings.distance_scale,
    )

    coordinates = orbiting_body_coordinates(
        primary_focus_plot_coordinate,
        plot_elements,
        EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
    )

    body_colour = "orange" if is_satellite else "grey"

    fig.add_trace(
        go.Scatter(
            x=[coordinates.x],
            y=[coordinates.y],
            mode="markers",
            name=body_name,
            marker=dict(
                size=body_radius_km / settings.distance_scale + 5,
                color=body_colour,
                line=dict(color=body_colour, width=2),
            ),
            hovertext=[body_name],
            hoverinfo="text",
        )
    )

    label_trace_index = len(tuple(fig.data))

    fig.add_trace(
        go.Scatter(
            x=[coordinates.x],
            y=[coordinates.y],
            mode="markers+text",
            name=f"{body_name} label",
            text=[body_name],
            textposition="top center",
            marker=dict(
                size=1,
                color="rgba(0,0,0,0)",
                line=dict(color="rgba(0,0,0,0)", width=0),
            ),
            hoverinfo="skip",
            showlegend=True,
        )
    )

    add_perifocal_orbit_line(
        fig,
        primary_focus_plot_coordinate,
        PerifocalOrbitLine(
            name=f"{body_name} orbit",
            orbital_elements=plot_elements,
            colour=body_colour,
        ),
    )

    figure_circle(
        fig,
        secondary_focus_coordinates_for_elements(
            primary_focus_plot_coordinate,
            plot_elements,
        ),
        Distance(Scalar(0.1)),
        "red",
        "red",
    )

    vector_trace_indices = (
        add_satellite_direction_traces(fig, body_name, coordinates)
        if is_satellite
        else []
    )

    return fig, body_trace_index, label_trace_index, vector_trace_indices


def real_semi_major_axis_metres(elements: OrbitalElements) -> SemiMajorAxis:
    return SemiMajorAxis(Distance(Scalar(elements.semi_major_axis * 1000)))


def generate_combined_orbital_slider_data(
    settings: OrbitPlot2DSettings,
    primary_focus_plot_coordinate: Coordinate2D,
    central_body_mass_kg: float,
    orbiting_body_names: list[str],
    orbiting_body_mass_kg: list[float],
    orbital_elements: list[OrbitalElements],
    orbiting_body_is_satellite: list[bool],
    body_trace_indices: list[int],
    label_trace_indices: list[int],
    vector_trace_indices: list[list[int]],
) -> list[dict]:
    steps = []

    reference_period = orbital_period(
        real_semi_major_axis_metres(orbital_elements[0]),
        gravitational_parameter(
            Mass(central_body_mass_kg),
            Mass(orbiting_body_mass_kg[0]),
        ),
    )

    for step_index in range(settings.slider_steps):
        fraction = step_index / (settings.slider_steps - 1)
        elapsed_time = reference_period * fraction

        body_x_updates = []
        body_y_updates = []
        label_x_updates = []
        label_y_updates = []
        label_text_updates = []
        vector_x_updates = []
        vector_y_updates = []
        vector_update_indices = []

        for index, elements in enumerate(orbital_elements):

            plot_elements = elements_scaled_to_plot(
                elements,
                settings.distance_scale,
            )

            mu = gravitational_parameter(
                Mass(central_body_mass_kg),
                Mass(orbiting_body_mass_kg[index]),
            )

            eccentric_anomaly_obj = eccentric_anomaly_at_time(
                elements,
                Second(Scalar(elapsed_time)),
            )

            true_anomaly = true_anomaly_from_eccentric_anomaly(
                eccentric_anomaly_obj,
                plot_elements.eccentricity,
            )

            coordinates = orbiting_body_coordinates(
                primary_focus_plot_coordinate,
                plot_elements,
                eccentric_anomaly_obj,
            )

            distance_km = (
                calculate_distance(
                    Coordinate2D(coordinates.x, coordinates.y),
                    primary_focus_plot_coordinate,
                )
                * settings.distance_scale
            )

            velocity_m_s = vis_viva(
                gravitational_parameter=mu,
                orbit_radius=Distance(Scalar(distance_km * 1000)),
                semi_major_axis=SemiMajorAxis(
                    Distance(
                        Scalar(
                            scale_distance_to_distance(
                                plot_elements.semi_major_axis,
                                settings.distance_scale,
                            )
                            * 1000
                        )
                    )
                ),
            )

            velocity_km_s = velocity_m_s / 1000

            body_x_updates.append([coordinates.x])
            body_y_updates.append([coordinates.y])

            label_x_updates.append([coordinates.x])
            label_y_updates.append([coordinates.y])
            label_text_updates.append(
                [
                    f"{orbiting_body_names[index]}<br>"
                    f"r = {distance_km:.2f} km <br>"
                    f"v = {velocity_km_s:.2f} km/s <br>"
                    f"ta = {true_anomaly:.2f} rad <br>"
                    f"t = {elapsed_time:.2f} s"
                ]
            )

            if orbiting_body_is_satellite[index]:
                position_vector = position_vector_from_coordinates(
                    Coordinate3D(coordinates.x, coordinates.y, Scalar(0)),
                    Coordinate3D(
                        primary_focus_plot_coordinate.x,
                        primary_focus_plot_coordinate.y,
                        Scalar(0),
                    ),
                )

                velocity_vector = tangent_vector_for_plot(
                    primary_focus_plot_coordinate,
                    plot_elements,
                    eccentric_anomaly_obj,
                )

                direction_vectors = [
                    radial(position_vector),
                    anti_radial(position_vector),
                    prograde(velocity_vector),
                    retrograde(velocity_vector),
                    normal(StateVectors(position_vector, velocity_vector)),
                    anti_normal(StateVectors(position_vector, velocity_vector)),
                ]

                for direction_vector, trace_index in zip(
                    direction_vectors,
                    vector_trace_indices[index],
                ):
                    xs, ys = vector_line(
                        coordinates,
                        direction_vector,
                        settings,
                    )

                    vector_x_updates.append(xs)
                    vector_y_updates.append(ys)
                    vector_update_indices.append(trace_index)

        update = {
            "x": body_x_updates + label_x_updates + vector_x_updates,
            "y": body_y_updates + label_y_updates + vector_y_updates,
            "text": [[] for _ in body_trace_indices] + label_text_updates,
        }

        steps.append(
            dict(
                method="restyle",
                args=[
                    update,
                    body_trace_indices + label_trace_indices + vector_update_indices,
                ],
                label=f"{fraction:.2f}",
            )
        )

    return steps


def build_2d_orbit_visualiser_figure(
    settings: OrbitPlot2DSettings,
    central_body_name: str,
    central_body_radius_km: float,
    central_body_mass_kg: float,
    orbiting_body_names: list[str],
    orbiting_body_radius_km: list[float],
    orbiting_body_mass_kg: list[float],
    orbital_elements: list[OrbitalElements],
    orbiting_body_is_satellite: list[bool] | None = None,
    title: str = "2D orbit visualiser",
) -> go.Figure:
    if orbiting_body_is_satellite is None:
        orbiting_body_is_satellite = [False for _ in orbiting_body_names]

    if not (
        len(orbiting_body_names)
        == len(orbiting_body_radius_km)
        == len(orbiting_body_mass_kg)
        == len(orbital_elements)
        == len(orbiting_body_is_satellite)
    ):
        raise ValueError(
            "orbiting_body_names, orbiting_body_radius_km, orbiting_body_mass_kg, "
            "orbital_elements, and orbiting_body_is_satellite must have the same length"
        )

    primary_focus_plot_coordinate = plot_centre(settings)

    fig = go.Figure()

    body_trace_indices: list[int] = []
    label_trace_indices: list[int] = []
    vector_trace_indices: list[list[int]] = []

    for index, elements in enumerate(orbital_elements):
        fig, body_trace_index, label_trace_index, body_vector_trace_indices = (
            add_orbiting_body_2d(
                fig,
                primary_focus_plot_coordinate,
                settings,
                orbiting_body_names[index],
                orbiting_body_radius_km[index],
                elements,
                orbiting_body_is_satellite[index],
            )
        )

        body_trace_indices.append(body_trace_index)
        label_trace_indices.append(label_trace_index)
        vector_trace_indices.append(body_vector_trace_indices)

    return add_plot_centre(
        figure_slider(
            figure_layout(
                figure_planetary_body(
                    fig,
                    primary_focus_plot_coordinate,
                    central_body_radius_plot(
                        central_body_radius_km,
                        settings.distance_scale,
                    ),
                    central_body_name,
                    "Black",
                    "blue",
                    "green",
                ),
                settings.plot_width,
                settings.plot_height,
                plot_min(settings),
                plot_max(settings),
                title=title,
            ),
            generate_combined_orbital_slider_data(
                settings,
                primary_focus_plot_coordinate,
                central_body_mass_kg,
                orbiting_body_names,
                orbiting_body_mass_kg,
                orbital_elements,
                orbiting_body_is_satellite,
                body_trace_indices,
                label_trace_indices,
                vector_trace_indices,
            ),
        ),
        primary_focus_plot_coordinate,
        Distance(Scalar(0.1)),
    )


DISTANCE_SCALE_KM = 12_824.9333333


def main() -> None:
    settings = OrbitPlot2DSettings(
        distance_scale=DISTANCE_SCALE_KM,
    )

    build_2d_orbit_visualiser_figure(
        settings=settings,
        central_body_name="Earth",
        central_body_radius_km=6_371.0,
        central_body_mass_kg=5.9722e24,
        orbiting_body_names=["Moon", "Sat"],
        orbiting_body_radius_km=[1_737.4, 1_737.4],
        orbiting_body_mass_kg=[7.346e22, 1000],
        orbiting_body_is_satellite=[False, True],
        orbital_elements=[EXAMPLE_ELEMENTS, OTHER_EXAMPLE_ELEMENTS],
        title="Earth-Moon system",
    ).show()


if __name__ == "__main__":
    main()
