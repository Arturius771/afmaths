from astronomy_types import (
    PositionVector,
    Scalar,
    Vector3D,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_multiplication_3d,
    vector_negate,
    vector_normalise,
)


def orthonormal_frame_transform(
    transformaton_matrix: Vector3D[Vector3D[Scalar]], vector: Vector3D[Scalar]
) -> Vector3D[Scalar]:
    """Transforms a vector from one coordinate system to another using an orthonormal transformation matrix. IE. a rotation matrix (changing the perspective)."""
    return Vector3D(
        dot_product_3d(transformaton_matrix.x, vector),
        dot_product_3d(transformaton_matrix.y, vector),
        dot_product_3d(transformaton_matrix.z, vector),
    )


def vector_from_direction(
    direction: Vector3D[Scalar],
    magnitude: Scalar,
) -> Vector3D[Scalar]:
    return vector_multiplication_3d(direction, magnitude)


def nadir_vector(position: PositionVector) -> Vector3D:
    return vector_negate(zenith_vector(position))


def zenith_vector(position: PositionVector) -> Vector3D:
    return vector_normalise(position)
