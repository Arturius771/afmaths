

from operation import divide, multiply, subtract


def gradient(x1, y1, x2, y2):
  ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
    return divide(subtract(x1)(x2))(subtract(y1)(y2))

def equation_of_line(x1, y1, x2, y2):
  ##y = mx + b
  ##m = gradient
  ##b = y intercept when x = 0
  m = gradient(x1, y1, x2, y2)
  rhs = multiply(m)(x1)
  subtractRhs = subtract(rhs)
  b = subtractRhs(y1)
  return (m,b)