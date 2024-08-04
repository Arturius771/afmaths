import operation
import math

def sigmoid(input, bias:float = 0):
  "TM358 Section Block 1 section 5"
  return (operation.divide(1,operation.add(1,operation.exponentiate(math.e, operation.add(-input, bias)))))

# def derivative_exponentiated(exponent_value: float):
#   # Other types of derivatives can be calculated using differentiating from first principles
#   # x = Symbol('x')
#   f = x**exponent_value
#   return f.diff(x)