from lib.operation import square_root


def hohmann_transfer(initial_altitude_metres: int, target_altitude_metres: int, initial_body_radius: int = 6378000):
    # www.braeunig.us/space/problem.htm#4.19

    r_a = initial_altitude_metres + initial_body_radius
    r_b = target_altitude_metres + initial_body_radius
    G_M = 3.986005e+14 # for Earth

    semi_major_axis_transfer_ellipse = (r_a + r_b) / 2
    initial_velocity = square_root(G_M / r_a)
    final_velocity = square_root(G_M / r_b)
    velocity_on_orbit_at_initial_orbit = square_root(G_M * ((2/r_a) - (1/semi_major_axis_transfer_ellipse)))
    velocity_on_orbit_at_final_orbit = square_root(G_M * ((2/r_b) - (1/semi_major_axis_transfer_ellipse)))
    initial_velocity_change = velocity_on_orbit_at_initial_orbit - initial_velocity
    final_velocity_change = final_velocity - velocity_on_orbit_at_final_orbit
    total_velocity_change = initial_velocity_change + final_velocity_change

    return total_velocity_change

# TODO: Vis Viva
# TODO: Orbital velocity
# TODO: FST 1 equations
# TODO: Increment of velocity