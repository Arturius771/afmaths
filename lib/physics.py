import math
from formula import inverse_square_law
from operation import divide, exponentiate, multiply, square

SPEED_OF_LIGHT_METRES_PER_SECONDS = 299792458
PLANCK_CONSTANT = multiply(6.62607004)(exponentiate(-34)(10))  
GRAVITATIONAL_CONSTANT = 6.67430e-11

### PHYSICS FORMULAS
def radiowave_relative_power_distances(distance1: float, distance2: float) -> tuple:
  ##TM255 Block 1
  distance_ratio = divide(distance1)(distance2)
  quartic = exponentiate(4)
  distance1_strength = quartic(distance_ratio)
  divide_by_distance_1_strength = divide(distance1_strength)
  distance2_strength = divide_by_distance_1_strength(1)
  
  return distance_ratio, distance1_strength, distance2_strength

def radiowave_received_power_difference_by_distance(power_in_watts_at_distance1: float, distance1: float, distance2: float) -> float:
  # https://www.youtube.com/watch?v=BF73QaY1aEg
  cross_multiply = multiply(power_in_watts_at_distance1)(square(distance1))
  return divide(square(distance2))(cross_multiply) 

def photon_energy_from_wavelength(wavelength_in_micrometer: float) -> float:
  """Returns photon energy in electrovolts"""
  divide_by_wavelength = divide(wavelength_in_micrometer)
  return divide_by_wavelength(1.2398)

def photon_energy_from_frequency(frequency_in_hertz: float) -> float:
  """Returns photon energy in joules"""
  return multiply(PLANCK_CONSTANT)(frequency_in_hertz: float)

def frequency_to_wavelength(frequency_in_hertz: float) -> float:
  """Returns wavelength in metres"""
  divide_by_frequency = divide(frequency_in_hertz)
  return divide_by_frequency(SPEED_OF_LIGHT_METRES_PER_SECONDS)
    
def wavelength_to_frequency(wavelength_in_metres: float) -> float:
  """Returns frequency in hertz"""
  divide_by_wavelength = divide(wavelength_in_metres)
  return divide_by_wavelength(SPEED_OF_LIGHT_METRES_PER_SECONDS)

def dynamic_pressure(fluid_mass_density: float, flow_speed: float) -> float: 
  return (fluid_mass_density * .5) * flow_speed^2

def watts_to_decibel_milliwatts(power_in_watts: float) -> float: 
  return decibels(power_in_watts)(.001)

def decibels(power1: float) -> function: 
  return lambda power2: math.log(power1/power2, 10)

def flux_density(luminosity: float, distance_metres: float) -> float:
  return inverse_square_law(luminosity, distance_metres)

def univesal_gravitation(mass1: float, mass2: float, distance: float) -> float: 
  return multiply(GRAVITATIONAL_CONSTANT)(multiply(mass1)(mass2) / square(distance))

def angular_diameter_degrees(distance: float, diameter: float) -> float:
  return math.degrees(diameter / distance)

def diameter_of_distant_object(distance: float, angular_diameter_degrees: float) -> float:
  """Returns a diameter of an object if the distance"""
  # Rearranges the equation in angular_diameter_degrees()
  return math.tan(math.radians(angular_diameter_degrees)) * distance


def calculate_gravitional_parameter(mass1: float, mass2: float) -> float:
  # Mu
  return GRAVITATIONAL_CONSTANT(mass1 + mass2)