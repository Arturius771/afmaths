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
  list.sort(number_list)
  list.length(number_list)
  list.sum(number_list)    
  list.minimum(number_list)
  list.maximum(number_list)
  list.range((number_list))
  list.mean(number_list)
  list.median(number_list)
  list.quartiles(number_list)