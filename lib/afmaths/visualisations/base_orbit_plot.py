from abc import ABC, abstractmethod
import math

from afmaths.constants import Mass
from afmaths.geometry import calculate_distance, calculate_foci, semi_minor_axis
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    fulldate_to_string,
    python_datetime_to_fulldate,
)
from afmaths.physics.space.celestial_mechanics import (
    generate_angles_on_circle,
    gravitational_parameter,
    kepler_equation,
    time_since_periapsis,
    translate_ellipse_coordinate,
    true_anomaly_from_eccentric_anomaly,
    vis_viva,
)
from afmaths.visualisations.helpers import (
    BodyPlotConfig,
    OrbitPlot2DSettings,
    OrbitPlotSettings,
    add_body_surface,
    add_orbiting_body_to_traces,
    figure_circle,
    figure_layout,
    figure_orbit_line,
    figure_planetary_body,
    figure_plot_centre,
    figure_slider,
    generate_orbital_slider_data,
    make_3d_orbit_figure,
    plot_foci_positions,
    rotate_around_point,
)

import plotly.graph_objects as go
from astronomy_types import (
    Anomaly,
    Coordinate2D,
    Distance,
    EccentricAnomaly,
    GravitationalParameter,
    OrbitalElements,
    Radians,
    Scalar,
    SemiMajorAxis,
    SemiMinorAxis,
    Vector2D,
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
            add_orbiting_body_to_traces(
                traces,
                body,
                self.settings,
            )

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
        return Coordinate2D(
            self.plot_max.x / 2,
            self.plot_max.y / 2,
        )

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

    def gravitational_parameter(self, index: int) -> GravitationalParameter:
        return gravitational_parameter(
            Mass(self.central_body_mass_kg),
            Mass(self.orbiting_body_mass_kg[index]),
        )

    def semi_minor_axis(self, index: int) -> SemiMinorAxis:
        return semi_minor_axis(
            self.orbital_elements[index].semi_major_axis,
            self.orbital_elements[index].eccentricity,
        )

    def primary_coordinates(self, index: int) -> Coordinate2D:
        return self.central_point

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
        ):
            raise ValueError(
                "orbiting_body_names, orbiting_body_radius_km, "
                "orbiting_body_mass_kg, and orbital_elements must have the same length"
            )

    def add_orbiting_body(
        self, fig: go.Figure, index: int
    ) -> tuple[go.Figure, int, int]:
        body_trace_index = len(tuple(fig.data))

        coordinates = self.initial_orbiting_body_coordinates(index)

        fig.add_trace(
            go.Scatter(
                x=[coordinates.x],
                y=[coordinates.y],
                mode="markers",
                name=self.orbiting_body_names[index],
                marker=dict(
                    size=self.orbiting_body_radius_plot(index) + 5,
                    color="grey",
                    line=dict(color="grey", width=2),
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

        fig = figure_orbit_line(
            fig,
            self.orbit_line_coordinates(index),
            f"{self.orbiting_body_names[index]} orbit",
        )

        fig = figure_circle(
            fig,
            plot_foci_positions(
                self.ellipse_centre(index), self.orbital_elements[index], 1
            ),
            Distance(Scalar(0.1)),
            "red",
            "red",
        )

        return fig, body_trace_index, label_trace_index

    def build_figure(self) -> go.Figure:
        self.validate_orbiting_bodies()

        fig = go.Figure()

        body_trace_indices: list[int] = []
        label_trace_indices: list[int] = []

        for index in range(len(self.orbital_elements)):
            fig, body_trace_index, label_trace_index = self.add_orbiting_body(
                fig, index
            )
            body_trace_indices.append(body_trace_index)
            label_trace_indices.append(label_trace_index)

        fig = figure_planetary_body(
            fig,
            self.primary_coordinates(0),
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
            ),
        )

        fig = figure_plot_centre(
            fig,
            self.central_point,
            Distance(Scalar(0.1)),
        )

        fig.update_layout(title=self.make_title())

        return fig

    def orbit_line_coordinates(self, index: int) -> list[Coordinate2D]:
        return [
            self.orbiting_body_coordinates(
                index,
                EccentricAnomaly(Anomaly(Radians(Scalar(angle)))),
            )
            for angle in generate_angles_on_circle(200)
        ]

    def make_title(self) -> str:
        return self.title_prefix

    def show(self) -> None:
        self.build_figure().show()

    def orbital_period_seconds(self, index: int) -> float:
        elements = self.orbital_elements[index]

        semi_major_axis_km = elements.semi_major_axis * self.settings.distance_scale_km
        semi_major_axis_m = semi_major_axis_km * 1000

        mu = self.gravitational_parameter(index)

        return 2 * math.pi * math.sqrt((semi_major_axis_m**3) / mu)

    def eccentric_anomaly_at_time(
        self, index: int, time_seconds: float
    ) -> EccentricAnomaly:
        elements = self.orbital_elements[index]

        semi_major_axis_km = elements.semi_major_axis * self.settings.distance_scale_km
        semi_major_axis_m = semi_major_axis_km * 1000

        mu = self.gravitational_parameter(index)

        mean_motion = math.sqrt(mu / semi_major_axis_m**3)
        mean_anomaly = mean_motion * time_seconds

        # Keep the body on the visible ellipse, but do not force it to complete
        # exactly one orbit during the slider cycle.
        mean_anomaly = mean_anomaly % (2 * math.pi)

        eccentricity = elements.eccentricity

        eccentric_anomaly = mean_anomaly

        for _ in range(20):
            eccentric_anomaly = eccentric_anomaly - (
                eccentric_anomaly
                - eccentricity * math.sin(eccentric_anomaly)
                - mean_anomaly
            ) / (1 - eccentricity * math.cos(eccentric_anomaly))

        return EccentricAnomaly(Anomaly(Radians(Scalar(eccentric_anomaly))))

    def generate_combined_orbital_slider_data(
        self,
        body_trace_indices: list[int],
        label_trace_indices: list[int],
    ) -> list[dict]:
        steps = []

        reference_period = self.orbital_period_seconds(0)

        for step_index in range(self.num_steps):
            fraction = step_index / (self.num_steps - 1)
            elapsed_time = reference_period * fraction

            body_x_updates = []
            body_y_updates = []

            label_x_updates = []
            label_y_updates = []
            label_text_updates = []

            for index in range(len(self.orbital_elements)):
                elements = self.orbital_elements[index]
                b = self.semi_minor_axis(index)
                primary_coordinates = self.primary_coordinates(index)

                eccentric_anomaly_obj = self.eccentric_anomaly_at_time(
                    index,
                    elapsed_time,
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
                        primary_coordinates,
                    )
                    * self.settings.distance_scale_km
                )

                distance_m = distance_km * 1000

                semi_major_axis_km = (
                    elements.semi_major_axis * self.settings.distance_scale_km
                )
                semi_major_axis_m = semi_major_axis_km * 1000

                velocity_m_s = vis_viva(
                    orbit_radius=Distance(Scalar(distance_m)),
                    semi_major_axis=SemiMajorAxis(Distance(Scalar(semi_major_axis_m))),
                    gravitational_parameter=self.gravitational_parameter(index),
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

            steps.append(
                dict(
                    method="restyle",
                    args=[
                        {
                            "x": body_x_updates + label_x_updates,
                            "y": body_y_updates + label_y_updates,
                            "text": [[] for _ in body_trace_indices]
                            + label_text_updates,
                        },
                        body_trace_indices + label_trace_indices,
                    ],
                    label=f"{fraction:.2f}",
                )
            )

        return steps

    def ellipse_centre(self, index: int) -> Coordinate2D:
        elements = self.orbital_elements[index]

        c = calculate_foci(
            elements.semi_major_axis,
            elements.eccentricity,
        )[0].x

        return Coordinate2D(
            self.central_point.x + c,
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
            self.semi_minor_axis(index),
            eccentric_anomaly,
        )

        return rotate_around_point(
            unrotated,
            self.central_point,  # Earth/focus
            elements.argument_of_perigee,
        )
