from lib.geometry import calculate_semi_major_axis_ellipse
from lib.operation import add, divide, square_root, subtract

def calculate_orbit_radius(altitude: float, initial_body_radius: int = 6378000) -> float:
    return add(altitude)(initial_body_radius)

def hohmann_transfer(initial_altitude_metres: int, target_altitude_metres: int, initial_body_radius: int = 6378000, gravitational_parameter: float = 3.986005e+14) -> tuple[float, float, float]:
    """Calculates the delta-v required for a Hohmann transfer"""
    # www.braeunig.us/space/problem.htm#4.19

    r_a = calculate_orbit_radius(initial_altitude_metres, initial_body_radius)
    r_b = calculate_orbit_radius(target_altitude_metres, initial_body_radius)

    semi_major_axis_transfer_ellipse = calculate_semi_major_axis_ellipse(r_a, r_b)
    initial_velocity = square_root(divide(r_a)(gravitational_parameter))
    final_velocity = square_root(divide(r_b)(gravitational_parameter))
    velocity_on_orbit_at_initial_orbit = square_root(gravitational_parameter * ((2/r_a) - (1/semi_major_axis_transfer_ellipse)))
    velocity_on_orbit_at_final_orbit = square_root(gravitational_parameter * ((2/r_b) - (1/semi_major_axis_transfer_ellipse)))
    initial_velocity_change = subtract(initial_velocity)(velocity_on_orbit_at_initial_orbit)
    final_velocity_change = subtract(velocity_on_orbit_at_final_orbit)(final_velocity)
    delta_v = add(initial_velocity_change)(final_velocity_change)

    return [delta_v, initial_velocity_change, final_velocity_change]

# TODO: Vis Viva
# TODO: Orbital velocity
# TODO: FST 1 equations
# TODO: Increment of velocity