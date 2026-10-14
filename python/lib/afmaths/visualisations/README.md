# AFMaths Visualisations

Interactive astrodynamics and orbital-mechanics visualisations built with Plotly.

Visualisations are launched from the command line by passing the visualisation name:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py <visualisation>
```

For example:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py keplers_ellipse_2d
```

Names containing underscores can also be written with spaces or hyphens:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py "solar system"
python lib/afmaths/visualisations/visualisation_launcher.py solar-system
python lib/afmaths/visualisations/visualisation_launcher.py orbit-3d --centre SUN
```

---

## Orbit data sources

The launcher resolves orbit inputs from one of three sources and passes the resolved data to each self-contained plot:

- `tle` — fetches TLE data from Space-Track using one or more NORAD IDs.

- `horizon` — fetches state vectors from JPL Horizons and converts them to orbital elements.

- `elements` — uses orbital elements supplied directly on the command line.

Select the source with `--source`:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source tle \
  --norad-id 25544
```

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source horizon \
  --target MOON
```

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source elements \
  --inclination 0.900590 \
  --semi-major-axis 6778000 \
  --eccentricity 0.001
```

`tle` is the default source. If an orbit-based visualisation is launched without `--source` or `--norad-id`, the ISS is used by default.

The source abstraction is used by:

- `control_room`

- `ground_track`

- `current_ground_track`

- `orbit_3d`

The remaining visualisations use their own fixed or specialised inputs.

Orbital-element angles are expressed in radians throughout the visualisation package and CLI.

---

## Available visualisations

### Control room

#### `control_room`

Launches the multi-plot satellite control room.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py controlroom
```

By default, the TLE source and ISS are used.

A different satellite can be selected with:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --source tle \
  --norad-id 20580
```

Multiple satellites can be supplied:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --source tle \
  --norad-id 25544 20580
```

The control room can also use Horizons:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --source horizon \
  --target MOON
```

The general propagation duration and current-position propagation duration can be configured independently:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --norad-id 25544 \
  --orbits 3 \
  --current-orbits 2
```

Custom elements can also be supplied:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --source elements \
  --inclination 0.900590 \
  --right-ascension-of-ascending-node 0.523599 \
  --argument-of-periapsis 0.785398 \
  --semi-major-axis 6778000 \
  --eccentricity 0.001 \
  --true-anomaly 0 \
  --orbits 1 \
  --current-orbits 1
```

The control room's inertial 3D panel accepts the same system options as `orbit_3d`. `--reference-frame ICRF` or `GCRF` selects that panel's frame, while the separate Earth-fixed panel remains ITRF and satellite-only.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --centre SUN \
  --body EARTH MARS JUPITER \
  --reference-frame ICRF
```

---

## Satellite and orbit visualisations

### `ground_track`

Displays an orbit's propagated Earth ground track. Orbit markers are displayed on this plot.

TLE:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source tle \
  --norad-id 25544
```

Horizons:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source horizon \
  --target MOON
```

Custom orbital elements:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source elements \
  --inclination 0.900590 \
  --right-ascension-of-ascending-node 0.523599 \
  --argument-of-periapsis 0.785398 \
  --semi-major-axis 6778000 \
  --eccentricity 0.001 \
  --true-anomaly 0
```

The propagation duration can be specified in orbits:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --norad-id 25544 \
  --orbits 4
```

The legacy names `ground_track_tle` and `ground_track_custom` are retained as aliases for `ground_track`.

---

### `current_ground_track`

Displays the propagated ground track starting from the orbit's current position. The current implementation also displays the configured ground station, apogee, perigee, and current position.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py current_ground_track \
  --source tle \
  --norad-id 25544
```

It can use the same alternative sources:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py current_ground_track \
  --source elements \
  --inclination 0.900590 \
  --semi-major-axis 6778000
