import math

def add(num1: float) -> float: return lambda num2: num1 + num2
def subtract(num2: float) -> float: return lambda num1: num1 - num2
def multiply(num1: float) -> float: return lambda num2: num1 * num2
def divide(denominator: float) -> float: return lambda numerator: numerator / denominator
def exponentiate(exponent: float) -> float: return  lambda num: num ** exponent
def square_root(num: float) -> float: return  math.sqrt(num) # TODO: use herons_method()
def square(): 
  """Squares a number"""
  return  exponentiate(2)
# def ratio(num1): return  lambda num2: divide(num1)(num2) # TODO: provide as {numerator and denominator object?}

def factorial(number: int):
  working_string = ""
  result = 1

  for i in range(number, 0, -1):
    result = multiply(result)(i)
    working_string = f"{working_string} {i} x"

  working_string = f"{number}! = {working_string[:-1]} = {result}"

  return result


# def normalize_vector()
# TODO - see TUB MSE Numerical Simulation assignment for method