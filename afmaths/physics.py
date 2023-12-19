import operation

def physics_radiowave_power_distances(distance1, distance2):
  ##TM255 Block 1
  distance_ratio = operation.divide(distance2, distance1) 
  distance1_strength = operation.exponentiate(distance_ratio, 4)
  distance2_strength = operation.divide(1, distance1_strength)
  print("The strength of the signal at distance: {} is {} times greater than distance {}".format(distance1, distance1_strength, distance2))
  print("The strength of the signal at distance: {} is {} times as strong than distance {}".format(distance2, distance2_strength, distance1))
  return distance_ratio, distance1_strength, distance2_strength

def physics_radiowave_recieved_power(watts, distance_metres):
  ##inverse square law
  ##tm255 block 1
  squared_distance = operation.exponentiate(distance_metres, 2)
  pi_times_four = operation.multiply(4, math.pi)
  denominator = operation.multiply(squared_distance, pi_times_four)
  result = operation.divide(watts, denominator)
  print("Received power: {} W/m^2".format(result))
  return result

def physics_speed_of_light_metres_per_second():
  print("Speed of light = 299792458 m/s")
  return 299792458

def physics_planck_constant():
  print ("Planck Constant = 6.62607004 x 10^-34 m^2 kg/s")
  return operation.multiply(6.62607004, operation.exponentiate(10, -34))  

def physics_photon_energy_from_wavelength(wavelength_in_micrometer):
  photon_energy_in_electrovolts = operation.divide(1.2398, wavelength_in_micrometer)
  print("The photon energy is {} eV (electronvolts)".format(photon_energy_in_electrovolts))
  return photon_energy_in_electrovolts

def physics_photon_energy_from_frequency(frequency_in_hertz):
  photon_energy_in_joules = operation.multiply(physics_planck_constant(), frequency_in_hertz)
  print("The energy of a wave with {} Hz = {} J".format(frequency_in_hertz, photon_energy_in_joules))
  return photon_energy_in_joules

def physics_frequency_to_wavelength(frequency_in_hertz):
  wavelength_in_metres = operation.divide(physics_speed_of_light_metres_per_second(), frequency_in_hertz)
  print("Wavelength of a wave with {} Hz = {} m".format(frequency_in_hertz, wavelength_in_metres))
  return wavelength_in_metres
    
def physics_wavelength_to_frequency(wavelength_in_metres):
  frequency_in_hertz = operation.divide(physics_speed_of_light_metres_per_second(), wavelength_in_metres)
  print("Frequency of a wave with {} m wavelength = {} Hz".format(wavelength_in_metres, frequency_in_hertz))
  return frequency_in_hertz