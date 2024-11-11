

from operation import divide, exponentiate, multiply


def radiowave_relative_power_distances(distance1, distance2):
  ##TM255 Block 1
  distance_ratio = divide(distance2, distance1) 
  distance1_strength = exponentiate(distance_ratio, 4)
  distance2_strength = divide(1, distance1_strength)
  
  return distance_ratio, distance1_strength, distance2_strength

def radiowave_received_power_difference_by_distance(power_in_watts_at_distance1, distance1, distance2):
  # https://www.youtube.com/watch?v=BF73QaY1aEg
  cross_multiply = multiply(power_in_watts_at_distance1, exponentiate(distance1, 2))
  
  return divide(cross_multiply, exponentiate(distance2, 2))

def speed_of_light_metres_per_second() -> int:
  
  return 299792458

def planck_constant():
  
  return multiply(6.62607004, exponentiate(10, -34))  

def photon_energy_from_wavelength(wavelength_in_micrometer):
  """Returns photon energy in electrovolts"""
  return divide(1.2398, wavelength_in_micrometer)

def photon_energy_from_frequency(frequency_in_hertz):
  """Returns photon energy in joules"""
  
  return multiply(planck_constant, frequency_in_hertz)

def frequency_to_wavelength(frequency_in_hertz):
  """Returns wavelength in metres"""
  return divide(speed_of_light_metres_per_second, frequency_in_hertz)
    
def wavelength_to_frequency(wavelength_in_metres):
  """Returns frequency in hertz"""
  
  return divide(speed_of_light_metres_per_second, wavelength_in_metres)

def dynamic_pressure(fluid_mass_density, flow_speed):
  return (fluid_mass_density * .5) * flow_speed^2
