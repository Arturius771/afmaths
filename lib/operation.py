import math
def add(num1: float, num2: float):
  result = num1 + num2
  print(f"Add: {num1} + {num2} = {result}")
  return result

def subtract(num1: float, num2: float):
  result = num1 - num2
  print(f"Subtract: {num1} - {num2} = {result}")
  return result

def multiply(num1: float, num2: float):
  result = num1 * num2
  print(f"Multiply: {num1} * {num2} = {result}")
  return result

def divide(num1: float, num2: float):
  if num2 != 0:
    result = num1 / num2
    print(f"Divide: {num1} / {num2} = {result}")
    return result
  else:
    print("Divide: You tried to divide by 0")

def exponentiate(number: float, exponent: float):
  result = number ** exponent
  print(f"Exponent: {number} ^ {exponent} = {result}")
  return result

def square_root(number: float):
  result = math.sqrt(number)
  print(f"Square root of {number} is {result}")
  return result

def factorial(number: int):
  working_string = ""
  result = 1

  for loop in range(number, 0, -1):
    result = multiply(result, loop)
    working_string = f"{working_string} {loop} x"

  working_string = working_string[:-1]
  working_string = f"{number}! ={working_string} = {result}"

  print(working_string)
  return result

def euclid(m: int, n: int):
    """Given two positive integers, m and n, find their greatest common divisor which is the largest positive integer that divides both evenly."""

    remainder = m % n
    if remainder == 0:
      print(f"Greatest common divisor for {m} and {n} = {n}")
      return n
    else:
      m = n
      n = remainder
      print(f"m {m} n {n}")
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

  if n < 500:
    print(f"All primes up to {n} = {primes}")
  else:
    print(f"There are {len(primes)} primes up to {n}. The last prime is {primes[-1]}") # Printing all primes is not practical above a certain amount

  return primes