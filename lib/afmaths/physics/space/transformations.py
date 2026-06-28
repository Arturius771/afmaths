import math
from afmaths.constants import TransformationMatrix3D
from astronomy_types import OrbitalElements, Scalar, Vector3D
from afmaths.geometry.transformations import (
    orthonormal_frame_transform_3d,
    rotation_matrix_3d,
)
from afmaths.physics.space.type_conversion_helpers import make_vector3d


def transform_perifocal_vector_to_element_reference_frame(
    orbital_elements: OrbitalElements,
    perifocal_vector: Vector3D[Scalar],
) -> Vector3D[Scalar]:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    return orthonormal_frame_transform_3d(
        perifocal_to_element_reference_frame_transformation(orbital_elements),
        perifocal_vector,
    )


# region Factories


def perifocal_to_element_reference_frame_transformation(
    orbital_elements: OrbitalElements,
) -> TransformationMatrix3D:
    """
    Build the transformation matrix from the orbit's perifocal frame (PQW) to the reference frame used by the orbital elements.

    If Ω, i, ω are GCRS-referenced:
        perifocal → GCRS

    If Ω, i, ω are EME2000-referenced:
        perifocal → EME2000

    If Ω, i, ω are TEME-referenced:
        perifocal → TEME"""

    p = [
        math.cos(orbital_elements.argument_of_periapsis)
        * math.cos(orbital_elements.right_ascension_of_ascending_node)
        - math.sin(orbital_elements.argument_of_periapsis)
        * math.cos(orbital_elements.inclination)
        * math.sin(orbital_elements.right_ascension_of_ascending_node),
        math.cos(orbital_elements.argument_of_periapsis)
        * math.sin(orbital_elements.right_ascension_of_ascending_node)
        + math.sin(orbital_elements.argument_of_periapsis)
        * math.cos(orbital_elements.inclination)
        * math.cos(orbital_elements.right_ascension_of_ascending_node),
        math.sin(orbital_elements.argument_of_periapsis)
        * math.sin(orbital_elements.inclination),
    ]

    q = [
        -math.sin(orbital_elements.argument_of_periapsis)
        * math.cos(orbital_elements.right_ascension_of_ascending_node)
        - math.cos(orbital_elements.argument_of_periapsis)
        * math.cos(orbital_elements.inclination)
        * math.sin(orbital_elements.right_ascension_of_ascending_node),
        -math.sin(orbital_elements.argument_of_periapsis)
        * math.sin(orbital_elements.right_ascension_of_ascending_node)
        + math.cos(orbital_elements.argument_of_periapsis)
        * math.cos(orbital_elements.inclination)
        * math.cos(orbital_elements.right_ascension_of_ascending_node),
        math.cos(orbital_elements.argument_of_periapsis)
        * math.sin(orbital_elements.inclination),
    ]

    w = [
        math.sin(orbital_elements.inclination)
        * math.sin(orbital_elements.right_ascension_of_ascending_node),
        -math.sin(orbital_elements.inclination)
        * math.cos(orbital_elements.right_ascension_of_ascending_node),
        math.cos(orbital_elements.inclination),
    ]

    return rotation_matrix_3d(
        make_vector3d(Scalar(p[0]), Scalar(p[1]), Scalar(p[2])),
        make_vector3d(Scalar(q[0]), Scalar(q[1]), Scalar(q[2])),
        make_vector3d(Scalar(w[0]), Scalar(w[1]), Scalar(w[2])),
    )


# endregion
