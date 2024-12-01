
from operation import add, divide, square
import math
from formula import taylor_series

pythagoras = lambda a: lambda b: add(square(a))(square(b))

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

def tangent(angle_degrees):
  """Returns a value in radians"""
  return divide(cosine(angle_degrees))(sine(angle_degrees))

def arctangent(radians): return math.degrees(math.atan(radians))

def sine(angle_degrees):
  """Returns a value in radians"""
  return taylor_series(math.radians(angle_degrees))(math.radians(angle_degrees),2,3)

def cosine(angle_degrees):
  """Returns a value in radians"""
  return taylor_series(math.radians(angle_degrees))(1,2,2)