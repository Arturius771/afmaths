import math
def add(num1: float):
  def to(num2: float):
    return num1 + num2
  return to

def subtract(num2: float):
  def from_n(num1: float):
    return num1 - num2
  return from_n

def multiply(num1: float):
  def by(num2: float):
    return num1 * num2
  return by

def divide(denominator: float):
  def by(numerator: float):
    return numerator / denominator
  return by

def exponentiate(exponent: float):
  def num(number: float):
    return number ** exponent
  return num

def square_root(number: float):
    
  return math.sqrt(number)

def factorial(number: int):
  working_string = ""
  result = 1

  for loop in range(number, 0, -1):
    result = multiply(result)(loop)
    working_string = f"{working_string} {loop} x"

  working_string = working_string[:-1]
  working_string = f"{number}! ={working_string} = {result}"

  
  return result

def square() -> function:
  return exponentiate(2)