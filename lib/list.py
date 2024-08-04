import operation
import math
import statistics

def sort(number_list: list):
  result = sorted(number_list)
  
  return result

def length(number_list: list):
  result = len(number_list)
  
  return result

def sum(number_list: list):
  result = math.sum(number_list)
  
  return result

def minimum(number_list: list):
  result = min(number_list)
  
  return result

def maximum(number_list: list):
  result = max(number_list)
  
  return result

def range(number_list: list):
  result = operation.subtract(maximum(number_list), minimum(number_list))
  
  return result

def mean(number_list: list):
  result = operation.divide(sum(number_list),length(number_list))
  
  return result

def median(number_list: list):
  result = statistics.median(number_list)
  
  return result

def quartiles(number_list: list):
  number_list = sorted(number_list)
  q1_index = int(math.ceil(length(number_list) * 0.25))
  q1_result = number_list[q1_index - 1]
  number_list[0:length(number_list)//2]
  q3_result = statistics.median(number_list)    
  iqr_result = operation.subtract(q3_result, q1_result)
  
  return q1_result, q3_result, iqr_result