import math

def add(num1: float) -> float: return lambda num2: num1 + num2
def subtract(num2: float) -> float: return lambda num1: num1 - num2
def multiply(num1: float) -> float: return lambda num2: num1 * num2
def divide(denominator: float) -> float: return lambda numerator: numerator / denominator
def exponentiate(exponent: float) -> float: return  lambda num: num ** exponent
def square_root(num: float) -> float: return  math.sqrt(num) # TODO: use herons_method()
def square(): 
  """Squares a number"""
  return  exponentiate(2)
# def ratio(num1): return  lambda num2: divide(num1)(num2) # TODO: provide as {numerator and denominator object?}

def factorial(number: int) -> int:
  working_string = ""
  result = 1

  for i in range(number, 0, -1):
    result: int = multiply(result)(i)
    working_string = f"{working_string} {i} x"

  working_string = f"{number}! = {working_string[:-1]} = {result}"

  return result


# def normalize_vector()
# TODO - see TUB MSE Numerical Simulation assignment for method


def vector_multiplication(vector: list[float], scalar: float) -> list[float]:
  result_vector: list[float] = []
  for value in vector:
    result_vector.append(multiply(value)(scalar))
  
  return result_vector

def matrix_multiplication(matrix_a: list[list[float]], matrix_b: list[list[float]]): 
  result = []

  if(range(len(matrix_a[0])) != range(len(matrix_b))):
    return None

  # a = [[1,2], 
  #      [3,4]]
  # b = [[3,4], 
  #      [5,6]]
  
  for row_index in range(len(matrix_a)):
    result_row = []
    for column_index in range(len(matrix_b[0])):
      sum = 0 
      for element_index in range(len(matrix_b)):
        # We go horizontally across matrix_a and vertically down matrix_b
        # Eg. 1*3 + 2*5
        sum = add(sum)(multiply( matrix_a[row_index][element_index])(matrix_b[element_index][column_index]))
      result_row.append(sum)
    result.append(result_row)

  return result

if __name__ == "__main__":
  a = [[1,2], 
       [3,4]]
  b = [[3,4], 
       [5,6]]
  
  print(matrix_multiplication(a,b))