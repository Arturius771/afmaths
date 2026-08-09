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
python lib/afmaths/visualisations/visualisation_launcher.py solar_system_3d
```

---

## Orbit data sources

Orbit-based visualisations use a common orbit model and can be populated from one of three sources:

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
  --inclination 51.6 \
  --semi-major-axis 6778000 \
  --eccentricity 0.001
```

`tle` is the default source. If an orbit-based visualisation is launched without `--source` or `--norad-id`, the ISS is used by default.

The source abstraction is used by:

- `control_room`
- `ground_track`
- `current_ground_track`
- `itrf_orbit_3d`
- `satellite_earth_3d`

The remaining visualisations use their own fixed or specialised inputs.

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
  --inclination 51.6 \
  --right-ascension-of-ascending-node 30 \
  --argument-of-periapsis 45 \
  --semi-major-axis 6778000 \
  --eccentricity 0.001 \
  --true-anomaly 0 \
  --orbits 1 \
  --current-orbits 1
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
  --inclination 51.6 \
  --right-ascension-of-ascending-node 30 \
  --argument-of-periapsis 45 \
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

Displays the propagated ground track starting from the orbit's current position. The current implementation also displays the configured Dublin ground station, apogee, perigee, and current position.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py current_ground_track \
  --source tle \
  --norad-id 25544
```

It can use the same alternative sources:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py current_ground_track \
  --source elements \
  --inclination 51.6 \
  --semi-major-axis 6778000
```

Legacy alias:

```text
ground_track_current
```

---

### `itrf_orbit_3d`

Displays one or more propagated orbits in the International Terrestrial Reference Frame (ITRF).

Alias: `itrf`

TLE:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py itrf \
  --source tle \
  --norad-id 25544
```

Multiple satellites can be displayed:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py itrf \
  --norad-id 25544 20580
```

Horizons:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py itrf \
  --source horizon \
  --target MOON
```

Custom orbital elements:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py itrf \
  --source elements \
  --inclination 51.6 \
  --semi-major-axis 6778000
```

Control the propagation duration with:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py itrf \
  --norad-id 25544 \
  --orbits 5
```

The legacy name `itrf_custom` is retained as an alias for `itrf_orbit_3d`.

---

### `satellite_earth_3d`

Displays one or more orbits around a 3D Earth.

Alias: `satellite_earth`

TLE:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py satellite_earth \
  --source tle \
  --norad-id 25544
```

Multiple satellites can be supplied:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py satellite_earth \
  --norad-id 25544 20580
```

Horizons:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py satellite_earth \
  --source horizon \
  --target MOON
```

Custom orbital elements are also supported through `--source elements`.

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

## Celestial visualisations

### `solar_system_3d`

Displays the 3D Solar System visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py solar_system_3d
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py solar_system
```

---

### `moon_earth_3d`

Displays the 3D Earth–Moon visualisation.

```bash
python lib/afmaths/visualisations/visualisation_launcher.py moon_earth_3d
```

Alias:

```bash
python lib/afmaths/visualisations/visualisation_launcher.py moon_earth
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
| `--inclination DEG`                       | Orbital inclination in degrees                                 |
| `--right-ascension-of-ascending-node DEG` | RAAN in degrees                                                |
| `--argument-of-periapsis DEG`             | Argument of periapsis in degrees                               |
| `--semi-major-axis VALUE`                 | Semi-major axis, using the units expected by `OrbitalElements` |
| `--eccentricity E`                        | Orbital eccentricity                                           |
| `--true-anomaly DEG`                      | True anomaly in degrees                                        |

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
  --inclination 70 \
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
python lib/afmaths/visualisations/visualisation_launcher.py itrf \
  --norad-id 25544 20580
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
  --inclination 45 \
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
  --inclination 89 \
  --right-ascension-of-ascending-node 0 \
  --argument-of-periapsis 110 \
  --semi-major-axis 42000000 \
  --eccentricity 0.001 \
  --true-anomaly 3.14 \
  --orbits 1 \
  --current-orbits 1
```

---

## Visualisation name reference

| Visualisation          | Alias                                     |
| ---------------------- | ----------------------------------------- |
| `control_room`         | `controlroom`                             |
| `itrf_orbit_3d`        | `itrf`, `itrf_custom`                     |
| `satellite_earth_3d`   | `satellite_earth`                         |
| `ground_track`         | `ground_track_tle`, `ground_track_custom` |
| `current_ground_track` | `ground_track_current`                    |
| `collision_detection`  | —                                         |
| `hohmann_tradeoff`     | —                                         |
| `hohmann_transfer_2d`  | `hohmann_transfer`                        |
| `keplers_ellipse_2d`   | `kepler`                                  |
| `moon_earth_3d`        | `moon_earth`                              |
| `newton_iteration`     | —                                         |
| `phase_orbit_2d`       | `phase_orbit`                             |
| `solar_system_3d`      | `solar_system`                            |
| `two_body_2d`          | `two_body`                                |
| `velocity_time`        | —                                         |

```

```
