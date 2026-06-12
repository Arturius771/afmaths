from abc import ABC, abstractmethod
from dataclasses import replace
import math

import plotly.graph_objects as go

from afmaths.constants import Mass
from afmaths.geometry import (
    calculate_distance,
    calculate_foci,
    semi_minor_axis,
    translate_ellipse_coordinate,
)
from afmaths.physics.kinematics import position_vector_from_coordinates
from afmaths.physics.space.astrodynamics import (
    anti_normal,
    anti_radial,
    normal,
    prograde,
    radial,
    retrograde,
)
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    fulldate_to_string,
    python_datetime_to_fulldate,
)
from afmaths.physics.space.celestial_mechanics import (
    gravitational_parameter,
    orbital_period,
    true_anomaly_from_eccentric_anomaly,
    vis_viva,
)
from afmaths.physics.space.orbit_propagation import (
    eccentric_anomaly_at_time,
    generate_angles_on_circle,
)
from afmaths.visualisations.helpers import (
    BodyPlotConfig,
    OrbitPlot2DSettings,
    OrbitPlotSettings,
    add_body_surface,
    add_orbiting_body_to_traces,
    figure_circle,
    figure_layout,
    figure_planetary_body,
    figure_plot_centre,
    figure_slider,
    make_3d_orbit_figure,
    rotate_around_point,
)

from astronomy_types import (
    Anomaly,
    Coordinate2D,
    Coordinate3D,
    Distance,
    EccentricAnomaly,
    MeanAnomaly,
    OrbitalElements,
    Radians,
    Scalar,
    Second,
    SemiMajorAxis,
    StateVectors,
    Vector2D,
    Vector3D,
    Velocity,
    VelocityVector,
)


class Base3DOrbitPlot(ABC):
    def __init__(self, settings: OrbitPlotSettings):
        self.settings = settings

    @property
    @abstractmethod
    def title_prefix(self) -> str:
        pass

    @property
    @abstractmethod
    def central_body_name(self) -> str:
        pass

    @property
    @abstractmethod
    def central_body_radius_km(self) -> float:
        pass

    @property
    @abstractmethod
    def central_body_radius_scale(self) -> float:
        pass

    @property
    def central_body_opacity(self) -> float:
        return 0.7

    @property
    @abstractmethod
    def orbiting_bodies(self) -> list[BodyPlotConfig]:
        pass

    def build_traces(self) -> list:
        traces = [
            add_body_surface(
                self.central_body_name,
                self.central_body_radius_km,
                self.central_body_radius_scale,
                self.settings.distance_scale_km,
                opacity=self.central_body_opacity,
            )
        ]

        for body in self.orbiting_bodies:
            add_orbiting_body_to_traces(traces, body, self.settings)

        return traces

    def make_title(self) -> str:
        return (
            self.title_prefix
            + ": "
            + fulldate_to_string(python_datetime_to_fulldate(self.settings.start_time))
        )

    def show(self) -> None:
        fig = make_3d_orbit_figure(
            self.build_traces(),
            self.make_title(),
            self.settings.distance_scale_km,
        )
        fig.show()


