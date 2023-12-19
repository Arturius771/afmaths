import list
import operation


def test(num1, num2):
  """
  Tests the basic operations

  Other functions called:
  :add (num1 + num2)
  :subtract (num1 - num2)
  :multiply( num1 * num2)
  :divide( num1 / num2)
  :exponentiate( num1 ^ num2)
  """
  operation.add(num1, num2)
  operation.subtract(num1, num2)    
  operation.multiply(num1, num2)
  operation.divide(num1, num2)
  operation.exponentiate(num1, num2)

def dataplotter(number_list):
  ##MU123
  list.list_sorted(number_list)
  list.list_length(number_list)
  list.list_sum(number_list)    
  list.list_minimum(number_list)
  list.list_maximum(number_list)
  list.list_range((number_list))
  list.list_mean(number_list)
  list.list_median(number_list)
  list.list_quartiles(number_list)






  






