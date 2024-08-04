import math
import operation

def radiowave_relative_power_distances(distance1, distance2):
  ##TM255 Block 1
  distance_ratio = operation.divide(distance2, distance1) 
  distance1_strength = operation.exponentiate(distance_ratio, 4)
  distance2_strength = operation.divide(1, distance1_strength)
  
  return distance_ratio, distance1_strength, distance2_strength

def radiowave_recieved_power(watts, distance_metres):
  ##inverse square law - should have its own function in formula?
  ##TM255 block 1
  squared_distance = operation.exponentiate(distance_metres, 2)
  pi_times_four = operation.multiply(4, math.pi)
  denominator = operation.multiply(squared_distance, pi_times_four)
  
  return operation.divide(watts, denominator)

def radiowave_received_power_difference_by_distance(power_in_watts_at_distance1, distance1, distance2):
  # https://www.youtube.com/watch?v=BF73QaY1aEg
  cross_multiply = operation.multiply(power_in_watts_at_distance1, operation.exponentiate(distance1, 2))
  
  return operation.divide(cross_multiply, operation.exponentiate(distance2, 2))

def speed_of_light_metres_per_second() -> int:
  
  return 299792458

def planck_constant():
  
  return operation.multiply(6.62607004, operation.exponentiate(10, -34))  

def photon_energy_from_wavelength(wavelength_in_micrometer):
  """Returns photon energy in electrovolts"""
  return operation.divide(1.2398, wavelength_in_micrometer)

def photon_energy_from_frequency(frequency_in_hertz):
  """Returns photon energy in joules"""
  
  return operation.multiply(planck_constant(), frequency_in_hertz)

def frequency_to_wavelength(frequency_in_hertz):
  """Returns wavelength in metres"""
  return operation.divide(speed_of_light_metres_per_second(), frequency_in_hertz)
    
def wavelength_to_frequency(wavelength_in_metres):
  """Returns frequency in hertz"""
  
  return operation.divide(speed_of_light_metres_per_second(), wavelength_in_metres)

def dynamic_pressure(fluid_mass_density, flow_speed):
  return (fluid_mass_density * .5) * flow_speed^2