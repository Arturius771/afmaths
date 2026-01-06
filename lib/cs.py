import math
from geometry import pythagoras
from operation import add, divide, exponentiate, factorial, multiply, subtract

def file_compression_ratio(uncompressed_size: float) -> float: return lambda compressed_size: divide(compressed_size)(uncompressed_size)

def compressed_file_size(uncompressed_size) -> float: return lambda compression_ratio: divide(compression_ratio)(uncompressed_size) 

def diagonal_pixel_length(length_in_pixels) -> float: return lambda width_in_pixels: math.floor(pythagoras(length_in_pixels, width_in_pixels))

def travelling_salesman_problem_total_routes(number_of_cities) -> float:
  ##(n - 1)!/2
  subtract1 = subtract(1)
  total_routes = divide(2)(factorial(subtract1(number_of_cities)))
  
  return total_routes

def check_drive_clusters(sectors_per_cluster, sector_size_bytes, physical_file_size_bytes) -> float:
  ## TM255    
  if physical_file_size_bytes % (multiply(sectors_per_cluster)(sector_size_bytes)) == 0:
     number_of_clusters = physical_file_size_bytes // multiply(sectors_per_cluster)(sector_size_bytes)
  else:
    number_of_clusters = (physical_file_size_bytes // (sectors_per_cluster * sector_size_bytes)) + 1
    
  multiply_number_of_clusters = multiply(number_of_clusters)
  multiply_number_of_clusters_by_sectors_per_cluster = multiply(multiply_number_of_clusters(sectors_per_cluster))
  slack_space_bytes = subtract(physical_file_size_bytes)(multiply_number_of_clusters_by_sectors_per_cluster(sector_size_bytes))      
  
  return(number_of_clusters, slack_space_bytes)

def ml_f1_score(precision: float, recall: float) -> float:
  """F1 score: related to the harmonic mean of precision and recall. Calculated as F1 = 2/[(1/Precision) + (1/Recall)] = 2/[(TP + FP)/TP + (TP + FN)/TP] = 2/[(2TP + FP + FN)/TP] = 2TP/[2TP + FP + FN] . A high F1 score implies the system has low numbers of false positives and false negatives. - TM358"""
  f1 = divide(add(divide(precision)(1))(divide(recall)(1)))(2)
  
  return f1

def ml_precesion(true_positives) -> float: return lambda false_positives: divide(add(true_positives)(false_positives))(true_positives)

def ml_recall(true_positives): 
  """Fraction of total positives out of both true and false positives - also known as the true positive rate."""
  return lambda false_negatives: divide(add(true_positives)(false_negatives))(true_positives) #TM358

def ml_false_positive_rate(false_positives) -> float: return lambda true_negatives: divide(add(false_positives)(true_negatives))(false_positives)

def ml_weighted_inputs(inputs: list[float], weights: list[float]) -> float:
  "Multiply the inputs by the weights - TM358 Block 1"
  weighted_inputs = []
  loop_count = 0
  if(len(inputs) != len(weights)):
    return None
  for x in inputs:
    weighted_inputs.append(multiply(x)(weights[inputs.index(x, loop_count)]))
    loop_count += 1

  return weighted_inputs

def ml_perceptron(inputs: list, weights: list, bias: float = 0) -> float:
  return ml_activation_function(add(sum(ml_weighted_inputs(inputs, weights)))(bias))

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
  """Takes an 8 bit value and returns its value in decimal form."""
  value = 0
  tracker = len(str(input)) - 1 

  for bit in str(input):
    if(int(bit) != 0):
      exponentiateByTracker = exponentiate(tracker)
      value += exponentiateByTracker(2)   
    tracker -= 1
  return value

def byte_to_hex(input: int) -> str:
  str_input = str(input)
  length = len(str_input)

  if(length == 8):
    return f"{bit_to_hex(str_input[:4])}{bit_to_hex(str_input[4:])}"
  if(length == 7):
    return f"{bit_to_hex(str_input[:3])}{bit_to_hex(str_input[3:])}"
  if(length == 6):
    return f"{bit_to_hex(str_input[:2])}{bit_to_hex(str_input[2:])}"
  if(length == 5):
    return f"{bit_to_hex(str_input[:1])}{bit_to_hex(str_input[1:])}"
  if(length <= 4):
    return f"{bit_to_hex(str_input)}"
  
  return str_input

def bit_to_hex(bit_string: str) -> str: 
  bit_string = bit_string
  if(bit_string == '0'):
      return('0')
  if(bit_string == '1'):
      return('1')
  if(bit_string == '10'):
      return('2')
  if(bit_string == '11'):
      return('3')
  if(bit_string == '100'):
      return('4') 
  if(bit_string == '101'):
      return('5')
  if(bit_string == '110'):
      return('6')
  if(bit_string == '111'):
      return('7')
  if(bit_string == '1000'):
      return('8')
  if(bit_string == '1001'):
      return('9')
  if(bit_string == '1010'):
      return('A')
  if(bit_string == '1011'):
      return('B')
  if(bit_string == '1100'):
      return('C')
  if(bit_string == '1101'):
      return('D')
  if(bit_string == '1110'):
      return('E')
  if(bit_string == '1111'): 
      return('F')  
  
  return bit_string