from operation import divide, multiply, subtract, termial

def gradient(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculates the slope between two points"""
  ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
    return divide(subtract(x1)(x2))(subtract(y1)(y2))

def equation_of_line(x1: float, y1: float, x2: float, y2: float) -> tuple[float, float]:
  """Returns the slope and y-intercept of the line passing through two points"""
  ##m = gradient
  m = gradient(x1, y1, x2, y2)
  ##b = y intercept when x = 0
  rhs = multiply(m)(x1)
  b = subtract(rhs)(y1)
  ##y = mx + b
  return (m,b)

def interpolations_for_bezier_curve(points: int) -> int:
  """Calculates the number of interpolations needed for a bezier curve with a given number of control points
    interpolations = n(n+1)/2 
  """
  # if points < 2:
  #   return 0
  # return points - 1 + interpolations_for_bezier_curve(points - 1)
  return termial(points)