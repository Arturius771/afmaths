from abc import ABC, abstractmethod

from afmaths.physics.space.astronomy.conversion_helpers import (
    fulldate_to_string,
    python_datetime_to_fulldate,
)
from afmaths.visualisations.helpers import (
    BodyPlotConfig,
    OrbitPlotSettings,
    add_body_surface,
    add_orbiting_body_to_traces,
    make_3d_orbit_figure,
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
