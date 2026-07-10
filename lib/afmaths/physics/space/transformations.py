import math
from astronomy_types import (
    Coordinate3D,
    Degrees,
    Distance,
    GeographicCoordinates,
    OrbitalElements,
    Scalar,
    Vector3D,
)
from afmaths.geometry.transformations import (
    orthonormal_frame_transform_3d,
    rotation_matrix_3d,
)
from afmaths.physics.space.type_conversion_helpers import make_vector2d, make_vector3d
from afmaths.tensors import vector_magnitude, vector_magnitude_3d
from afmaths.types import TransformationMatrix3D


def transform_element_reference_frame_from_perifocal_vector(
    orbital_elements: OrbitalElements,
    perifocal_vector: Vector3D[Scalar],
) -> Vector3D[Scalar]:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    return orthonormal_frame_transform_3d(
        transform_element_reference_frame_from_perifocal(orbital_elements),
        perifocal_vector,
    )


def transform_geographic_coordinates_from_itrs(
    coords: Coordinate3D[Scalar],
) -> GeographicCoordinates:
    """Converts ITRS cartesian coordinates to geographic Lat/Lon (degrees). Useful for ground track plotting."""
    return GeographicCoordinates(
        Degrees(
            Scalar(
                math.degrees(
                    math.atan2(
                        coords.z, vector_magnitude(make_vector2d(coords.x, coords.y))
                    )
                )
            )
        ),
        Degrees(Scalar(math.degrees(math.atan2(coords.y, coords.x)))),
    )


# TODO: Maybe move this?
def radius_from_itrs(coords: Coordinate3D[Scalar]) -> Distance:
    return Distance(vector_magnitude_3d(make_vector3d(coords.x, coords.y, coords.z)))


# region Transformation Matrices


def transform_element_reference_frame_from_perifocal(
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
