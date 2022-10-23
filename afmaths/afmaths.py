import math
import statistics


def test(num1, num2):
  """
  Tests the basic operations

  Other functions called:
  :add (num1 + num2)
  :subtract (num1 - num2)
  :multiply( num1 * num2)
  :divide( num1 / num2)
  :exponentiate( num1 ^ num2)
  """
  add(num1, num2)
  subtract(num1, num2)    
  multiply(num1, num2)
  divide(num1, num2)
  exponentiate(num1, num2)

def dataplotter(number_list):
  ##MU123
  list_sorted(number_list)
  list_length(number_list)
  list_sum(number_list)    
  list_minimum(number_list)
  list_maximum(number_list)
  list_range((number_list))
  list_mean(number_list)
  list_median(number_list)
  list_quartiles(number_list)

def add(num1: float, num2: float):
  result = num1 + num2
  print("Add: {} + {} = {}".format(num1, num2, result))
  return result

def subtract(num1: float, num2: float):
  result = num1 - num2
  print("Subtract: {} - {} = {}".format(num1, num2, result))
  return result

def multiply(num1: float, num2: float):
  result = num1 * num2
  print("Multiply: {} * {} = {}".format(num1, num2, result))
  return result

def divide(num1: float, num2: float):
  if num2 != 0:
    result = num1 / num2
    print("Divide: {} / {} = {}".format(num1, num2, result))
    return result
  else:
    print("Divide: You tried to divide by 0")

def exponentiate(number: float, exponent: float):
  result = number ** exponent
  print("Exponent: {} to the power of {} = {}".format(number, exponent, result))
  return result

def square_root(number: float):
  result = math.sqrt(number)
  print("Square root: {} is {}".format(number, result))
  return result

def factorial(number: int):
  working_string = ""
  result = 1

  for loop in range(number, 0, -1):
    result = multiply(result, loop)
    working_string = "{} {} x".format(working_string, loop)

  working_string = working_string[:-1]
  working_string = "{}! ={} = {}".format(number, working_string, result)

  print(working_string)
  return result

def euclid(m: int, n: int):
    """Given two positive integers, m and n, find their greatest common divisor which is the largest positive integer that divides both evenly."""

    remainder = m % n
    if remainder == 0:
      print("Greatest common divisor for {} and {} = {}".format(m, n, n))
      return n
    else:
      m = n
      n = remainder
      print("m {} n {}".format(m, n))
      euclid(m,n)

def pythagoras(a,b):
  result = square_root(add(exponentiate(a, 2), exponentiate(b, 2)))
  print("Pythagoras = {}".format(result))
  return result

def sigmoid(input, bias:float = 0):
  "TM358 Section Block 1 section 5"
  return (divide(1,add(1,exponentiate(math.e, add(-input, bias)))))

def cs_file_compression_ratio(uncompressed_file_size, compressed_file_size):
  result = divide(uncompressed_file_size, compressed_file_size)
  print("Compression Ratio: {}/{}={}".format(uncompressed_file_size, compressed_file_size, result))
  return result

def cs_compressed_file_size(uncompressed_file_size, compression_ratio, unit_string):
  result = divide(uncompressed_file_size, compression_ratio)
  print("Compressed File Size: {} / {} = {} {}".format(uncompressed_file_size, compression_ratio, result, unit_string))
  return result

def cs_diagonal_pixel_length(length_in_pixels, width_in_pixels):
  ##TM255 Block 1 part 5
  result = math.floor(pythagoras(length_in_pixels, width_in_pixels)) ##round down to nearest int according to source material
  print("The diagonal length is {} pixels".format(result))
  return result

def cs_travelling_salesman_problem_total_routes(number_of_cities):
  ##(n - 1)!/2
  total_routes = divide(factorial(subtract(number_of_cities, 1)), 2)
  print("The total number of routes: {}".format(total_routes))
  return total_routes

