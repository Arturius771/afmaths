import math
import statistics

from afmaths.afmaths import divide, subtract

def list_sorted(number_list):
  result = sorted(number_list)
  print("Sorted: {}".format(result))
  return result

def list_length(number_list):
  result = len(number_list)
  print("Length{}: {}".format(number_list, result))
  return result

def list_sum(number_list):
  result = sum(number_list)
  print("Sum{}: {}".format(number_list, result))
  return result

def list_minimum(number_list):
  result = min(number_list)
  print("Minimum{}: {}".format(number_list, result))
  return result

def list_maximum(number_list):
  result = max(number_list)
  print("Maximum{}: {}".format(number_list, result))
  return result

def list_range(number_list):
  result = subtract(list_maximum(number_list), list_minimum(number_list))
  print("Range{}: {}".format(number_list, result))
  return result

def list_mean(number_list):
  result = divide(list_sum(number_list),list_length(number_list))
  print("Mean{}: {}".format(number_list, result))
  return result

def list_median(number_list):
  result = statistics.median(number_list)
  print("Median{}: {}".format(number_list, result))
  return result

def list_quartiles(number_list):
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