```

Legacy alias:

```text
ground_track_current
```

---

### `orbit_3d`

Builds the common 3D orbit view for Horizons bodies, satellites, or both. The default is the Earth-Moon system in GCRF. Each orbiting body's legend entry toggles its orbit, body, and prediction together.

`--reference-frame` accepts `ICRF`, `GCRF`, and `ITRF`. ICRF and GCRF currently share the inertial propagation path. ITRF transforms Earth-centred satellite tracks into Earth-fixed coordinates, so it requires a satellite orbit and does not currently support Horizons bodies.

Earth-Moon (default):

```bash
python lib/afmaths/visualisations/visualisation_launcher.py orbit_3d
```

Heliocentric solar system:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py orbit_3d \
  --centre SUN \
  --reference-frame ICRF
```

Select only specific Horizons bodies:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py orbit_3d \
  --centre SUN \
  --body EARTH MARS JUPITER
```

Satellite-only Earth-fixed view:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py orbit_3d \
  --source tle \
  --norad-id 25544 20580 \
  --reference-frame ITRF \
  --no-system-bodies \
  --orbits 5
```

The legacy names `moon_earth_3d`, `moon_earth`, `solar_system_3d`, `solar_system`, `satellite_earth_3d`, `satellite_earth`, `itrf_orbit_3d`, `itrf`, and `itrf_custom` remain aliases for `orbit_3d`.

---

## Orbital mechanics visualisations

### `keplers_ellipse_2d`

Displays the default 2D Keplerian ellipse visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py keplers_ellipse_2d
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py kepler
```

---

### `two_body_2d`

Displays the default 2D two-body problem visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py two_body_2d
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py two_body
```

---

### `phase_orbit_2d`

Displays the default 2D perifocal phase-orbit visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py phase_orbit_2d
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py phase_orbit
```

---

### `velocity_time`

Displays the velocity-versus-time visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py velocity_time
```

---

### `newton_iteration`

Displays the Newton iteration visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py newton_iteration
```

---

## Orbital manoeuvre visualisations

### `hohmann_transfer_2d`

Displays the default 2D perifocal Hohmann transfer visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py hohmann_transfer_2d
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py hohmann_transfer
```

---

### `hohmann_tradeoff`

Displays the Hohmann transfer trade-off visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py hohmann_tradeoff
```

---

## Collision detection

### `collision_detection`

Displays the collision-detection visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py collision_detection
```

---

## Command-line options

The launcher supports the following options:

| Option                                    | Description                                                    |

| ----------------------------------------- | -------------------------------------------------------------- |

| `name`                                    | Name or alias of the visualisation to launch                   |

| `--source {tle,horizon,elements}`         | Orbit data source for source-backed visualisations             |

| `--norad-id ID [ID ...]`                  | One or more NORAD catalogue IDs for `--source tle`             |

| `--target TARGET [TARGET ...]`            | One or more JPL Horizons targets for `--source horizon`        |

| `--orbits N`                              | Number of orbits to propagate                                  |

| `--tle-orbits N`                          | Backwards-compatible alias for `--orbits`                      |

| `--current-orbits N`                      | Number of current-position orbits used by the control room     |

| `--inclination RAD`                       | Orbital inclination in radians                                 |

| `--right-ascension-of-ascending-node RAD` | RAAN in radians                                                |

| `--argument-of-periapsis RAD`             | Argument of periapsis in radians                               |

| `--semi-major-axis M`                     | Semi-major axis in metres                                      |

| `--eccentricity E`                        | Orbital eccentricity                                           |

| `--true-anomaly RAD`                      | True anomaly in radians                                        |

| `--reference-frame {ICRF,GCRF,ITRF}`       | Reference frame used by `orbit_3d`                             |

| `--centre {EARTH,SUN}`                     | Central body used by `orbit_3d`                                |

| `--body TARGET [TARGET ...]`               | Horizons bodies displayed by `orbit_3d`                        |

| `--system-bodies` / `--no-system-bodies`   | Include or omit default Moon/planet bodies in `orbit_3d`       |

### Plot settings

Plot settings can be overridden from the same launcher. Flags only affect visualisations that support the corresponding setting; otherwise the existing visualisation default is retained.

| Option | Description |

| --- | --- |

| `--distance-scale M` | Physical distance in metres represented by one plot unit where supported |

| `--plot-width PX` | 2D plot width |

