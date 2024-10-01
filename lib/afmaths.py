import list
import operation


def test(num1, num2):
  """
  Tests the basic operations
  """
  operation.add(num1, num2)
  operation.subtract(num1, num2)    
  operation.multiply(num1, num2)
  operation.divide(num1, num2)
  operation.exponentiate(num1, num2)

def dataplotter(number_list):
  ##MU123
  """
  Runs some useful functions on a provided list
  """
  list.sort(number_list)
  list.length(number_list)
  list.sum(number_list)    
  list.minimum(number_list)
  list.maximum(number_list)
  list.range((number_list))
  list.mean(number_list)
  list.median(number_list)
  list.quartiles(number_list)