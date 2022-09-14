import math

from afmaths.lists import list_length, list_maximum, list_mean, list_median, list_minimum, list_quartiles, list_range, list_sorted, list_sum


class AfMaths():
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
    add(num1, num2)
    subtract(num1, num2)    
    multiply(num1, num2)
    divide(num1, num2)
    exponentiate(num1, num2)

def dataplotter(number_list):
  ##MU123
  list_sorted(number_list)
  list_length(number_list)
  list_sum(number_list)    
  list_minimum(number_list)
  list_maximum(number_list)
  list_range((number_list))
  list_mean(number_list)
  list_median(number_list)
  list_quartiles(number_list)

def add(num1, num2):
  result = num1 + num2
  print("Add: {} + {} = {}".format(num1, num2, result))
  return result

def subtract(num1, num2):
  result = num1 - num2
  print("Subtract: {} - {} = {}".format(num1, num2, result))
  return result

def multiply(num1, num2):
  result = num1 * num2
  print("Multiply: {} * {} = {}".format(num1, num2, result))
  return result

def divide(num1, num2):
  if num2 != 0:
      result = num1 / num2
      print("Divide: {} / {} = {}".format(num1, num2, result))
      return result
  else:
      print("Divide: You tried to divide by 0")

def exponentiate(number, exponent):
  result = number ** exponent
  print("Exponent: {} to the power of {} = {}".format(number, exponent, result))
  return result

def square_root(number):
  result = math.sqrt(number)
  print("Square root: {} is {}".format(number, result))
  return result

def factorial(number):
  working_string = ""
  result = 1

  for loop in range(number, 0, -1):
      result = multiply(result, loop)
      working_string = "{} {} x".format(working_string, loop)

  working_string = working_string[:-1]
  working_string = "{}! ={} = {}".format(number, working_string, result)

  print(working_string)
  return result

def euclid(m,n):
    """Given two positive integers, m and n, find their greatest common divisor which is the largest positive integer that divides both evenly."""

    remainder = m % n
    if remainder == 0:
        print("Greatest common divisor for {} and {} = {}".format(m, n, n))
        return n
    else:
        m = n
        n = remainder
        print("m {} n {}".format(m, n))
        euclid(m,n) 