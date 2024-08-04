import operation
import math
import statistics

def sort(number_list: list):
    
  return sorted(number_list)

def length(number_list: list):
    
  return len(number_list)

def sum(number_list: list):
    
  return math.sum(number_list)

def minimum(number_list: list):
    
  return min(number_list)

def maximum(number_list: list):
    
  return max(number_list)

def range(number_list: list):
    
  return operation.subtract(maximum(number_list), minimum(number_list))

def mean(number_list: list):
    
  return operation.divide(sum(number_list),length(number_list))

def median(number_list: list):
    
  return statistics.median(number_list)

def quartiles(number_list: list):
  number_list = sorted(number_list)
  q1_index = int(math.ceil(length(number_list) * 0.25))
  q1_result = number_list[q1_index - 1]
  number_list[0:length(number_list)//2]
  q3_result = median(number_list)    
  iqr_result = operation.subtract(q3_result, q1_result)
  
  return q1_result, q3_result, iqr_result