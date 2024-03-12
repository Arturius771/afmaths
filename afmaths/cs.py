import operation
import math
import formula

def cs_file_compression_ratio(uncompressed_file_size, compressed_file_size):
  result = operation.divide(uncompressed_file_size, compressed_file_size)
  print("Compression Ratio: {}/{}={}".format(uncompressed_file_size, compressed_file_size, result))
  return result

def cs_compressed_file_size(uncompressed_file_size, compression_ratio, unit_string):
  result = operation.divide(uncompressed_file_size, compression_ratio)
  print("Compressed File Size: {} / {} = {} {}".format(uncompressed_file_size, compression_ratio, result, unit_string))
  return result

def cs_diagonal_pixel_length(length_in_pixels, width_in_pixels):
  ##TM255 Block 1 part 5
  result = math.floor(formula.pythagoras(length_in_pixels, width_in_pixels)) ##round down to nearest int according to source material
  print("The diagonal length is {} pixels".format(result))
  return result

def cs_travelling_salesman_problem_total_routes(number_of_cities):
  ##(n - 1)!/2
  total_routes = operation.divide(operation.factorial(operation.subtract(number_of_cities, 1)), 2)
  print("The total number of routes: {}".format(total_routes))
  return total_routes

def cs_check_clusters(sectors_per_cluster, sector_size_bytes, physical_file_size_bytes):    
  if physical_file_size_bytes % (operation.multiply(sectors_per_cluster, sector_size_bytes)) == 0:
     clusters = physical_file_size_bytes // operation.multiply(sectors_per_cluster, sector_size_bytes)
  else:
    clusters = (physical_file_size_bytes // (sectors_per_cluster * sector_size_bytes)) + 1
  slack_space_bytes = operation.subtract(operation.multiply(operation.multiply(clusters, sectors_per_cluster), sector_size_bytes), physical_file_size_bytes)        
  print('You will need {} cluster(s) and you will have {} bytes of slack space'.format(clusters, slack_space_bytes))
  return(clusters, slack_space_bytes)

def cs_ml_precision(tp, fp):
  """Fraction of positive results that are actually truly positive - TM358"""
  return operation.divide(tp,operation.add(tp, fp))

def cs_ml_recall(tp, fn):
  """Fraction of total positives out of both true and false positives - also known as the true positive rate. TM358"""
  return operation.divide(tp,operation.add(tp, fn))

def cs_ml_false_positive_rate(fp, tn):
  return operation.divide(fp, operation.add(fp, tn))

def cs_ml_f1_score(precision: float, recall: float):
  """F1 score: related to the harmonic mean of precision and recall. Calculated as F1 = 2/[(1/Precision) + (1/Recall)] = 2/[(TP + FP)/TP + (TP + FN)/TP] = 2/[(2TP + FP + FN)/TP] = 2TP/[2TP +FP + FN] . A high F1 score implies the system has low numbers of false positives and false negatives. - TM358"""
  f1 = operation.divide(2, operation.add(operation.divide(1, precision), operation.divide(1, recall)))
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
    weighted_inputs.append(operation.multiply(x, weights[inputs.index(x, loop_count)]))
    loop_count += 1
  return weighted_inputs

def cs_ml_perceptron(inputs: list, weights: list, bias: float = 0):
  return cs_ml_activation_function(operation.add(operation.list_sum(cs_ml_weighted_inputs(inputs, weights)), bias))

def cs_ml_activation_function(input: float, threshold: float = 0):
  if input > threshold:
    return 1
  else:
    return 0
  
def cs_byte_to_ascii_text(input: int) -> str:
  # https://www.rapidtables.com/convert/number/binary-to-ascii.html
  value = cs_byte_to_decimal(input)
  print (f"{value} as ascii text is {chr(value)}")
  return chr(value)

def cs_byte_to_decimal(input: int) -> int:
  value = 0
  tracker = len(str(input)) - 1 # Leading 0s are not allowed in Python, so we cannot assume there will be 8 bits in the byte
  
  for bit in str(input):
    if(int(bit) != 0):
      value += operation.exponentiate(2, tracker)    
    tracker -= 1

  print(f"{input} in decimal is: {value}")
  return value

def cs_byte_to_hex(input: int):
  length = len(str(input))

  str_input = str(input)

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
    
  if(length == 8):
    result = f"{find_hex(str_input[:4])}{find_hex(str_input[4:])}"
    print(result)
    return result
  if(length == 7):
    result = f"{find_hex(str_input[:3])}{find_hex(str_input[3:])}"
    print(result)
    return result
  if(length == 6):
    result = f"{find_hex(str_input[:2])}{find_hex(str_input[2:])}"
    print(result)
    return result
  if(length == 5):
    result = f"{find_hex(str_input[:1])}{find_hex(str_input[1:])}"
    print(result)
    return result
  if(length <= 4):
    result = f"{find_hex(str_input)}"
    print(result)
    return result

    


##def cs_convert_denary_to_base(denary):
    ##todo