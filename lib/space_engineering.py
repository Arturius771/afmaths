from lib.geometry import calculate_semi_major_axis_ellipse
from lib.operation import add, divide, half, multiply, square_root, subtract

def calculate_orbit_radius(altitude: float, initial_body_radius: int = 6378000) -> float:
    return add(altitude)(initial_body_radius)

def vis_viva(gravitational_parameter: float, orbit_radius: float, semi_major_axis: float) -> float:
    """Calculates the velocity of an object in an elliptical orbit using the vis-viva equation."""
    return square_root(multiply(gravitational_parameter)(subtract(divide(semi_major_axis)(1))(divide(orbit_radius)(2))))

def calculate_velocity_for_altitude(orbit_radius: float, gravitational_parameter: float = 3.986005e+14) -> float:
    return square_root(divide(orbit_radius)(gravitational_parameter))

def velocity_difference(initial_velocity: float, final_velocity: float) -> float:
    return subtract(initial_velocity)(final_velocity)

def hohmann_transfer(initial_altitude_metres: int, target_altitude_metres: int, initial_body_radius: int = 6378000, gravitational_parameter: float = 3.986005e+14, result_in_km: bool = True) -> tuple[float, float, float]:
    """Calculates the delta-v required for a Hohmann transfer"""
    # www.braeunig.us/space/problem.htm#4.19

    r_a = calculate_orbit_radius(initial_altitude_metres, initial_body_radius)
    r_b = calculate_orbit_radius(target_altitude_metres, initial_body_radius)

    semi_major_axis_transfer_ellipse = calculate_semi_major_axis_ellipse(r_a, r_b)
    initial_velocity = calculate_velocity_for_altitude(r_a, gravitational_parameter)
    final_velocity = calculate_velocity_for_altitude(r_b, gravitational_parameter)
    velocity_on_orbit_at_initial_orbit = vis_viva(gravitational_parameter, r_a, semi_major_axis_transfer_ellipse)
    velocity_on_orbit_at_final_orbit = vis_viva(gravitational_parameter, r_b, semi_major_axis_transfer_ellipse)
    initial_velocity_change = velocity_difference(initial_velocity, velocity_on_orbit_at_initial_orbit)
    final_velocity_change = velocity_difference(velocity_on_orbit_at_final_orbit, final_velocity)
    delta_v = add(initial_velocity_change)(final_velocity_change)

    if(result_in_km):
        delta_v = divide(1000)(delta_v)
        initial_velocity_change = divide(1000)(initial_velocity_change)
        final_velocity_change = divide(1000)(final_velocity_change)
    return (delta_v, initial_velocity_change, final_velocity_change)

# TODO: FST 1 equations
# TODO: Increment of velocity

if __name__ == '__main__':
    print(hohmann_transfer(300000, 1000000)) # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)