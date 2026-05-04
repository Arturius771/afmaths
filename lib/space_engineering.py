from math import atan
import math

from geometry import calculate_semi_major_axis_ellipse
from operation import CUBE, SQUARE, add, divide, dot_product_3d, exponentiate, multiply, square, square_root, subtract, vector_cross_multiplication_3d, vector_magnitude_3d

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

def inclination_from_angular_momentum_vector(angular_momentum_vector: list[float]) -> float:
    """Calculates the inclination of an orbit from the angular momentum vector"""
    x = SQUARE(angular_momentum_vector[0])
    y = SQUARE(angular_momentum_vector[1])
    numerator = square_root(add(x)(y))
    denominator = angular_momentum_vector[2]
    return atan(divide(denominator)(numerator))

def right_ascension_from_angular_momentum_vector(angular_momentum_vector: list[float]) -> float:
    """Calculates the right ascension of an orbit from the angular momentum vector"""
    return add(atan(divide(-angular_momentum_vector[1])(angular_momentum_vector[0])))(math.pi)

def semi_major_axis_from_position_and_velocity(position_vector: list[float], velocity_vector: list[float], gravitational_parameter: float = 3.986005e+14) -> float:
    """Calculates the semi major axis of an orbit from the position and velocity vectors"""
    r = vector_magnitude_3d(position_vector)
    v = vector_magnitude_3d(velocity_vector)
    # This is a rearranged vis-viva equation
    a = subtract(divide(gravitational_parameter)(SQUARE(v)))(divide(r)(2))
    return exponentiate(-1)(a)

def calculate_eccentricity_from_angular_momentum_vector(angular_momentum_vector: list[float], semi_major_axis: float, gravitational_parameter: float = 398600) -> float:
    """Calculates the eccentricity of an orbit from the angular momentum vector"""
    h = vector_magnitude_3d(angular_momentum_vector)
    denominator = multiply(gravitational_parameter)(semi_major_axis)
    division = divide(denominator)(SQUARE(h))
    return square_root(subtract(division)(1))

def mean_motion_from_semi_major_axis(semi_major_axis: float, gravitational_parameter: float = 398600) -> float:
    """Calculates the mean motion of an orbit from the semi major axis"""
    return square_root(divide(CUBE(semi_major_axis))(gravitational_parameter))

def eccentric_anomaly(position_vector: list[float], velocity_vector: list[float], semi_major_axis: float, mean_motion: float) -> float:
    first_term = dot_product_3d(position_vector, velocity_vector)
    second_term = multiply(SQUARE(semi_major_axis))(mean_motion)
    third_term = subtract(divide(semi_major_axis)(vector_magnitude_3d(position_vector)))(1)

    numerator = divide(second_term)(first_term)
    brackets = divide(third_term)(numerator)
    
    return add(atan(brackets))(math.pi)

def true_anomaly_from_eccentric_anomaly(E: float, e: float) -> float:
    sin_E = math.sin(E)
    cos_E = math.cos(E)

    sqrt_term = square_root(subtract(SQUARE(e))(1)) 

    y = multiply(sqrt_term)(sin_E)        # √(1 - e²) * sin(E)
    x = subtract(e)(cos_E)        
    
    theta = math.atan(y / x)

    if x > 0:
        if y < 0:
            theta += 2 * math.pi
    elif x < 0:
        theta += math.pi
    else:  # x == 0
        if y > 0:
            theta = math.pi / 2
        elif y < 0:
            theta = 3 * math.pi / 2
        else:
            theta = 0  

    return theta

def argument_of_latitude(right_ascension_of_ascending_node: float, inclination: float, position_vector: list[float]) -> float:
    numerator = divide(math.sin(inclination))(position_vector[2])
    second_term = add(multiply(position_vector[0])(math.cos(right_ascension_of_ascending_node)))(multiply(position_vector[1])(math.sin(right_ascension_of_ascending_node)))

    x = numerator
    y = second_term
    u = atan(divide(second_term)(numerator))

    # Account for the correct quadrant of the latitude
    if x > 0:
        if y < 0:
            u += 2 * math.pi
    elif x < 0:
        u += math.pi
    else:  # x == 0
        if y > 0:
            u = math.pi / 2
        elif y < 0:
            u = 3 * math.pi / 2
        else:
            u = 0  

    return u

def orbital_elements_from_state_vectors(position_vector: list[float], velocity_vector: list[float], gravitational_parameter: float = 398600) -> dict:
    """Calculates the orbital elements of an orbit from the state vectors (position and velocity)"""
    # From TUB MSE SFM Exercise 2 solution
    angular_momentum_vector = vector_cross_multiplication_3d(position_vector, velocity_vector)
    inclination = inclination_from_angular_momentum_vector(angular_momentum_vector)
    right_ascension = right_ascension_from_angular_momentum_vector(angular_momentum_vector)
    semi_major_axis = semi_major_axis_from_position_and_velocity(position_vector, velocity_vector, gravitational_parameter)
    eccentricity = calculate_eccentricity_from_angular_momentum_vector(angular_momentum_vector, semi_major_axis, gravitational_parameter)
    mean_motion = mean_motion_from_semi_major_axis(semi_major_axis, gravitational_parameter)
    eccentric_an = eccentric_anomaly(position_vector, velocity_vector, semi_major_axis, mean_motion)
    true_anomaly = true_anomaly_from_eccentric_anomaly(eccentric_an, eccentricity)
    latitude = argument_of_latitude(right_ascension, inclination, position_vector)
    argument_of_perigee = subtract(true_anomaly)(latitude)
    

    return {"inclination": inclination, "right_ascension": right_ascension, "argument_of_perigee": argument_of_perigee, "semi_major_axis": semi_major_axis, "eccentricity": eccentricity, "true_anomaly": true_anomaly}


# TODO: FST 1 equations
# TODO: Increment of velocity

if __name__ == '__main__':
    # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)
    print(hohmann_transfer(300000, 1000000)) 
    # {'inclination': 0.12166217595729033, 'right_ascension': 3.024483909022929, 'argument_of_perigee': 1.5978995641224425, 'semi_major_axis': 25015.186690979368, 'eccentricity': 0.7079768603248032, 'true_anomaly': 2.987554518980773}
    print(orbital_elements_from_state_vectors([10000,40000,-5000], [-1.5, 1, -0.1]))