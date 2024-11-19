import math

add = lambda num1: lambda num2: num1 + num2
subtract = lambda num2: lambda num1: num1 - num2
multiply = lambda num1: lambda num2: num1 * num2
divide = lambda denominator: lambda numerator: numerator / denominator
exponentiate = lambda exponent: lambda num: num ** exponent
square_root = lambda num: math.sqrt(num)
square = exponentiate(2)
ratio = lambda num1: lambda num2: divide(num1)(num2)

def factorial(number: int):
  working_string = ""
  result = 1

  for i in range(number, 0, -1):
    result = multiply(result)(i)
    working_string = f"{working_string} {i} x"

  working_string = f"{number}! = {working_string[:-1]} = {result}"

  return result