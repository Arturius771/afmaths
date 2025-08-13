

from functools import reduce
import math
from operation import add, divide, exponentiate, multiply, square, factorial


def sigmoid(input, bias:float = 0):
  #TM358 Section Block 1 section 5
  add_bias = add(bias)
  return divide(add(1)(exponentiate(add_bias(-input))(math.e)))(1)

def inverse_square_law(source_strength, distance_metres):
  ##TM255 block 1
  four_times_pi = multiply(4)(math.pi)
  denominator =  multiply(square(distance_metres))(four_times_pi)
  return divide(denominator)(source_strength)

def taylor_series(value): 
  # Written for sin and cos functions so may not be generic for pure Taylor Series functions.
  def steps(initial_value_in_series, increment = 1, initial_denmoninator = 1, steps = 3, sign = -1):
    taylor = [initial_value_in_series]
    for _ in range(steps):
      exponent = exponentiate(initial_denmoninator)
      fact = factorial(initial_denmoninator)
      division = divide(fact)
      taylor.append(division(exponent(value)))
      initial_denmoninator += increment

    for index in range(len(taylor)):
      sign = -1 if sign == +1 else +1
      taylor[index] = taylor[index] * sign

    return reduce(lambda a,b: a+b, taylor)
  return steps

def herons_method(value: float):
  """
  O(log precision) method for calculating square roots. The square roots of two values (eg. 25, 2982186) will be calculated in the same number of cycles to the same precision
  """
  # www.youtube.com/watch?v=l2TCgS_eLwA
  initial_estimate = value / 2
  current_step = initial_estimate
  epsilon = value * exponentiate(-9)(10)

  while(True):
    next_step = (1/2 * (current_step + (value / current_step)))
    if(next_step < epsilon):
      break
    current_step = next_step

  return current_step
