


import math
import statistics

from operation import divide, subtract


sort = lambda number_list: sorted(number_list)
length = lambda number_list: len(number_list)
sum = lambda number_list: math.sum(number_list)
minimum = lambda number_list: min(number_list)
maximum = lambda number_list: max(number_list)
range = lambda number_list: subtract(minimum(number_list))(maximum(number_list))
mean = lambda number_list: divide(length(number_list))(sum(number_list))
median = lambda number_list: statistics.median(number_list)

def quartiles(number_list: list):
  number_list = sorted(number_list)
  q1_index = int(math.ceil(length(number_list) * 0.25))
  q1_result = number_list[q1_index - 1]
  number_list[0:length(number_list)//2]
  q3_result = median(number_list)    
  iqr_result = subtract(q1_result)(q3_result)
  
  return q1_result, q3_result, iqr_result