

import math
from operation import divide, exponentiate, multiply, square


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

def speed_of_light_metres_per_second() -> int:
  
  return 299792458

def planck_constant():
  
  return multiply(6.62607004)(exponentiate(-34)(10))  

def photon_energy_from_wavelength(wavelength_in_micrometer):
  """Returns photon energy in electrovolts"""
  divide_by_wavelength = divide(wavelength_in_micrometer)
  return divide_by_wavelength(1.2398)

def photon_energy_from_frequency(frequency_in_hertz):
  """Returns photon energy in joules"""
  
  return multiply(planck_constant)(frequency_in_hertz)

def frequency_to_wavelength(frequency_in_hertz):
  """Returns wavelength in metres"""
  divide_by_frequency = divide(frequency_in_hertz)
  return divide_by_frequency(speed_of_light_metres_per_second)
    
def wavelength_to_frequency(wavelength_in_metres):
  """Returns frequency in hertz"""

  divide_by_wavelength = divide(wavelength_in_metres)
  
  return divide_by_wavelength(speed_of_light_metres_per_second)

def dynamic_pressure(fluid_mass_density, flow_speed):
  return (fluid_mass_density * .5) * flow_speed^2

def watts_to_decibel_milliwatts(power_in_watts: float) -> float:
  return decibels(power_in_watts, .001)

def decibels(power1: float, power2: float) -> float:
  return math.log(power1/power2, 10)