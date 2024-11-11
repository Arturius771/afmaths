import math
from geometry import pythagoras
from operation import add, divide, exponentiate, factorial, multiply, subtract


def file_compression_ratio(uncompressed_file_size, compressed_file_size):
  result = divide(uncompressed_file_size, compressed_file_size)
  
  return result

def compressed_file_size(uncompressed_file_size, compression_ratio, unit_string):
  result = divide(uncompressed_file_size, compression_ratio)
  
  return result

def diagonal_pixel_length(length_in_pixels, width_in_pixels):
  ##TM255 Block 1 part 5
  result = math.floor(pythagoras(length_in_pixels, width_in_pixels)) ##round down to nearest int according to source material
  
  return result

def travelling_salesman_problem_total_routes(number_of_cities):
  ##(n - 1)!/2
  total_routes = divide(factorial(subtract(number_of_cities, 1)), 2)
  
  return total_routes

def check_drive_clusters(sectors_per_cluster, sector_size_bytes, physical_file_size_bytes):    
  if physical_file_size_bytes % (multiply(sectors_per_cluster, sector_size_bytes)) == 0:
     number_of_clusters = physical_file_size_bytes // multiply(sectors_per_cluster, sector_size_bytes)
  else:
    number_of_clusters = (physical_file_size_bytes // (sectors_per_cluster * sector_size_bytes)) + 1
  slack_space_bytes = subtract(multiply(multiply(number_of_clusters, sectors_per_cluster), sector_size_bytes), physical_file_size_bytes)        
  
  return(number_of_clusters, slack_space_bytes)

def ml_precision(tp, fp):
  """Fraction of positive results that are actually truly positive - TM358"""
  return divide(tp,add(tp, fp))

def ml_recall(tp, fn):
  """Fraction of total positives out of both true and false positives - also known as the true positive rate. TM358"""
  return divide(tp,add(tp, fn))

def ml_false_positive_rate(fp, tn):
  return divide(fp, add(fp, tn))

def ml_f1_score(precision: float, recall: float):
  """F1 score: related to the harmonic mean of precision and recall. Calculated as F1 = 2/[(1/Precision) + (1/Recall)] = 2/[(TP + FP)/TP + (TP + FN)/TP] = 2/[(2TP + FP + FN)/TP] = 2TP/[2TP + FP + FN] . A high F1 score implies the system has low numbers of false positives and false negatives. - TM358"""
  f1 = divide(2, add(divide(1, precision), divide(1, recall)))
  
  return f1

def ml_weighted_inputs(inputs: list[float], weights: list[float]):
  "Multiply the inputs by the weights - TM358 Block 1"
  weighted_inputs = []
  loop_count = 0
  if(len(inputs) != len(weights)):
    return None
  for x in inputs:
    weighted_inputs.append(multiply(x, weights[inputs.index(x, loop_count)]))
    loop_count += 1

  return weighted_inputs

def ml_perceptron(inputs: list, weights: list, bias: float = 0):
  return ml_activation_function(add(sum(ml_weighted_inputs(inputs, weights)), bias))

def ml_activation_function(input: float, threshold: float = 0):
  if input > threshold:
    return 1
  else:
    return 0
  
def byte_to_ascii_text(input: int) -> str:
  # https://www.rapidtables.com/convert/number/binary-to-ascii.html
  value = byte_to_decimal(input)
  
  return chr(value)

def byte_to_decimal(input: int) -> int:
  value = 0
  tracker = len(str(input)) - 1 # Leading 0s are not allowed in Python, so we cannot assume there will be 8 bits in the byte
  
  for bit in str(input):
    if(int(bit) != 0):
      value += exponentiate(2, tracker)    
    tracker -= 1

  return value

def byte_to_hex(input: int):
  length = len(str(input))

  str_input = str(input)

  if(length == 8):
    result = f"{find_hex(str_input[:4])}{find_hex(str_input[4:])}"
    
  if(length == 7):
    result = f"{find_hex(str_input[:3])}{find_hex(str_input[3:])}"
    
  if(length == 6):
    result = f"{find_hex(str_input[:2])}{find_hex(str_input[2:])}"
    
  if(length == 5):
    result = f"{find_hex(str_input[:1])}{find_hex(str_input[1:])}"
    
  if(length <= 4):
    result = f"{find_hex(str_input)}"
    
  return result

def find_hex(input: str): 
  if(int(input) == 0):
      return('0')
  if(int(input) == 1):
      return('1')
  if(int(input) == 10):
      return('2')
  if(int(input) == 11):
      return('3')
  if(int(input) == 100):
      return('4') 
  if(int(input) == 101):
      return('5')
  if(int(input) == 110):
      return('6')
  if(int(input) == 111):
      return('7')
  if(int(input) == 1000):
      return('8')
  if(int(input) == 1001):
      return('9')
  if(int(input) == 1010):
      return('A')
  if(int(input) == 1011):
      return('B')
  if(int(input) == 1100):
      return('C')
  if(int(input) == 1101):
      return('D')
  if(int(input) == 1110):
      return('E')
  if(int(input) == 1111): 
      return('F')  

##def convert_denary_to_base(denary):
    ##todo