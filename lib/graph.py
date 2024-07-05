import operation

def graph_gradient(x1, y1, x2, y2):
  ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
  try:
    result = operation.divide(operation.subtract(y2, y1), operation.subtract(x2, x1))
    print(f"The gradient of line with coordinates ({x1}, {y1}) and ({x2}, {y2}) is: {result}")
    return result
  except TypeError:
    print("Gradient: You probably have a vertical line")    

def graph_equation_of_line(x1, y1, x2, y2):
  ##y = mx + b
  ##m = gradient
  ##b = y intercept when x = 0
  try:
    m = graph_gradient(x1, y1, x2, y2)
    rhs = operation.multiply(m, x1)
    b = operation.subtract(y1, rhs)
    if b < 0:
      print(f"Equation of line: y = {m}x {b}")
    else:
      print(f"Equation of line: y = {m}x + {b}")
    return b
  except TypeError:
    print("Equation of Line: You probably have a vertical line")