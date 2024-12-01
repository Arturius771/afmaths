

import math
from formula import inverse_square_law
from operation import divide, exponentiate, multiply, square, square_root

SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(-34)(10))  
GRAVITATIONAL_CONSTANT = 6.67430e-11


def radiowave_relative_power_distances(distance1, distance2):
  ##TM255 Block 1
  distance_ratio = divide(distance1)(distance2)
  quartic = exponentiate(4)
  distance1_strength = quartic(distance_ratio)
  divide_by_distance_1_strength = divide(distance1_strength)
  distance2_strength = divide_by_distance_1_strength(1)
  
  return distance_ratio, distance1_strength, distance2_strength

def radiowave_received_power_difference_by_distance(power_in_watts_at_distance1, distance1, distance2):
  # https://www.youtube.com/watch?v=BF73QaY1aEg
  cross_multiply = multiply(power_in_watts_at_distance1)(square(distance1))
  return divide(square(distance2))(cross_multiply) 

def photon_energy_from_wavelength(wavelength_in_micrometer):
  """Returns photon energy in electrovolts"""
  divide_by_wavelength = divide(wavelength_in_micrometer)
  return divide_by_wavelength(1.2398)

def photon_energy_from_frequency(frequency_in_hertz):
  """Returns photon energy in joules"""
  return multiply(PLANCK_CONSTANT)(frequency_in_hertz)

def frequency_to_wavelength(frequency_in_hertz):
  """Returns wavelength in metres"""
  divide_by_frequency = divide(frequency_in_hertz)
  return divide_by_frequency(SPEED_OF_LIGHT_METRES_PER_SECONDS)
    
def wavelength_to_frequency(wavelength_in_metres):
  """Returns frequency in hertz"""
  divide_by_wavelength = divide(wavelength_in_metres)
  return divide_by_wavelength(SPEED_OF_LIGHT_METRES_PER_SECONDS)

def dynamic_pressure(fluid_mass_density, flow_speed): return (fluid_mass_density * .5) * flow_speed^2

def watts_to_decibel_milliwatts(power_in_watts: float) -> float: return decibels(power_in_watts)(.001)

def decibels(power1: float): return lambda power2: math.log(power1/power2, 10)

def hohmann_transfer(initial_altitude_metres: int, target_altitude_metres: int, initial_body_radius: int = 6378000):
    # www.braeunig.us/space/problem.htm#4.19

    r_a = initial_altitude_metres + initial_body_radius
    r_b = target_altitude_metres
    G_M = 3.986005e+14

    semi_major_axis_transfer_ellipse = (r_a + r_b) / 2
    initial_velocity = square_root(G_M / r_a)
    final_velocity = square_root(G_M / r_b)
    velocity_on_orbit_at_initial_orbit = square_root(G_M * ((2/r_a) - (1/semi_major_axis_transfer_ellipse)))
    velocity_on_orbit_at_final_orbit = square_root(G_M * ((2/r_b) - (1/semi_major_axis_transfer_ellipse)))
    initial_velocity_change = velocity_on_orbit_at_initial_orbit - initial_velocity
    final_velocity_change = final_velocity - velocity_on_orbit_at_final_orbit
    total_velocity_change = initial_velocity_change + final_velocity_change

    return total_velocity_change

def flux_density(luminosity, distance_metres):
  return inverse_square_law(luminosity, distance_metres)

def univesal_gravitation(mass1, mass2, distance): return multiply(GRAVITATIONAL_CONSTANT)(multiply(mass1)(mass2) / square(distance))

def angular_diameter_degrees(distance: float, diameter: float):
  return math.degrees(diameter / distance)

def diameter_of_distant_object(distance, angular_diameter_degrees) -> float:
  """Returns a diameter of an object if the distance"""
  # Rearranges the equation in angular_diameter_degrees()
  return math.tan(math.radians(angular_diameter_degrees)) * distance