| `--plot-height PX` | 2D plot height |

| `--plot-min-x VALUE` | 2D plot minimum X value |

| `--plot-min-y VALUE` | 2D plot minimum Y value |

| `--plot-max-x VALUE` | 2D plot maximum X value |

| `--plot-max-y VALUE` | 2D plot maximum Y value |

| `--slider-steps N` | Slider resolution for interactive 2D plots |

| `--plot-points N` | Sampling resolution for orbit and ground-track plots |

| `--lines` / `--no-lines` | Enable or disable lines between ground-track samples |

| `--show-orbit-markers` / `--no-show-orbit-markers` | Enable or disable ground-track orbit markers |

| `--dashboard-columns N` | Number of control-room dashboard columns |

| `--output-path PATH` | Write the control-room dashboard to a specific HTML path |

For example:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py kepler \
  --distance-scale 75 \
  --plot-width 900 \
  --plot-height 700 \
  --plot-points 1000
```

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --norad-id 25544 \
  --plot-points 1000 \
  --dashboard-columns 3 \
  --output-path control-room.html
```

Run:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py --help
```

to see the command-line help.

### Custom orbital elements

Custom elements are enabled with:

```text
--source elements
```

Any element that is not supplied uses the corresponding value from `EXAMPLE_ELEMENTS`.

For example, to override only inclination and semi-major axis:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source elements \
  --inclination 1.221730 \
  --semi-major-axis 7000000
```

---

## Quick examples

Launch the Kepler ellipse:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py kepler
```

Display the ISS ground track:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --norad-id 25544
```

Display three ISS orbits:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --norad-id 25544 \
  --orbits 3
```

Display multiple satellites in ITRF:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py orbit_3d \
  --norad-id 25544 20580 \
  --reference-frame ITRF \
  --no-system-bodies
```

Display a Horizons target:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source horizon \
  --target MOON
```

Launch the control room for the ISS:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --norad-id 25544
```

Visualise a custom circular orbit:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py ground_track \
  --source elements \
  --inclination 0.785398 \
  --right-ascension-of-ascending-node 0 \
  --argument-of-periapsis 0 \
  --semi-major-axis 7000000 \
  --eccentricity 0 \
  --true-anomaly 0
```

Interesting polar orbit:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py control_room \
  --source elements \
  --inclination 1.553343 \
  --right-ascension-of-ascending-node 4.014257 \
  --argument-of-periapsis 0 \
  --semi-major-axis 42168100 \
  --eccentricity 0.001 \
  --true-anomaly 0 \
  --orbits 1 \
  --current-orbits 1
```

---

## Visualisation name reference

| Visualisation          | Alias                                     |

| ---------------------- | ----------------------------------------- |

| `control_room`         | `controlroom`                             |

| `orbit_3d`              | `moon_earth`, `moon_earth_3d`, `solar_system`, `solar_system_3d`, `satellite_earth`, `satellite_earth_3d`, `itrf`, `itrf_orbit_3d`, `itrf_custom` |

| `ground_track`         | `ground_track_tle`, `ground_track_custom` |

| `current_ground_track` | `ground_track_current`                    |

| `collision_detection`  | —                                         |

| `hohmann_tradeoff`     | —                                         |

| `hohmann_transfer_2d`  | `hohmann_transfer`                        |

| `keplers_ellipse_2d`   | `kepler`                                  |

| `newton_iteration`     | —                                         |

| `phase_orbit_2d`       | `phase_orbit`                             |

| `two_body_2d`          | `two_body`                                |

| `velocity_time`        | —                                         |


## Architecture: PRY (Prefer Repetition Yourself)

- `visualisation_launcher.py` is the only visualisation module that imports other visualisation modules. It owns command-line arguments, orbit source resolution, control-room composition, and dashboard HTML output.
- Plot modules only import the AFMaths/astronomy domain library, Plotly, and Python/third-party dependencies needed for their own display. They do not import `base.py`, `helpers.py`, or one another.
- Plot-specific geometrical conversions, display scales, and Plotly traces remain next to the plot they belong to. Some repeated plotting logic is intentional, allowing a wholly different system (such as Kerbal) to be added without changing a shared graphical base layer.
- To add a new visualisation, create a standalone file with a `build_*_figure(...) -> go.Figure` entry point and register it in the launcher.
- `base.py`, `helpers.py`, `orbit_source.py`, `dashboard.py`, and `control_room.py` have been removed as standalone modules. The launcher retains their orchestration responsibilities.

