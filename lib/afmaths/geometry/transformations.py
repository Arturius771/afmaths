import math

from astronomy_types import (
    Coordinate2D,
    Coordinate3D,
    Degrees,
    Scalar,
    SemiMajorAxis,
    SemiMinorAxis,
    EccentricAnomaly,
    Vector2D,
    Vector3D,
)

from afmaths.constants import TransformationMatrix2D, TransformationMatrix3D
from afmaths.operation import add, multiply, negate, subtract
from afmaths.physics.space.type_conversion_helpers import make_vector2d, make_vector3d
from afmaths.tensors import (
    matrix_vector_multiply_2d,
    matrix_vector_multiply_3d,
)


def translate_coordinate(coord: Coordinate2D, offset: Vector2D) -> Coordinate2D:
    return Coordinate2D(x=add(coord.x)(offset.x), y=add(coord.y)(offset.y))


def translate_coordinate_3d(coord: Coordinate3D, offset: Vector3D) -> Coordinate3D:
    return Coordinate3D(
        x=add(coord.x)(offset.x), y=add(coord.y)(offset.y), z=add(coord.z)(offset.z)
    )


def translate_ellipse(
    central_point: Coordinate2D,
    a: SemiMajorAxis,
    b: SemiMinorAxis,
    E: EccentricAnomaly,
) -> Coordinate2D:

    relative = ellipse_perimeter_coordinate_from_eccentric_anomaly(
        a,
        b,
        E,
    )

    return translate_coordinate(central_point, make_vector2d(relative.x, relative.y))


def ellipse_perimeter_coordinate_from_eccentric_anomaly(
    a: SemiMajorAxis,
    b: SemiMinorAxis,
    E: EccentricAnomaly,
) -> Coordinate2D:
    return Coordinate2D(
        x=multiply(a)(math.cos(E)),
        y=multiply(b)(math.sin(E)),
    )


def rotate_point_around_centre(
    point: Coordinate2D,
    angle: Degrees,
    centre: Coordinate2D = Coordinate2D(0, 0),
) -> Coordinate2D:
    relative_point = make_vector2d(
        Scalar(subtract(point.x)(centre.x)),
        Scalar(subtract(point.y)(centre.y)),
    )

    rotated = orthonormal_frame_transform(
        rotation_matrix_2d(
            make_vector2d(
                Scalar(math.cos(angle)),
                Scalar(negate(math.sin(angle))),
            ),
            make_vector2d(
                Scalar(math.sin(angle)),
                Scalar(math.cos(angle)),
            ),
        ),
        relative_point,
    )

    return Coordinate2D(
        add(centre.x)(rotated.x),
        add(centre.y)(rotated.y),
    )


# region Transform Helpers


def orthonormal_frame_transform(
    transformation_matrix: TransformationMatrix2D,
    vector: Vector2D[Scalar],
) -> Vector2D[Scalar]:
    return matrix_vector_multiply_2d(transformation_matrix, vector)


def orthonormal_frame_transform_3d(
    transformation_matrix: TransformationMatrix3D,
    vector: Vector3D[Scalar],
) -> Vector3D[Scalar]:
    return matrix_vector_multiply_3d(transformation_matrix, vector)


# endregion


# region Factories


def rotation_matrix_2d(
    x_basis: Vector2D[Scalar],
    y_basis: Vector2D[Scalar],
) -> TransformationMatrix2D:
    return TransformationMatrix2D(
        make_vector2d(
            make_vector2d(
                x_basis.x,
                y_basis.x,
            ),
            make_vector2d(
                x_basis.y,
                y_basis.y,
            ),
        )
    )


def rotation_matrix_3d(
    x_basis: Vector3D[Scalar],
    y_basis: Vector3D[Scalar],
    z_basis: Vector3D[Scalar],
) -> TransformationMatrix3D:
    return TransformationMatrix3D(
        make_vector3d(
            make_vector3d(
                x_basis.x,
                y_basis.x,
                z_basis.x,
            ),
            make_vector3d(
                x_basis.y,
                y_basis.y,
                z_basis.y,
            ),
            make_vector3d(
                x_basis.z,
                y_basis.z,
                z_basis.z,
            ),
        )
    )


# endregion
