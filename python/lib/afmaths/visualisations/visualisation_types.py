"""Shared types used by AFMaths Plotly visualisations.

Keep models here; plotting logic stays in individual visualisation files.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from astronomy_types import (
    Coordinate2D,
    Distance,
    Epoch,
    GravitationalParameter,
    OrbitalElements,
    Scalar,
    Second,
)

from afmaths.constants import TWO_PI
from afmaths.physics.space.external.horizons_api import HorizonsCommandTarget
from afmaths.physics.space.type_conversion_helpers import seconds_from_python_timedelta

ReferenceFrame = Literal["ICRF", "GCRF", "ITRF"]
OrbitDescription = OrbitalElements | str


class OrbitSource(StrEnum):
    TLE = "tle"
    HORIZONS = "horizons"
    ELEMENTS = "elements"


@dataclass(frozen=True)
class Orbit:
    name: str
    epoch: Epoch
    description: OrbitDescription


@dataclass(frozen=True)
class PlotOrbital2DSettings:
    distance_scale: float
    plot_width: int = 800
    plot_height: int = 800
    plot_min_x: float = -35
    plot_min_y: float = -35
    plot_max_x: float = 35
    plot_max_y: float = 35
    slider_steps: int = 51
    orbit_points: int = 200

    def __post_init__(self) -> None:
        if self.distance_scale <= 0:
            raise ValueError("distance_scale must be greater than 0.")
        if self.plot_width <= 0 or self.plot_height <= 0:
            raise ValueError("plot dimensions must be greater than 0.")
        if self.plot_min_x >= self.plot_max_x or self.plot_min_y >= self.plot_max_y:
            raise ValueError("plot minimums must be smaller than plot maximums.")
        if self.slider_steps < 2:
            raise ValueError("slider_steps must be at least 2.")
        if self.orbit_points < 2:
            raise ValueError("orbit_points must be at least 2.")


@dataclass(frozen=True)
class PlotNode:
    name: str
    coordinate: Coordinate2D
    text: str | None = None
    colour: str = "red"
    size: int = 12
    symbol: str = "x"
    marker_only: bool = False


@dataclass(frozen=True)
class PlotPerifocalOrbitLine:
    name: str
    orbital_elements: OrbitalElements
    colour: str = "grey"
    start_eccentric_anomaly: float = 0.0
    end_eccentric_anomaly: float = TWO_PI
    show_secondary_focus: bool = False


@dataclass(frozen=True)
class OrbitPlotSettings:
    centre: HorizonsCommandTarget | None
    gravitational_parameter: GravitationalParameter
    distance_scale: float
    orbit_points: int
    start_time: datetime.datetime
    time_offset: datetime.timedelta = datetime.timedelta(
        days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0
    )
    add_prediction_to_orbit: bool = False

    def __post_init__(self) -> None:
        if self.distance_scale <= 0:
            raise ValueError("distance_scale must be greater than 0.")
        if self.orbit_points < 2:
            raise ValueError("orbit_points must be at least 2.")

    @property
    def stop_time(self) -> datetime.datetime:
        return self.start_time + self.time_offset

    @property
    def time_offset_seconds(self) -> Second:
        return Second(Scalar(seconds_from_python_timedelta(self.time_offset)))


@dataclass(frozen=True)
class BodyPlotConfig:
    name: str
    target_object: HorizonsCommandTarget | OrbitalElements
    radius: Distance  # metres
    radius_scale: float


@dataclass(frozen=True)
class PlotOriginConfig:
    name: str
    target: HorizonsCommandTarget | None
    radius: Distance
    gravitational_parameter: GravitationalParameter
    radius_scale: float
    distance_scale: float
    opacity: float = 0.7
    texture_path: Path | None = None


@dataclass(frozen=True)
class PlotCoordinateSystem:
    """The coordinate-system properties the visualiser actually implements."""

    name: ReferenceFrame
    axes: str
    is_inertial: bool


@dataclass(frozen=True)
class OrbitingBody2D:
    name: str
    radius_m: float
    mass_kg: float
    elements: OrbitalElements
    is_satellite: bool = False
    colour: str | None = None


@dataclass(frozen=True)
class PlotOptions:
    distance_scale: float | None = None
    plot_width: int | None = None
    plot_height: int | None = None
    plot_min_x: float | None = None
    plot_min_y: float | None = None
    plot_max_x: float | None = None
    plot_max_y: float | None = None
    slider_steps: int | None = None
    plot_points: int | None = None
    lines: bool | None = None
    show_orbit_markers: bool | None = None
    dashboard_columns: int = 1
    output_path: Path | None = None
    reference_frame: ReferenceFrame = "ICRF"
    central_body: HorizonsCommandTarget | PlotOriginConfig = HorizonsCommandTarget.EARTH
    horizons_bodies: list[HorizonsCommandTarget] | None = None
    include_default_system_bodies: bool = True

    def __post_init__(self) -> None:
        if self.distance_scale is not None and self.distance_scale <= 0:
            raise ValueError("distance_scale must be greater than 0.")
        if self.plot_width is not None and self.plot_width <= 0:
            raise ValueError("plot_width must be greater than 0.")
        if self.plot_height is not None and self.plot_height <= 0:
            raise ValueError("plot_height must be greater than 0.")
        if self.slider_steps is not None and self.slider_steps < 2:
            raise ValueError("slider_steps must be at least 2.")
        if self.plot_points is not None and self.plot_points < 2:
            raise ValueError("plot_points must be at least 2.")
        if self.dashboard_columns < 1:
            raise ValueError("dashboard_columns must be at least 1.")
