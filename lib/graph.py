

from operation import divide, multiply, subtract


def gradient(x1, y1, x2, y2):
  ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
    return divide(subtract(x1)(x2))(subtract(y1)(y2))

def equation_of_line(x1, y1, x2, y2):
  ##m = gradient
  m = gradient(x1, y1, x2, y2)
  ##b = y intercept when x = 0
  rhs = multiply(m)(x1)
  subtractRhs = subtract(rhs)
  b = subtractRhs(y1)
  ##y = mx + b
  return (m,b)