## Shared types

`visualisation_types.py` is the single source of truth for cross-visualisation
configuration and data types (e.g. `PlotOrbital2DSettings`, `PlotNode`,
`PlotPerifocalOrbitLine`, `Orbit`, and 3D plot settings). Import those types
from this module. Plotting functions and calculations remain in their own
visualisation modules; no generic plotting helper layer is required.


## Arbitrary 3D origin spheres

The Python API accepts a `PlotOriginConfig` in place of a Horizons target. Set
`target=None` for a sphere with no Horizons ephemeris, and supply its physical
radius, gravitational parameter, and plotting scale.

```python
from astronomy_types import Distance, GravitationalParameter, Scalar
from afmaths.visualisations.visualisation_types import PlotOriginConfig
from afmaths.visualisations.orbit_system_3d import build_3d_orbit_system_figure

figure = build_3d_orbit_system_figure(
    origin_body=PlotOriginConfig(
        name="Kerbin",
        target=None,
        radius=Distance(Scalar(600_000)),
        gravitational_parameter=GravitationalParameter(Scalar(3.5316e12)),
        radius_scale=1.0,
        distance_scale=100_000.0,
    ),
)
figure.show()
```

A custom sphere can also be used with supplied `satellite_orbits` (orbital
elements), propagated using the custom gravitational parameter. Horizons bodies
require a Horizons-backed origin, and ITRF is currently Earth-only. The launcher
CLI continues to resolve named Horizons targets; custom spheres use the Python API.

## Kerbin orbit (3D)

The launcher includes a Kerbin preset, with a 600,000 m radius and
`mu = 3.5316e12 m³/s²`. This does not query Horizons or Space-Track.
Pass orbital elements in metres/radians (semi-major axis is measured from
Kerbin's centre, **not altitude**):

```bash
python -m afmaths.visualisations.visualisation_launcher kerbin \
  --source elements \
  --inclination 0.900590 \
  --right-ascension-of-ascending-node 0.523599 \
  --argument-of-periapsis 0.785398 \
  --semi-major-axis 700000 \
  --eccentricity 0.001 \
  --true-anomaly 0 \
  --orbits 1
```

An optional `kerbin.jpg` equirectangular texture may be placed beside
`orbit_system_3d.py`. Without it, the visualisation shows an untextured sphere.
Use `python -m` from a project environment where `afmaths` is importable;
physical paths like `lib/afmaths/...` depend on the repository layout.
`--reference-frame ITRF` is Earth-specific and is not valid for Kerbin.

## Kerbin control room

`kerbin` and `kerbin_control_room` open a six-panel dashboard (3D orbit,
Kerbin-fixed ground track, ground-track epoch position, equatorial orbit
projection, position components and velocity components). `kerbin_3d` remains
3D-only.

```bash
python -m afmaths.visualisations.visualisation_launcher kerbin \
  --source elements --inclination 0.900590 \
  --right-ascension-of-ascending-node 0.523599 \
  --argument-of-periapsis 0.785398 --semi-major-axis 700000 \
  --eccentricity 0.001 --true-anomaly 0 \
  --orbits 1 --current-orbits 1
```

The ground track uses stock KSP 1 Kerbin's sidereal rotation period
(21,549.425 s) and µ=3.5316e12 m³/s². The prime meridian is assumed to align
with the inertial +X direction at the supplied epoch. This is a relative
Kerbin-fixed track, not an absolute KSP save-file longitude; synchronising to
a game's longitude requires supplying its UT/initial body orientation. The
red marker identifies the position at the supplied orbital-elements epoch,
not necessarily the wall-clock current spacecraft location.

Satellite 3D sphere radius defaults to 1% of the central body's radius. A
custom `satellite_display_radius` still overrides it in Python.
