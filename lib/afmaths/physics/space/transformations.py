import math
from afmaths.constants import EarthCentredInertialFrame, TransformationMatrix3D
from astronomy_types import OrbitalElements, Scalar, Vector3D
from afmaths.geometry.transformations import (
    orthonormal_frame_transform_3d,
    rotation_matrix_3d,
)
from afmaths.physics.space.type_conversion_helpers import vector3d


def transform_perifocal_to_inertial(
    perifocal_to_eci_rotation_matrix: TransformationMatrix3D,
    perifocal_vector: Vector3D[Scalar],
) -> EarthCentredInertialFrame:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    # TODO: reuse
    return EarthCentredInertialFrame(
        orthonormal_frame_transform_3d(
            perifocal_to_eci_rotation_matrix, perifocal_vector
        )
    )


# region Factories


def perifocal_to_inertial_frame_rotation_matrix(
    orbital_elements: OrbitalElements,
) -> TransformationMatrix3D:
    argument_of_perigee = orbital_elements.argument_of_periapsis
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

    return rotation_matrix_3d(
        vector3d(Scalar(p[0]), Scalar(p[1]), Scalar(p[2])),
        vector3d(Scalar(q[0]), Scalar(q[1]), Scalar(q[2])),
        vector3d(Scalar(w[0]), Scalar(w[1]), Scalar(w[2])),
    )


# endregion
