import math
def add(num1: float, num2: float):
    
  return num1 + num2

def subtract(num1: float, num2: float):
    
  return num1 - num2

def multiply(num1: float, num2: float):
    
  return num1 * num2

def divide(num1: float, num2: float):
      
  return num1 / num2
    
def exponentiate(number: float, exponent: float):
    
  return number ** exponent

def square_root(number: float):
    
  return math.sqrt(number)

def factorial(number: int):
  working_string = ""
  result = 1

  for loop in range(number, 0, -1):
    result = multiply(result, loop)
    working_string = f"{working_string} {loop} x"

  working_string = working_string[:-1]
  working_string = f"{number}! ={working_string} = {result}"

  
  return result


