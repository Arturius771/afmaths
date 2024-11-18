


import math
import statistics

from operation import divide, subtract


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
    
  return subtract(minimum(number_list))(maximum(number_list))

def mean(number_list: list):
    
  return divide(length(number_list))(sum(number_list))

def median(number_list: list):
    
  return statistics.median(number_list)

def quartiles(number_list: list):
  number_list = sorted(number_list)
  q1_index = int(math.ceil(length(number_list) * 0.25))
  q1_result = number_list[q1_index - 1]
  number_list[0:length(number_list)//2]
  q3_result = median(number_list)    
  iqr_result = subtract(q1_result)(q3_result)
  
  return q1_result, q3_result, iqr_result