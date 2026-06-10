from abc import ABC, abstractmethod

from afmaths.physics.space.astronomy.type_conversion_helpers import (
    fulldate_to_string,
    python_datetime_to_fulldate,
)
from afmaths.physics.space.celestial_mechanics import translate_ellipse_coordinate
from afmaths.visualisations.helpers import (
    BodyPlotConfig,
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
)

import plotly.graph_objects as go
from astronomy_types import (
    Anomaly,
    Distance,
    EccentricAnomaly,
    OrbitalElements,
    Radians,
    Scalar,
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
    def orbiting_body(self) -> list[OrbitalElements]:
        pass

    def build_figure(self) -> go.Figure:
        return figure_plot_centre(
            figure_slider(
                figure_layout(
                    figure_circle(
                        figure_planetary_body(
                            figure_orbit_line(
                                figure_planetary_body(
                                    go.Figure(),
                                    translate_ellipse_coordinate(
                                        central_point,
                                        self.orbiting_body[0].semi_major_axis,
                                        semi_minor_axis,
                                        EccentricAnomaly(Anomaly(Radians(Scalar(0)))),
                                    ),
                                    Distance(Scalar(SECONDARY_BODY_RADIUS_PLOT)),
                                    SECONDARY_BODY_LABEL,
                                    "white",
                                    "grey",
                                    moveable=True,
                                ),
                                central_point,
                                self.orbiting_body[0],
                            ),
                            primary_coordinates,
                            Distance(Scalar(PRIMARY_BODY_RADIUS_PLOT)),
                            self.central_body_name,
                            "Black",
                            "blue",
                            "green",
                        ),
                        plot_foci_positions(central_point, self.orbiting_body[0], 1),
                        Distance(Scalar(0.1)),
                        "red",
                        "red",
                    ),
                    PLOT_WIDTH,
                    PLOT_HEIGHT,
                    PLOT_MIN,
                    PLOT_MAX,
                ),
                generate_orbital_slider_data(
                    NUM_STEPS,
                    central_point,
                    primary_coordinates,
                    self.orbiting_body[0],
                    semi_minor_axis,
                    DISTANCE_SCALE_KM,
                    GRAVITATIONAL_PARAMETER,
                ),
            ),
            central_point,
            Distance(Scalar(0.1)),
        )

    def make_title(self) -> str:
        return (
            self.title_prefix
            + ": "
            + fulldate_to_string(python_datetime_to_fulldate(self.settings.start_time))
        )

    def show(self) -> None:
        fig = self.build_figure()
        # self.make_title(),

        fig.show()
