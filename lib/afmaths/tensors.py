from afmaths.physics.space.type_conversion_helpers import make_vector3d
from afmaths.types import TransformationMatrix2D, TransformationMatrix3D
from .operation import SQUARE, add, divide_by, multiply, negate, square_root, subtract
from astronomy_types import (
    Position,
    Scalar,
    Vector2D,
    Vector3D,
    Velocity,
)

# region Factories


def vector_negate(vector: Vector3D) -> Vector3D:
    return make_vector3d(
        negate(vector.x),
        negate(vector.y),
        negate(vector.z),
    )


# endregion


# region Vectors
def dot_product(vector_a: Vector2D[Scalar], vector_b: Vector2D[Scalar]) -> Scalar:
    a = multiply(vector_a.x)(vector_b.x)
    b = multiply(vector_a.y)(vector_b.y)

    return add(a)(b)


def dot_product_3d(vector_a: Vector3D[Scalar], vector_b: Vector3D[Scalar]) -> Scalar:
    """Returns the dot product of two vectors"""
    a = multiply(vector_a.x)(vector_b.x)
    b = multiply(vector_a.y)(vector_b.y)
    c = multiply(vector_a.z)(vector_b.z)

    return add(a)(add(b)(c))


# TODO: check naming
def vector_magnitude(vector: Vector3D[Scalar]) -> Scalar:
    """Returns the magnitude of a vector"""
    return Scalar(
        square_root(add(SQUARE(vector.x))(add(SQUARE(vector.y))(SQUARE(vector.z))))
    )


def vector_normalise(vector: Vector3D) -> Vector3D:
    magnitude = vector_magnitude(vector)

    return make_vector3d(
        divide_by(magnitude)(vector.x),
        divide_by(magnitude)(vector.y),
        divide_by(magnitude)(vector.z),
    )


def vector_multiplication_2d(
    vector: Vector2D[Scalar], scalar: Scalar
) -> Vector2D[Scalar]:
    scalar_multiply = multiply(scalar)
    i = scalar_multiply(vector.x)
    j = scalar_multiply(vector.y)

    return Vector2D(i, j)


def vector_multiplication_3d(
    vector: Vector3D[Scalar], scalar: Scalar
) -> Vector3D[Scalar]:
    scalar_multiply = multiply(scalar)
    i = scalar_multiply(vector.x)
    j = scalar_multiply(vector.y)
    k = scalar_multiply(vector.z)

    return make_vector3d(i, j, k)


def vector_cross_multiplication(
    vector_a: Vector2D[Scalar] | Vector2D[Position] | Vector2D[Velocity],
    vector_b: Vector2D[Scalar] | Vector2D[Position] | Vector2D[Velocity],
) -> Vector2D[Scalar]:
    """Returns the cross product of two 3D vectors"""

    value = vector_cross_multiplication_3d(
        Vector3D[Scalar](vector_a.x, vector_a.y, Scalar(0)),
        Vector3D[Scalar](vector_b.x, vector_b.y, Scalar(0)),
    )

    return Vector2D(value.x, value.y)


def vector_cross_multiplication_3d(
    vector_a: Vector3D[Scalar] | Vector3D[Position] | Vector3D[Velocity],
    vector_b: Vector3D[Scalar] | Vector3D[Position] | Vector3D[Velocity],
) -> Vector3D[Scalar]:
    """Returns the cross product of two 3D vectors"""
    # i = subtract(multiply(vector_a[1])(vector_b[2]))(multiply(vector_a[2])(vector_b[1]))
    # j = subtract(multiply(vector_a[2])(vector_b[0]))(multiply(vector_a[0])(vector_b[2]))
    # k = subtract(multiply(vector_a[0])(vector_b[1]))(multiply(vector_a[1])(vector_b[0]))

    # (a_{2}b_{3}-a_{3}b_{2}),(a_{3}b_{1}-a_{1}b_{3}),(a_{1}b_{2}-a_{2}b_{1})
    a = multiply(vector_a.y)(vector_b.z)
    b = multiply(vector_a.z)(vector_b.y)
    c = multiply(vector_a.z)(vector_b.x)
    d = multiply(vector_a.x)(vector_b.z)
    e = multiply(vector_a.x)(vector_b.y)
    f = multiply(vector_a.y)(vector_b.x)

    i = subtract(b)(a)
    j = subtract(d)(c)
    k = subtract(f)(e)

    return make_vector3d(i, j, k)


def vector_subtract(vector_a: Vector3D, vector_b: Vector3D) -> Vector3D:
    return Vector3D(
        subtract(vector_b.x)(vector_a.x),
        subtract(vector_b.y)(vector_a.y),
        subtract(vector_b.z)(vector_a.z),
    )


def vector_add(vector_a: Vector3D, vector_b: Vector3D) -> Vector3D:
    return Vector3D(
        add(vector_b.x)(vector_a.x),
        add(vector_b.y)(vector_a.y),
        add(vector_b.z)(vector_a.z),
    )


# endregion

# region Matrices


def matrix_vector_multiply_2d(
    matrix: TransformationMatrix2D,
    vector: Vector2D[Scalar],
) -> Vector2D[Scalar]:
    return Vector2D(
        dot_product(matrix.x, vector),
        dot_product(matrix.y, vector),
    )


def matrix_vector_multiply_3d(
    matrix: TransformationMatrix3D,
    vector: Vector3D[Scalar],
) -> Vector3D[Scalar]:
    return make_vector3d(
        dot_product_3d(matrix.x, vector),
        dot_product_3d(matrix.y, vector),
        dot_product_3d(matrix.z, vector),
    )


# endregion
