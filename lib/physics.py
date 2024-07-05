import math
import operation

def physics_radiowave_relative_power_distances(distance1, distance2):
  ##TM255 Block 1
  distance_ratio = operation.divide(distance2, distance1) 
  distance1_strength = operation.exponentiate(distance_ratio, 4)
  distance2_strength = operation.divide(1, distance1_strength)
  print(f"The strength of the signal at distance: {distance1} is {distance1_strength} times greater than distance {distance2}")
  print(f"The strength of the signal at distance: {distance2} is {distance2_strength} times as strong as distance {distance1}")
  return distance_ratio, distance1_strength, distance2_strength

def physics_radiowave_recieved_power(watts, distance_metres):
  ##inverse square law
  ##TM255 block 1
  squared_distance = operation.exponentiate(distance_metres, 2)
  pi_times_four = operation.multiply(4, math.pi)
  denominator = operation.multiply(squared_distance, pi_times_four)
  result = operation.divide(watts, denominator)
  print(f"Received power: {result} W/m^2")
  return result

def physics_radiowave_received_power_difference_by_distance(power_in_watts_at_distance1, distance1, distance2):
  # https://www.youtube.com/watch?v=BF73QaY1aEg
  cross_multiply = operation.multiply(power_in_watts_at_distance1, operation.exponentiate(distance1, 2))
  i2 = operation.divide(cross_multiply, operation.exponentiate(distance2, 2))
  print(f"Received power at distance 2: {i2} W/m^2")
  return i2

def physics_speed_of_light_metres_per_second() -> int:
  print("Speed of light = 299792458 m/s")
  return 299792458

def physics_planck_constant():
  print ("Planck Constant = 6.62607004 x 10^-34 m^2 kg/s")
  return operation.multiply(6.62607004, operation.exponentiate(10, -34))  

def physics_photon_energy_from_wavelength(wavelength_in_micrometer):
  photon_energy_in_electrovolts = operation.divide(1.2398, wavelength_in_micrometer)
  print(f"The photon energy is {photon_energy_in_electrovolts} eV (electronvolts)")
  return photon_energy_in_electrovolts

def physics_photon_energy_from_frequency(frequency_in_hertz):
  photon_energy_in_joules = operation.multiply(physics_planck_constant(), frequency_in_hertz)
  print(f"The energy of a wave with {frequency_in_hertz} Hz = {photon_energy_in_joules} J")
  return photon_energy_in_joules

def physics_frequency_to_wavelength(frequency_in_hertz):
  wavelength_in_metres = operation.divide(physics_speed_of_light_metres_per_second(), frequency_in_hertz)
  print(f"Wavelength of a frequency with {frequency_in_hertz} Hz = {wavelength_in_metres} m")
  return wavelength_in_metres
    
def physics_wavelength_to_frequency(wavelength_in_metres):
  frequency_in_hertz = operation.divide(physics_speed_of_light_metres_per_second(), wavelength_in_metres)
  print(f"Frequency of a wave with {wavelength_in_metres} m wavelength = {frequency_in_hertz} Hz")
  return frequency_in_hertz