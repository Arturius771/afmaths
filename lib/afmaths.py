
from list import length, maximum, mean, median, minimum, quartiles, sort
from operation import add, divide, exponentiate, multiply, subtract


def test(num1, num2):
  """
  Tests the basic operations
  """
  add(num1)(num2)
  subtract(num2)(num1)    
  multiply(num1)(num2)
  divide(num2)(num1)
  exponentiate(num2)(num1)

def dataplotter(number_list):
  ##MU123
  """
  Runs some useful functions on a provided list
  """
  sort(number_list)
  length(number_list)
  sum(number_list)    
  minimum(number_list)
  maximum(number_list)
  range((number_list))
  mean(number_list)
  median(number_list)
  quartiles(number_list)