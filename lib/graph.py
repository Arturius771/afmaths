from dataclasses import dataclass

from operation import divide, multiply, subtract, termial


@dataclass(frozen=True)
class GraphCoordinates:
    x: float
    y: float


def slope_gradiant(point1: GraphCoordinates, point2: GraphCoordinates) -> float:
    """Calculates the slope between two points"""
    ##https://www.bbc.co.uk/bitesize/topics/zvhs34j/articles/z4ctng8
    return divide(subtract(point1.x)(point2.x))(subtract(point1.y)(point2.y))


def equation_of_line(
    point1: GraphCoordinates, point2: GraphCoordinates
) -> tuple[float, float]:
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
