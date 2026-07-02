import unittest

import plotly.graph_objects as go
from astronomy_types import Coordinate2D, Distance, Scalar, Vector3D

from afmaths.visualisations.helpers import (
    PlotOrbital2DSettings,
    add_plot_node,
    add_plot_nodes,
    central_body_radius_plot,
    direction_vector_length,
    distance_to_scale_distance,
    plot_centre,
    plot_max,
    plot_min,
    scale_distance_to_distance,
    scaled_radius,
    vector_line,
)


class PlotHelperTests(unittest.TestCase):
    def test_scale_distance_to_distance(self) -> None:
        result = scale_distance_to_distance(Distance(Scalar(2.5)), 100.0)

        self.assertAlmostEqual(float(result), 250.0)

    def test_distance_to_scale_distance(self) -> None:
        result = distance_to_scale_distance(Distance(Scalar(250.0)), 100.0)

        self.assertAlmostEqual(float(result), 2.5)

    def test_plot_bounds_and_centre(self) -> None:
        settings = PlotOrbital2DSettings(
            distance_scale=10.0,
            plot_min_x=-10.0,
            plot_min_y=20.0,
            plot_max_x=30.0,
            plot_max_y=100.0,
        )

        self.assertEqual(plot_min(settings).x, -10.0)
        self.assertEqual(plot_min(settings).y, 20.0)
        self.assertEqual(plot_max(settings).x, 30.0)
        self.assertEqual(plot_max(settings).y, 100.0)
        self.assertEqual(plot_centre(settings).x, 10.0)
        self.assertEqual(plot_centre(settings).y, 60.0)

    def test_central_body_radius_plot(self) -> None:
        result = central_body_radius_plot(6_371.0, 1_000.0)

        self.assertAlmostEqual(float(result), 6.371)

    def test_scaled_radius(self) -> None:
        result = scaled_radius(
            radius_km=1_000.0,
            radius_scale=5.0,
            distance_scale_km=10_000.0,
        )

        self.assertAlmostEqual(float(result), 0.5)

    def test_vector_line_uses_six_percent_of_shortest_plot_axis(self) -> None:
        settings = PlotOrbital2DSettings(
            distance_scale=1.0,
            plot_min_x=0,
            plot_min_y=0,
            plot_max_x=100,
            plot_max_y=50,
        )

        self.assertAlmostEqual(direction_vector_length(settings), 3.0)

        xs, ys = vector_line(
            Coordinate2D(Scalar(10), Scalar(20)),
            Vector3D(x=2, y=-1, z=0),
            settings,
        )

        self.assertEqual(xs, [10, 16])
        self.assertEqual(ys, [20, 17])


if __name__ == "__main__":
    unittest.main()
