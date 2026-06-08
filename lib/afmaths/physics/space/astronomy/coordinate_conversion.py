import math

from astronomy_types import (
    Coordinate3D,
    NewType,
    OrbitalElements,
    Scalar,
    Vector3D,
)

from afmaths.physics.space.astronomy.type_conversion_helpers import (
    coordinate3d_to_vector3d,
)
from afmaths.tensors import (
    RotationMatrix,
    dot_product_3d,
    rotation_matrix,
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


def transform_perifocal_to_earth_centred_inertial(
    transposed_PQW: RotationMatrix,
    perifocal_vector: Vector3D[Scalar],
) -> EarthCentredInertial:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    # TODO: reuse
    return EarthCentredInertial(
        orthonormal_frame_transform(transposed_PQW, perifocal_vector)
    )


def vector_from_coordinates(
    coordinates: Coordinate3D,
    magnitude: Scalar,
) -> Vector3D[Scalar]:
    return vector_multiplication_3d(
        coordinate3d_to_vector3d(coordinates),
        magnitude,
    )


def eci_rotation_matrix_from_orbital_elements(
    orbital_elements: OrbitalElements,
) -> RotationMatrix:
    argument_of_perigee = orbital_elements.argument_of_perigee
    right_ascension_of_ascening_node = (
        orbital_elements.right_ascension_of_ascending_node
    )
    inclination = orbital_elements.inclination

    p = [
        math.cos(argument_of_perigee) * math.cos(right_ascension_of_ascening_node)
        - math.sin(argument_of_perigee)
        * math.cos(inclination)
        * math.sin(right_ascension_of_ascening_node),
        math.cos(argument_of_perigee) * math.sin(right_ascension_of_ascening_node)
        + math.sin(argument_of_perigee)
        * math.cos(inclination)
        * math.cos(right_ascension_of_ascening_node),
        math.sin(argument_of_perigee) * math.sin(inclination),
    ]

    q = [
        -math.sin(argument_of_perigee) * math.cos(right_ascension_of_ascening_node)
        - math.cos(argument_of_perigee)
        * math.cos(inclination)
        * math.sin(right_ascension_of_ascening_node),
        -math.sin(argument_of_perigee) * math.sin(right_ascension_of_ascening_node)
        + math.cos(argument_of_perigee)
        * math.cos(inclination)
        * math.cos(right_ascension_of_ascening_node),
        math.cos(argument_of_perigee) * math.sin(inclination),
    ]

    w = [
        math.sin(inclination) * math.sin(right_ascension_of_ascening_node),
        -math.sin(inclination) * math.cos(right_ascension_of_ascening_node),
        math.cos(inclination),
    ]

    return rotation_matrix(
        Vector3D(Scalar(p[0]), Scalar(p[1]), Scalar(p[2])),
        Vector3D(Scalar(q[0]), Scalar(q[1]), Scalar(q[2])),
        Vector3D(Scalar(w[0]), Scalar(w[1]), Scalar(w[2])),
    )
