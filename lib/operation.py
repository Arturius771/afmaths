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

def euclid(m: int, n: int):
    """Given two positive integers, m and n, find their greatest common divisor which is the largest positive integer that divides both evenly."""

    remainder = m % n
    if remainder == 0:
      return n
    else:
      m = n
      n = remainder
      euclid(m,n)

def sieve_of_eratosthenes(n: int):
  """Finds prime numbers up to n"""
  # https://www.youtube.com/watch?v=fwxjMKBMR7s
  numbers = [True] * n 
  primes = []
  
  for index in range(2, n):
    if numbers[index]:
      primes.append(index)
      for multiple in range(index*index,n,index):
        numbers[multiple] = False

  return primes
