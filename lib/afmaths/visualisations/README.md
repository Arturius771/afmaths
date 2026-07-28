# AFMaths visualisation launcher

All visualisation modules now build and return `plotly.graph_objects.Figure` objects. They do not open browser windows themselves and contain no `main()` entry points.

Use the shared launcher:

```bash
python visualisation_launcher.py "control room" --norad-id 25544 --orbits 16 --point-interval 30
python visualisation_launcher.py "ground track" --norad-id 25544 --orbits 3 --point-interval 30
python visualisation_launcher.py "solar system"
python visualisation_launcher.py "hohmann transfer"
```

The control room creates four independent Plotly figures in one responsive 2×2 HTML dashboard:

1. ITRS 3D orbit
2. TLE-epoch ground track
3. Current-position ground track
4. Multi-satellite Earth-centred 3D view

Individual use remains possible:

```python
from solar_system_3d import build_solar_system_3d_figure

build_solar_system_3d_figure().show()
```
