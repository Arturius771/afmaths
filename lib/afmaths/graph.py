from afmaths.operation import divide_by, multiply, subtract, termial

from astronomy_types import Coordinate2D


def slope_gradiant(point1: Coordinate2D, point2: Coordinate2D) -> float:
    """Calculates the slope between two points"""
    ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
    return divide_by(subtract(point1.x)(point2.x))(subtract(point1.y)(point2.y))


def equation_of_line(point1: Coordinate2D, point2: Coordinate2D) -> tuple[float, float]:
    """Returns the slope and y-intercept of the line passing through two points"""
    ##m = gradient
    m = slope_gradiant(point1, point2)
    ##b = y intercept when x = 0
    rhs = multiply(m)(point1.x)
    b = subtract(rhs)(point1.y)
    ##y = mx + b
    return (m, b)


def interpolations_for_bezier_curve(number_of_control_points: int) -> int:
    """Calculates the number of interpolations needed for a bezier curve with a given number of control points
    interpolations = n(n+1)/2
    """
    # if points < 2:
    #   return 0
    # return points - 1 + interpolations_for_bezier_curve(points - 1)
    return termial(number_of_control_points)
