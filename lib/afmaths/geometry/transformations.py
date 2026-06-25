import math

from astronomy_types import (
    Coordinate2D,
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
from afmaths.physics.space.type_conversion_helpers import vector2d, vector3d
from afmaths.tensors import (
    matrix_vector_multiply_2d,
    matrix_vector_multiply_3d,
)


def translate_ellipse_coordinate(
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

    return Coordinate2D(
        x=central_point.x + relative.x,
        y=central_point.y + relative.y,
    )


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
    relative_point = vector2d(
        Scalar(subtract(point.x)(centre.x)),
        Scalar(subtract(point.y)(centre.y)),
    )

    rotated = orthonormal_frame_transform(
        rotation_matrix_2d(
            vector2d(
                Scalar(math.cos(angle)),
                Scalar(negate(math.sin(angle))),
            ),
            vector2d(
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
        vector2d(
            vector2d(
                x_basis.x,
                y_basis.x,
            ),
            vector2d(
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
        vector3d(
            vector3d(
                x_basis.x,
                y_basis.x,
                z_basis.x,
            ),
            vector3d(
                x_basis.y,
                y_basis.y,
                z_basis.y,
            ),
            vector3d(
                x_basis.z,
                y_basis.z,
                z_basis.z,
            ),
        )
    )


# endregion
