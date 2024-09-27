import operation
import math

def sigmoid(input, bias:float = 0):
  #TM358 Section Block 1 section 5
  return (operation.divide(1,operation.add(1,operation.exponentiate(math.e, operation.add(-input, bias)))))

def inverse_square_law(source_strength, distance_metres):
  ##TM255 block 1
  denominator = operation.multiply(operation.exponentiate(distance_metres, 2), operation.multiply(4, math.pi))
  return operation.divide(source_strength, denominator)


# def derivative_exponentiated(exponent_value: float):
#   # Other types of derivatives can be calculated using differentiating from first principles
#   # x = Symbol('x')
#   f = x**exponent_value
#   return f.diff(x)