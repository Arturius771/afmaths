import operation
import math
import statistics

def sorted(number_list: list):
  result = sorted(number_list)
  print(f"Sorted: {result}")
  return result

def length(number_list: list):
  result = len(number_list)
  print(f"Length{number_list}: {result}")
  return result

def sum(number_list: list):
  result = sum(number_list)
  print(f"Sum{number_list}: {result}")
  return result

def minimum(number_list: list):
  result = min(number_list)
  print(f"Minimum{number_list}: {result}")
  return result

def maximum(number_list: list):
  result = max(number_list)
  print(f"Maximum{number_list}: {result}")
  return result

def range(number_list: list):
  result = operation.subtract(maximum(number_list), minimum(number_list))
  print(f"Range{number_list}: {result}")
  return result

def mean(number_list: list):
  result = operation.divide(sum(number_list),length(number_list))
  print(f"Mean{number_list}: {result}")
  return result

def median(number_list: list):
  result = operation.statistics.median(number_list)
  print(f"Median{number_list}: {result}")
  return result

def quartiles(number_list: list):
  number_list = sorted(number_list)
  q1_index = int(math.ceil(length(number_list) * 0.25))
  q1_result = number_list[q1_index - 1]
  number_list[0:length(number_list)//2]
  q3_result = statistics.median(number_list)    
  iqr_result = operation.subtract(q3_result, q1_result)
  print(f"Q1: {q1_result}")
  print(f"Q3: {q3_result}")
  print(f"IQR: {iqr_result}")
  return q1_result, q3_result, iqr_result