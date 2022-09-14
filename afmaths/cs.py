import math
from afmaths.afmaths import add, divide, exponentiate, factorial, multiply, square_root, subtract

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
  length_squared = exponentiate(length_in_pixels, 2)
  width_squared = exponentiate(width_in_pixels, 2)
  pythagoras = add(length_squared, width_squared)
  result = math.floor(square_root(pythagoras)) ##round down to nearest int according to source material
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
  "Fraction of positive results that are actually truly positive - TM358"
  return divide(tp,add(tp, fp))

def cs_ml_recall(tp, fn):
  "Fraction of total positives out of both true and false positives - TM358"
  return divide(tp,add(tp, fn))

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

##def cs_convert_denary_to_base(denary):
    ##todo