class Base2DOrbitPlot(ABC):
    def __init__(self, settings: OrbitPlot2DSettings):
        self.settings = settings

    @property
    @abstractmethod
    def title_prefix(self) -> str:
        pass

    @property
    @abstractmethod
    def central_body_name(self) -> str:
        pass

    @property
    @abstractmethod
    def central_body_radius_km(self) -> float:
        pass

    @property
    @abstractmethod
    def central_body_mass_kg(self) -> float:
        pass

    @property
    @abstractmethod
    def orbiting_body_names(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def orbiting_body_radius_km(self) -> list[float]:
        pass

    @property
    @abstractmethod
    def orbiting_body_mass_kg(self) -> list[float]:
        pass

    @property
    @abstractmethod
    def orbital_elements(self) -> list[OrbitalElements]:
        pass

    @property
    def orbiting_body_is_satellite(self) -> list[bool]:
        return [False for _ in self.orbiting_body_names]

    @property
    def plot_min(self) -> Vector2D:
        return Vector2D(x=self.settings.plot_min_x, y=self.settings.plot_min_y)

    @property
    def plot_max(self) -> Vector2D:
        return Vector2D(x=self.settings.plot_max_x, y=self.settings.plot_max_y)

    @property
    def plot_width(self) -> int:
        return self.settings.plot_width

    @property
    def plot_height(self) -> int:
        return self.settings.plot_height

    @property
    def num_steps(self) -> int:
        return self.settings.slider_steps

    @property
    def central_point(self) -> Coordinate2D:
        return Coordinate2D(self.plot_max.x / 2, self.plot_max.y / 2)

    @property
    def central_body_radius_plot(self) -> Distance:
        return Distance(
            Scalar(self.central_body_radius_km / self.settings.distance_scale_km)
        )

    def orbiting_body_radius_plot(self, index: int) -> Distance:
        return Distance(
            Scalar(
                self.orbiting_body_radius_km[index] / self.settings.distance_scale_km
            )
        )

    def semi_major_axis_metres(self, index: int) -> SemiMajorAxis:
        return SemiMajorAxis(
            Distance(
                Scalar(
                    self.orbital_elements[index].semi_major_axis
                    * self.settings.distance_scale_km
                    * 1000
                )
            )
        )

    def initial_orbiting_body_coordinates(self, index: int) -> Coordinate2D:
        return self.orbiting_body_coordinates(
            index,
            EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
        )

    def validate_orbiting_bodies(self) -> None:
        if not (
            len(self.orbiting_body_names)
            == len(self.orbiting_body_radius_km)
            == len(self.orbiting_body_mass_kg)
            == len(self.orbital_elements)
            == len(self.orbiting_body_is_satellite)
        ):
            raise ValueError(
                "orbiting_body_names, orbiting_body_radius_km, "
                "orbiting_body_mass_kg, orbital_elements, and "
                "orbiting_body_is_satellite must have the same length"
            )

    def add_orbiting_body(
        self, fig: go.Figure, index: int
    ) -> tuple[go.Figure, int, int, list[int]]:
        body_trace_index = len(tuple(fig.data))
        coordinates = self.initial_orbiting_body_coordinates(index)
        body_colour = "orange" if self.orbiting_body_is_satellite[index] else "grey"

        fig.add_trace(
            go.Scatter(
                x=[coordinates.x],
                y=[coordinates.y],
                mode="markers",
                name=self.orbiting_body_names[index],
                marker=dict(
                    size=self.orbiting_body_radius_plot(index) + 5,
                    color=body_colour,
                    line=dict(color=body_colour, width=2),
                ),
                hovertext=[self.orbiting_body_names[index]],
                hoverinfo="text",
            )
        )

        label_trace_index = len(tuple(fig.data))

        fig.add_trace(
            go.Scatter(
                x=[coordinates.x],
                y=[coordinates.y],
                mode="markers+text",
                name=f"{self.orbiting_body_names[index]} label",
                text=[self.orbiting_body_names[index]],
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

        self.add_orbit_line(fig, index)

        fig = figure_circle(
            fig,
            self.secondary_focus_coordinates(index),
            Distance(Scalar(0.1)),
            "red",
            "red",
        )

        vector_trace_indices = self.add_satellite_direction_traces(
            fig,
            index,
            coordinates,
        )

        return fig, body_trace_index, label_trace_index, vector_trace_indices

    def add_orbit_line(self, fig: go.Figure, index: int) -> None:
        coordinates = [
            self.orbiting_body_coordinates(
                index,
                EccentricAnomaly(Anomaly(Radians(Scalar(angle)))),
            )
            for angle in generate_angles_on_circle(200)
        ]

        orbit_colour = "orange" if self.orbiting_body_is_satellite[index] else "grey"

        fig.add_trace(
            go.Scatter(
                x=[coordinate.x for coordinate in coordinates],
                y=[coordinate.y for coordinate in coordinates],
                mode="lines",
                name=f"{self.orbiting_body_names[index]} orbit",
                line=dict(color=orbit_colour),
                hoverinfo="skip",
            )
        )

    def add_satellite_direction_traces(
        self,
        fig: go.Figure,
        index: int,
        coordinates: Coordinate2D,
    ) -> list[int]:
        if not self.orbiting_body_is_satellite[index]:
            return []

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
                    name=f"{self.orbiting_body_names[index]} {direction_name}",
                    hoverinfo="name",
                )
            )

        return trace_indices

    def secondary_focus_coordinates(self, index: int) -> Coordinate2D:
        elements = self.orbital_elements[index]

        c = calculate_foci(
            elements.semi_major_axis,
            elements.eccentricity,
        )[0].x

        unrotated_second_focus = Coordinate2D(
            self.central_point.x + 2 * c,
            self.central_point.y,
        )

        return rotate_around_point(
            unrotated_second_focus,
            self.central_point,
            elements.argument_of_periapsis,
        )

    def build_figure(self) -> go.Figure:
        self.validate_orbiting_bodies()

        fig = go.Figure()

        body_trace_indices: list[int] = []
        label_trace_indices: list[int] = []
        vector_trace_indices: list[list[int]] = []

        for index in range(len(self.orbital_elements)):
            fig, body_trace_index, label_trace_index, body_vector_trace_indices = (
                self.add_orbiting_body(fig, index)
            )

            body_trace_indices.append(body_trace_index)
            label_trace_indices.append(label_trace_index)
            vector_trace_indices.append(body_vector_trace_indices)

        fig = figure_planetary_body(
            fig,
            self.central_point,
            self.central_body_radius_plot,
            self.central_body_name,
            "Black",
            "blue",
            "green",
        )

        fig = figure_layout(
            fig,
            self.plot_width,
            self.plot_height,
            self.plot_min,
            self.plot_max,
        )

        fig = figure_slider(
            fig,
            self.generate_combined_orbital_slider_data(
                body_trace_indices,
                label_trace_indices,
                vector_trace_indices,
            ),
        )

        fig = figure_plot_centre(
            fig,
            self.central_point,
            Distance(Scalar(0.1)),
        )

        fig.update_layout(title=self.make_title())

        return fig

    def make_title(self) -> str:
        return self.title_prefix

    def show(self) -> None:
        self.build_figure().show()

    def generate_combined_orbital_slider_data(
        self,
        body_trace_indices: list[int],
        label_trace_indices: list[int],
        vector_trace_indices: list[list[int]],
    ) -> list[dict]:
        steps = []

        reference_period = orbital_period(
            self.semi_major_axis_metres(0),
            gravitational_parameter(
                Mass(self.central_body_mass_kg),
                Mass(self.orbiting_body_mass_kg[0]),
            ),
        )

        for step_index in range(self.num_steps):
            fraction = step_index / (self.num_steps - 1)
            elapsed_time = reference_period * fraction

            body_x_updates = []
            body_y_updates = []

            label_x_updates = []
            label_y_updates = []
            label_text_updates = []

            vector_x_updates = []
            vector_y_updates = []
            vector_update_indices = []

            for index in range(len(self.orbital_elements)):
                elements = self.orbital_elements[index]

                eccentric_anomaly_obj = eccentric_anomaly_at_time(
                    replace(
                        elements,
                        semi_major_axis=SemiMajorAxis(
                            Distance(
                                Scalar(
                                    self.orbital_elements[index].semi_major_axis
                                    * self.settings.distance_scale_km
                                )
                            )
                        ),
                    ),
                    Second(Scalar(elapsed_time)),
                )

                true_anomaly = true_anomaly_from_eccentric_anomaly(
                    eccentric_anomaly_obj,
                    elements.eccentricity,
                )

                coordinates = self.orbiting_body_coordinates(
                    index,
                    eccentric_anomaly_obj,
                )

                distance_km = (
                    calculate_distance(
                        Coordinate2D(coordinates.x, coordinates.y),
                        self.central_point,
                    )
                    * self.settings.distance_scale_km
                )

                distance_m = distance_km * 1000

                velocity_m_s = vis_viva(
                    gravitational_parameter=gravitational_parameter(
                        Mass(self.central_body_mass_kg),
                        Mass(self.orbiting_body_mass_kg[index]),
                    ),
                    orbit_radius=Distance(Scalar(distance_m)),
                    semi_major_axis=self.semi_major_axis_metres(index),
                )

                velocity_km_s = velocity_m_s / 1000

                body_x_updates.append([coordinates.x])
                body_y_updates.append([coordinates.y])

                label_x_updates.append([coordinates.x])
                label_y_updates.append([coordinates.y])
                label_text_updates.append(
                    [
                        f"{self.orbiting_body_names[index]}<br>"
                        f"r = {distance_km:.2f} km <br>"
                        f"v = {velocity_km_s:.2f} km/s <br>"
                        f"ta = {true_anomaly:.2f} rad <br>"
                        f"t = {elapsed_time:.2f} s"
                    ]
                )

                if self.orbiting_body_is_satellite[index]:
                    position_vector = position_vector_from_coordinates(
                        Coordinate3D(coordinates.x, coordinates.y, Scalar(0)),
                        Coordinate3D(
                            self.central_point.x,
                            self.central_point.y,
                            Scalar(0),
                        ),
                    )

                    velocity_vector = self.velocity_vector_at_time(
                        index,
                        elapsed_time,
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
                        xs, ys = self.vector_line(coordinates, direction_vector)

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
                        body_trace_indices
                        + label_trace_indices
                        + vector_update_indices,
                    ],
                    label=f"{fraction:.2f}",
                )
            )

        return steps

    def velocity_vector_at_time(
        self,
        index: int,
        elapsed_time: float,
    ) -> VelocityVector:
        period = orbital_period(
            self.semi_major_axis_metres(index),
            gravitational_parameter(
                Mass(self.central_body_mass_kg),
                Mass(self.orbiting_body_mass_kg[index]),
            ),
        )

        delta_time = period / 10000

        elements = self.orbital_elements[index]

        scaled_elements = replace(
            elements,
            semi_major_axis=SemiMajorAxis(
                Distance(
                    Scalar(
                        self.orbital_elements[index].semi_major_axis
                        * self.settings.distance_scale_km
                    )
                )
            ),
        )

        current_coordinates = self.orbiting_body_coordinates(
            index,
            eccentric_anomaly_at_time(
                scaled_elements,
                Second(Scalar(elapsed_time)),
            ),
        )

        next_coordinates = self.orbiting_body_coordinates(
            index,
            eccentric_anomaly_at_time(
                scaled_elements,
                Second(Scalar(elapsed_time + delta_time)),
            ),
        )
        return VelocityVector(
            Velocity(Scalar((next_coordinates.x - current_coordinates.x) / delta_time)),
            Velocity(Scalar((next_coordinates.y - current_coordinates.y) / delta_time)),
            Velocity(Scalar(0)),
        )

    def vector_line(
        self,
        start: Coordinate2D,
        direction: Vector3D,
    ) -> tuple[list[float], list[float]]:
        length = self.direction_vector_length()

        return (
            [start.x, start.x + direction.x * length],
            [start.y, start.y + direction.y * length],
        )

    def direction_vector_length(self) -> float:
        plot_range_x = self.plot_max.x - self.plot_min.x
        plot_range_y = self.plot_max.y - self.plot_min.y

        return min(plot_range_x, plot_range_y) * 0.06

    def ellipse_centre(self, index: int) -> Coordinate2D:
        elements = self.orbital_elements[index]
        c = calculate_foci(elements.semi_major_axis, elements.eccentricity)[0]

        return Coordinate2D(
            self.central_point.x + c.x,
            self.central_point.y,
        )

    def orbiting_body_coordinates(
        self,
        index: int,
        eccentric_anomaly: EccentricAnomaly,
    ) -> Coordinate2D:
        elements = self.orbital_elements[index]

        centre = self.ellipse_centre(index)

        unrotated = translate_ellipse_coordinate(
            centre,
            elements.semi_major_axis,
            semi_minor_axis(
                self.orbital_elements[index].semi_major_axis,
                self.orbital_elements[index].eccentricity,
            ),
            eccentric_anomaly,
        )

        return rotate_around_point(
            unrotated,
            self.central_point,
            elements.argument_of_periapsis,
        )
