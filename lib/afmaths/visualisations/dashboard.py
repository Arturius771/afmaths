from __future__ import annotations

from collections.abc import Sequence
from html import escape
from pathlib import Path
import tempfile
import webbrowser

import plotly.graph_objects as go
import plotly.io as pio


def write_visualisation_dashboard(
    figures: Sequence[go.Figure],
    title: str = "AFMaths Visualisations",
    columns: int = 2,
    output_path: Path | None = None,
) -> Path:
    """Write independent Plotly figures into one responsive HTML dashboard."""
    if not figures:
        raise ValueError("At least one figure is required.")
    if columns < 1:
        raise ValueError("columns must be at least 1.")

    if output_path is None:
        with tempfile.NamedTemporaryFile(
            prefix="afmaths-visualisations-",
            suffix=".html",
            delete=False,
        ) as temporary_file:
            output_path = Path(temporary_file.name)

    panels: list[str] = []
    for index, figure in enumerate(figures):
        panels.append(
            '<section class="plot-panel">'
            + pio.to_html(
                figure,
                full_html=False,
                include_plotlyjs=True if index == 0 else False,
                config={"responsive": True, "displaylogo": False},
                default_width="100%",
                default_height="100%",
            )
            + "</section>"
        )

    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    * {{ box-sizing: border-box; }}
    html, body {{ margin: 0; min-height: 100%; }}
    body {{
      padding: 16px;
      background: #eef1f5;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    h1 {{ margin: 0 0 16px; font-size: 24px; }}
    .dashboard {{
      display: grid;
      grid-template-columns: repeat({columns}, minmax(0, 1fr));
      gap: 16px;
    }}
    .plot-panel {{
      min-width: 0;
      height: min(620px, 72vh);
      overflow: hidden;
      background: white;
      border: 1px solid #d8dde5;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    .plot-panel > div,
    .plot-panel .plotly-graph-div {{
      width: 100% !important;
      height: 100% !important;
    }}
    @media (max-width: 1100px) {{
      .dashboard {{ grid-template-columns: 1fr; }}
      .plot-panel {{ height: 600px; }}
    }}
  </style>
</head>
<body>
  <h1>{escape(title)}</h1>
  <main class="dashboard">{''.join(panels)}</main>
  <script>
    const resizePlots = () => document
      .querySelectorAll('.plotly-graph-div')
      .forEach(plot => Plotly.Plots.resize(plot));
    window.addEventListener('load', resizePlots);
    window.addEventListener('resize', resizePlots);
  </script>
</body>
</html>
"""

    output_path.write_text(document, encoding="utf-8")
    return output_path


def show_visualisation_dashboard(
    figures: Sequence[go.Figure],
    title: str = "AFMaths Visualisations",
    columns: int = 2,
    output_path: Path | None = None,
) -> Path:
    """Write a dashboard and open it in the default browser."""
    dashboard_path = write_visualisation_dashboard(
        figures=figures,
        title=title,
        columns=columns,
        output_path=output_path,
    )
    webbrowser.open(dashboard_path.resolve().as_uri())
    return dashboard_path
