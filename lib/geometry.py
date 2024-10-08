import operation

def pythagoras(a,b):
    
  return operation.square_root(operation.add(operation.exponentiate(a, 2), operation.exponentiate(b, 2)))

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