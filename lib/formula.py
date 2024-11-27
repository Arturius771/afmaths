

import math
from operation import add, divide, exponentiate, multiply, square


def sigmoid(input, bias:float = 0):
  #TM358 Section Block 1 section 5
  add_bias = add(bias)
  return divide(add(1)(exponentiate(add_bias(-input))(math.e)))(1)

def inverse_square_law(source_strength, distance_metres):
  ##TM255 block 1
  four_times_pi = multiply(4)(math.pi)
  denominator =  multiply(square(distance_metres))(four_times_pi)
  return divide(denominator)(source_strength)