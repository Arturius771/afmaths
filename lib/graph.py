import operation

def gradient(x1, y1, x2, y2):
  ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
  result = operation.divide(operation.subtract(y2, y1), operation.subtract(x2, x1))
  return result

def equation_of_line(x1, y1, x2, y2):
  ##y = mx + b
  ##m = gradient
  ##b = y intercept when x = 0
  m = gradient(x1, y1, x2, y2)
  rhs = operation.multiply(m, x1)
  b = operation.subtract(y1, rhs)
  return (m,b)