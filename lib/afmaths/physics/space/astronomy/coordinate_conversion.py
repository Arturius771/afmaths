from astronomy_types import (
    Coordinate3D,
    NewType,
    Scalar,
    Vector3D,
)

from afmaths.physics.space.astronomy.type_conversion_helpers import (
    coordinate3d_to_vector3d,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_multiplication_3d,
)

EarthCentredInertial = NewType("EarthCentredInertial", Vector3D[Scalar])


def orthonormal_frame_transform(
    transformaton_matrix: Vector3D[Vector3D[Scalar]], vector: Vector3D[Scalar]
) -> Vector3D[Scalar]:
    """Transforms a vector from one coordinate system to another using an orthonormal transformation matrix. IE. a rotation matrix (changing the perspective)."""
    return Vector3D(
        dot_product_3d(transformaton_matrix.x, vector),
        dot_product_3d(transformaton_matrix.y, vector),
        dot_product_3d(transformaton_matrix.z, vector),
    )


def vector_from_coordinates(
    coordinates: Coordinate3D,
    magnitude: Scalar,
) -> Vector3D[Scalar]:
    return vector_multiplication_3d(
        coordinate3d_to_vector3d(coordinates),
        magnitude,
    )
