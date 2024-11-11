

import math
from operation import add, divide, exponentiate, multiply


def sigmoid(input, bias:float = 0):
  #TM358 Section Block 1 section 5
  return (divide(1,add(1,exponentiate(math.e, add(-input, bias)))))

def inverse_square_law(source_strength, distance_metres):
  ##TM255 block 1
  denominator = multiply(exponentiate(distance_metres, 2), multiply(4, math.pi))
  return divide(source_strength, denominator)


# def derivative_exponentiated(exponent_value: float):
#   # Other types of derivatives can be calculated using differentiating from first principles
#   # x = Symbol('x')
#   f = x**exponent_value
#   return f.diff(x)