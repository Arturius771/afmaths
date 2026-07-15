import math
from astronomy_types import (
    Degrees,
    Epoch,
    GeographicCoordinates,
    JulianDate,
    Minute,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    Scalar,
    Second,
    Vector3D,
)
from afmaths.constants import MINUTES_PER_DAY
from afmaths.geometry.transformations import (
    orthonormal_frame_transform_3d,
    rotation_matrix_3d,
)
from afmaths.operation import DOUBLE, add, multiply, negate
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    greenwich_mean_sidereal_time_radians_from_julian_date,
    j200_from_julian_Date,
    seconds_from_minutes,
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
    itrs: PositionVector,
) -> GeographicCoordinates:
    """Converts ITRS cartesian coordinates to geographic Lat/Lon (degrees). Useful for ground track plotting."""
    return GeographicCoordinates(
        Degrees(
            Scalar(
                math.degrees(
                    math.atan2(itrs.z, vector_magnitude(make_vector2d(itrs.x, itrs.y)))
                )
            )
        ),
        Degrees(Scalar(math.degrees(math.atan2(itrs.y, itrs.x)))),
    )


def earth_rotation_angle(jd: JulianDate) -> Radians:
    # ISG lecture no. 2
    return Radians(
        Scalar(
            DOUBLE(
                multiply(math.pi)(
                    add(0.7790572732640)(
                        multiply(1.00273781191135448)(j200_from_julian_Date(jd))
                    )
                )
            )
            % DOUBLE(math.pi)
        )
    )


def itrs_position_from_gmst_passive(
    gmst: Radians, gcrs_position: PositionVector
) -> PositionVector:
    """Simplified conversion not taking into account any perturbations or time compatibility."""
    itrs_position = orthonormal_frame_transform_3d(
        z_axis_passive_rotation(gmst),
        make_vector3d(gcrs_position.x, gcrs_position.y, gcrs_position.z),
    )
    return PositionVector(
        Position(itrs_position.x), Position(itrs_position.y), Position(itrs_position.z)
    )


def itrs_position_from_gmst(
    gmst: Radians, gcrs_position: PositionVector
) -> PositionVector:
    itrs_position = orthonormal_frame_transform_3d(
        z_axis_active_rotation(gmst),
        make_vector3d(gcrs_position.x, gcrs_position.y, gcrs_position.z),
    )
    return PositionVector(
        Position(itrs_position.x), Position(itrs_position.y), Position(itrs_position.z)
    )


def itrs_position_from_gcrs_position(
    jd: JulianDate, gcrs_position: PositionVector
) -> PositionVector:
    gmst = greenwich_mean_sidereal_time_radians_from_julian_date(jd)
    return itrs_position_from_gmst_passive(gmst, gcrs_position)


def itrs_positions_from_gcrs_position(
    gcrs_positions: list[PositionVector],
    epoch: Epoch,
) -> list[PositionVector]:
    itrs_positions: list[PositionVector] = []

    for minute, gcrs_position in enumerate(gcrs_positions):
        current_julian_date = epoch_offset(
            epoch, Second(Scalar(seconds_from_minutes(Minute(minute))))
        )
        itrs_positions.append(
            itrs_position_from_gcrs_position(current_julian_date, gcrs_position)
        )

    return itrs_positions


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


def x_axis_passive_xrotation(angle: Radians) -> TransformationMatrix3D:
    """Passive coordinate-frame rotation about the x-axis."""
    return rotation_matrix_3d(
        make_vector3d(
            Scalar(1),
            Scalar(0),
            Scalar(0),
        ),
        make_vector3d(
            Scalar(0),
            Scalar(math.cos(angle)),
            Scalar(negate(math.sin(angle))),
        ),
        make_vector3d(
            Scalar(0),
            Scalar(math.sin(angle)),
            Scalar(math.cos(angle)),
        ),
    )


def y_axis_passive_rotation(angle: Radians) -> TransformationMatrix3D:
    """Passive coordinate-frame rotation about the y-axis."""
    return rotation_matrix_3d(
        make_vector3d(
            Scalar(math.cos(angle)),
            Scalar(0),
            Scalar(math.sin(angle)),
        ),
        make_vector3d(
            Scalar(0),
            Scalar(1),
            Scalar(0),
        ),
        make_vector3d(
            Scalar(negate(math.sin(angle))),
            Scalar(0),
            Scalar(math.cos(angle)),
        ),
    )


def z_axis_passive_rotation(angle: Radians) -> TransformationMatrix3D:
    return rotation_matrix_3d(
        make_vector3d(
            Scalar(math.cos(angle)),
            Scalar(negate(math.sin(angle))),
            Scalar(0),
        ),
        make_vector3d(
            Scalar(math.sin(angle)),
            Scalar(math.cos(angle)),
            Scalar(0),
        ),
        make_vector3d(
            Scalar(0),
            Scalar(0),
            Scalar(1),
        ),
    )


def x_axis_active_rotation(angle: Radians) -> TransformationMatrix3D:
    return rotation_matrix_3d(
        make_vector3d(Scalar(1), Scalar(0), Scalar(0)),
        make_vector3d(Scalar(0), Scalar(math.cos(angle)), Scalar(math.sin(angle))),
        make_vector3d(
            Scalar(0), Scalar(negate(math.sin(angle))), Scalar(math.cos(angle))
        ),
    )


def y_axis_active_rotation(angle: Radians) -> TransformationMatrix3D:
    return rotation_matrix_3d(
        make_vector3d(
            Scalar(math.cos(angle)), Scalar(0), Scalar(negate(math.sin(angle)))
        ),
        make_vector3d(Scalar(0), Scalar(1), Scalar(0)),
        make_vector3d(Scalar(math.sin(angle)), Scalar(0), Scalar(math.cos(angle))),
    )


def z_axis_active_rotation(angle: Radians) -> TransformationMatrix3D:
    return rotation_matrix_3d(
        make_vector3d(Scalar(math.cos(angle)), Scalar(math.sin(angle)), Scalar(0)),
        make_vector3d(
            Scalar(negate(math.sin(angle))), Scalar(math.cos(angle)), Scalar(0)
        ),
        make_vector3d(Scalar(0), Scalar(0), Scalar(1)),
    )


# endregion