def cs_check_clusters(sectors_per_cluster, sector_size_bytes, physical_file_size_bytes):    
  if physical_file_size_bytes % (multiply(sectors_per_cluster, sector_size_bytes)) == 0:
     clusters = physical_file_size_bytes // multiply(sectors_per_cluster, sector_size_bytes)
  else:
    clusters = (physical_file_size_bytes // (sectors_per_cluster * sector_size_bytes)) + 1
  slack_space_bytes = subtract(multiply(multiply(clusters, sectors_per_cluster), sector_size_bytes), physical_file_size_bytes)        
  print('You will need {} cluster(s) and you will have {} bytes of slack space'.format(clusters, slack_space_bytes))
  return(clusters, slack_space_bytes)

def cs_ml_precision(tp, fp):
  """Fraction of positive results that are actually truly positive - TM358"""
  return divide(tp,add(tp, fp))

def cs_ml_recall(tp, fn):
  """Fraction of total positives out of both true and false positives - also known as the true positive rate. TM358"""
  return divide(tp,add(tp, fn))

def cs_ml_false_positive_rate(fp, tn):
  return divide(fp, add(fp, tn))

def cs_ml_f1_score(precision: float, recall: float):
  """F1 score: related to the harmonic mean of precision and recall. Calculated as F1 = 2/[(1/Precision) + (1/Recall)] = 2/[(TP + FP)/TP + (TP + FN)/TP] = 2/[(2TP + FP + FN)/TP] = 2TP/[2TP +FP + FN] . A high F1 score implies the system has low numbers of false positives and false negatives. - TM358"""
  f1 = divide(2, add(divide(1, precision), divide(1, recall)))
  print('Your F1 score = {}'.format(f1))
  return f1

def cs_ml_weighted_inputs(inputs: list[float], weights: list[float]):
  "Multiply the inputs by the weights - TM358 Block 1"
  weighted_inputs = []
  loop_count = 0
  if(len(inputs) != len(weights)):
    print('The inputs list must be the same length as the weights list')
    return None
  for x in inputs:
    weighted_inputs.append(multiply(x, weights[inputs.index(x, loop_count)]))
    loop_count += 1
  return weighted_inputs

def cs_ml_perceptron(inputs: list, weights: list, bias: float = 0):
  return cs_ml_activation_function(add(list_sum(cs_ml_weighted_inputs(inputs, weights)), bias))

def cs_ml_activation_function(input: float, threshold: float = 0):
  if input > threshold:
    return 1
  else:
    return 0

##def cs_convert_denary_to_base(denary):
    ##todo

def graph_gradient(x1, y1, x2, y2):
  ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
  try:
    result = divide(subtract(y2, y1), subtract(x2, x1))
    print("The gradient of line with coordinates ({}, {}) and ({}, {}) is: {}".format(x1, y1, x2, y2, result))
    return result
  except TypeError:
    print("Gradient: You probably have a vertical line")    

def graph_equation_of_line(x1, y1, x2, y2):
  ##y = mx + b
  ##m = gradient
  ##b = y intercept when x = 0
  try:
    m = graph_gradient(x1, y1, x2, y2)
    rhs = multiply(m, x1)
    b = subtract(y1, rhs)
    if b < 0:
      print("Equation of line: y = {}x {}".format(m, b))
    else:
      print("Equation of line: y = {}x + {}".format(m, b))
    return b
  except TypeError:
    print("Equation of Line: You probably have a vertical line")

def list_sorted(number_list: list):
  result = sorted(number_list)
  print("Sorted: {}".format(result))
  return result

def list_length(number_list: list):
  result = len(number_list)
  print("Length{}: {}".format(number_list, result))
  return result

def list_sum(number_list: list):
  result = sum(number_list)
  print("Sum{}: {}".format(number_list, result))
  return result

def list_minimum(number_list: list):
  result = min(number_list)
  print("Minimum{}: {}".format(number_list, result))
  return result

def list_maximum(number_list: list):
  result = max(number_list)
  print("Maximum{}: {}".format(number_list, result))
  return result

def list_range(number_list: list):
  result = subtract(list_maximum(number_list), list_minimum(number_list))
  print("Range{}: {}".format(number_list, result))
  return result

def list_mean(number_list: list):
  result = divide(list_sum(number_list),list_length(number_list))
  print("Mean{}: {}".format(number_list, result))
  return result

def list_median(number_list: list):
  result = statistics.median(number_list)
  print("Median{}: {}".format(number_list, result))
  return result

def list_quartiles(number_list: list):
  number_list = list_sorted(number_list)
  q1_index = int(math.ceil(list_length(number_list) * 0.25))
  q1_result = number_list[q1_index - 1]
  number_list[0:list_length(number_list)//2]
  q3_result = statistics.median(number_list)    
  iqr_result = subtract(q3_result, q1_result)
  print("Q1: {}".format(q1_result))
  print("Q3: {}".format(q3_result))
  print("IQR: {}".format(iqr_result))
  return q1_result, q3_result, iqr_result

def physics_radiowave_power_distances(distance1, distance2):
  ##TM255 Block 1
  distance_ratio = divide(distance2, distance1) 
  distance1_strength = exponentiate(distance_ratio, 4)
  distance2_strength = divide(1, distance1_strength)
  print("The strength of the signal at distance: {} is {} times greater than distance {}".format(distance1, distance1_strength, distance2))
  print("The strength of the signal at distance: {} is {} times as strong than distance {}".format(distance2, distance2_strength, distance1))
  return distance_ratio, distance1_strength, distance2_strength

def physics_radiowave_recieved_power(watts, distance_metres):
  ##inverse square law
  ##tm255 block 1
  squared_distance = exponentiate(distance_metres, 2)
  pi_times_four = multiply(4, math.pi)
  denominator = multiply(squared_distance, pi_times_four)
  result = divide(watts, denominator)
  print("Received power: {} W/m^2".format(result))
  return result

def physics_speed_of_light_metres_per_second():
  print("Speed of light = 299792458 m/s")
  return 299792458

def physics_planck_constant():
  print ("Planck Constant = 6.62607004 x 10^-34 m^2 kg/s")
  return multiply(6.62607004, exponentiate(10, -34))  

def physics_photon_energy_from_wavelength(wavelength_in_micrometer):
  photon_energy_in_electrovolts = divide(1.2398, wavelength_in_micrometer)
  print("The photon energy is {} eV (electronvolts)".format(photon_energy_in_electrovolts))
  return photon_energy_in_electrovolts

def physics_photon_energy_from_frequency(frequency_in_hertz):
  photon_energy_in_joules = multiply(physics_planck_constant(), frequency_in_hertz)
  print("The energy of a wave with {} Hz = {} J".format(frequency_in_hertz, photon_energy_in_joules))
  return photon_energy_in_joules

def physics_frequency_to_wavelength(frequency_in_hertz):
  wavelength_in_metres = divide(physics_speed_of_light_metres_per_second(), frequency_in_hertz)
  print("Wavelength of a wave with {} Hz = {} m".format(frequency_in_hertz, wavelength_in_metres))
  return wavelength_in_metres
    
def physics_wavelength_to_frequency(wavelength_in_metres):
  frequency_in_hertz = divide(physics_speed_of_light_metres_per_second(), wavelength_in_metres)
  print("Frequency of a wave with {} m wavelength = {} Hz".format(wavelength_in_metres, frequency_in_hertz))
  return frequency_in_hertz