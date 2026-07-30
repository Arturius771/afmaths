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
from afmaths.geometry.transformations import (
    orthonormal_frame_transform_3d,
    transformation_matrix_from_basis_vectors,
)
from afmaths.operation import DOUBLE, add, multiply, negate
from afmaths.physics.space.astronomy.time_functions import (
    epoch_offset,
    greenwich_mean_sidereal_time_radians_from_julian_date,
    j200_from_julian_Date,
    seconds_from_minutes,
)
from afmaths.physics.space.type_conversion_helpers import make_vector2d, make_vector3d
from afmaths.tensors import vector_magnitude
from afmaths.afmath_types import TransformationMatrix3D


def transform_vector_from_perifocal(
    orbital_elements: OrbitalElements,
    vector_in_perifocal_frame: Vector3D[Scalar],
) -> Vector3D[Scalar]:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    return orthonormal_frame_transform_3d(
        perifocal_to_reference_frame_matrix(orbital_elements),
        vector_in_perifocal_frame,
    )


def geographic_coordinates_from_itrf(
    itrf: PositionVector,
) -> GeographicCoordinates:
    """Converts ITRS cartesian coordinates to geographic Lat/Lon (degrees). Useful for ground track plotting."""
    return GeographicCoordinates(
        Degrees(
            Scalar(
                math.degrees(
                    math.atan2(itrf.z, vector_magnitude(make_vector2d(itrf.x, itrf.y)))
                )
            )
        ),
        Degrees(Scalar(math.degrees(math.atan2(itrf.y, itrf.x)))),
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


def itrf_position_from_gmst_passive(
    gmst: Radians, gcrs_position: PositionVector
) -> PositionVector:
    """Simplified conversion not taking into account any perturbations or time compatibility. Calculated using the passive rotation of the GCRS frame to the ITRF frame."""
    itrf_position = orthonormal_frame_transform_3d(
        z_axis_passive_rotation(gmst),
        make_vector3d(gcrs_position.x, gcrs_position.y, gcrs_position.z),
    )
    return PositionVector(
        Position(itrf_position.x), Position(itrf_position.y), Position(itrf_position.z)
    )


def itrf_position_from_gmst(
    gmst: Radians, gcrs_position: PositionVector
) -> PositionVector:
    """Simplified conversion not taking into account any perturbations or time compatibility. Calculated using the active rotation of the GCRS frame to the ITRF frame."""
    itrf_position = orthonormal_frame_transform_3d(
        z_axis_active_rotation(gmst),
        make_vector3d(gcrs_position.x, gcrs_position.y, gcrs_position.z),
    )
    return PositionVector(
        Position(itrf_position.x), Position(itrf_position.y), Position(itrf_position.z)
    )


def itrf_position_from_gcrs_position(
    jd: JulianDate, gcrs_position: PositionVector
) -> PositionVector:
    """Simplified conversion not taking into account any perturbations or time compatibility. Calculated using the active rotation of the GCRS frame to the ITRF frame."""
    gmst = greenwich_mean_sidereal_time_radians_from_julian_date(jd)
    return itrf_position_from_gmst_passive(gmst, gcrs_position)


def itrf_positions_from_gcrs_position(
    gcrs_positions: list[PositionVector],
    epoch: Epoch,
) -> list[PositionVector]:
    """Converts a list of GCRS positions to ITRF positions, taking into account the epoch offset for each position based on its index in the list."""
    itrf_positions: list[PositionVector] = []

    for minute, gcrs_position in enumerate(gcrs_positions):
        offset_jd = epoch_offset(
            epoch, Second(Scalar(seconds_from_minutes(Minute(minute))))
        )
        itrf_positions.append(
            itrf_position_from_gcrs_position(offset_jd, gcrs_position)
        )

    return itrf_positions


## TODO
# def itrf_position_from_icrf_position(
#     jd_tt: JulianDate,
#     jd_ut1: JulianDate,
#     icrf_position: PositionVector,
#     earth_icrf_position: PositionVector,
#     polar_motion_x: Angle = Angle(Scalar(0)),
#     polar_motion_y: Angle = Angle(Scalar(0)),
# ) -> PositionVector:
#     """Transforms a barycentric ICRF position into an Earth-fixed ITRF position."""

#     geocentric_position = make_vector3d(
#         subtract(earth_icrf_position.x)(icrf_position.x),
#         subtract(earth_icrf_position.y)(icrf_position.y),
#         subtract(earth_icrf_position.z)(icrf_position.z),
#     )

#     precessed_position = orthonormal_frame_transform_3d(
#         precession_matrix(jd_tt),
#         geocentric_position,
#     )

#     nutated_position = orthonormal_frame_transform_3d(
#         nutation_matrix(jd_tt),
#         precessed_position,
#     )

#     earth_rotated_position = orthonormal_frame_transform_3d(
#         earth_rotation_matrix(jd_ut1),
#         nutated_position,
#     )

#     itrf_position = orthonormal_frame_transform_3d(
#         polar_motion_matrix(
#             polar_motion_x,
#             polar_motion_y,
#         ),
#         earth_rotated_position,
#     )

#     return PositionVector(
#         Position(itrf_position.x),
#         Position(itrf_position.y),
#         Position(itrf_position.z),
#     )


# region Transformation Matrices


## TODO: Implement the following transformation matrices:
# def precession_matrix() -> TransformationMatrix3D:
#     """Calculates the precession matrix for a given Julian Date."""
#     # Implementation of precession matrix calculation goes here
#     return transformation_matrix_from_basis_vectors(
#         make_vector3d(Scalar(1), Scalar(0), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(1), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(0), Scalar(1)),
#     )

# def nutation_matrix() -> TransformationMatrix3D:
#     """Calculates the precession matrix for a given Julian Date."""
#     # Implementation of precession matrix calculation goes here
#     return transformation_matrix_from_basis_vectors(
#         make_vector3d(Scalar(1), Scalar(0), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(1), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(0), Scalar(1)),
#     )

## Maybe the same as itrf_position_from_gmst()?
# def earth_rotation_matrix() -> TransformationMatrix3D:
#     """Calculates the precession matrix for a given Julian Date."""
#     # Implementation of precession matrix calculation goes here
#     return transformation_matrix_from_basis_vectors(
#         make_vector3d(Scalar(1), Scalar(0), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(1), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(0), Scalar(1)),
#     )

# def polar_motion_matrix() -> TransformationMatrix3D:
#     """Calculates the precession matrix for a given Julian Date."""
#     # Implementation of precession matrix calculation goes here
#     return transformation_matrix_from_basis_vectors(
#         make_vector3d(Scalar(1), Scalar(0), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(1), Scalar(0)),
#         make_vector3d(Scalar(0), Scalar(0), Scalar(1)),
#     )


def perifocal_to_reference_frame_matrix(
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

    return transformation_matrix_from_basis_vectors(
        make_vector3d(Scalar(p[0]), Scalar(p[1]), Scalar(p[2])),
        make_vector3d(Scalar(q[0]), Scalar(q[1]), Scalar(q[2])),
        make_vector3d(Scalar(w[0]), Scalar(w[1]), Scalar(w[2])),
    )


def x_axis_passive_xrotation(angle: Radians) -> TransformationMatrix3D:
    """Passive coordinate-frame rotation about the x-axis."""
    return transformation_matrix_from_basis_vectors(
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
    return transformation_matrix_from_basis_vectors(
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
    return transformation_matrix_from_basis_vectors(
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
    return transformation_matrix_from_basis_vectors(
        make_vector3d(Scalar(1), Scalar(0), Scalar(0)),
        make_vector3d(Scalar(0), Scalar(math.cos(angle)), Scalar(math.sin(angle))),
        make_vector3d(
            Scalar(0), Scalar(negate(math.sin(angle))), Scalar(math.cos(angle))
        ),
    )


def y_axis_active_rotation(angle: Radians) -> TransformationMatrix3D:
    return transformation_matrix_from_basis_vectors(
        make_vector3d(
            Scalar(math.cos(angle)), Scalar(0), Scalar(negate(math.sin(angle)))
        ),
        make_vector3d(Scalar(0), Scalar(1), Scalar(0)),
        make_vector3d(Scalar(math.sin(angle)), Scalar(0), Scalar(math.cos(angle))),
    )


def z_axis_active_rotation(angle: Radians) -> TransformationMatrix3D:
    return transformation_matrix_from_basis_vectors(
        make_vector3d(Scalar(math.cos(angle)), Scalar(math.sin(angle)), Scalar(0)),
        make_vector3d(
            Scalar(negate(math.sin(angle))), Scalar(math.cos(angle)), Scalar(0)
        ),
        make_vector3d(Scalar(0), Scalar(0), Scalar(1)),
    )


# endregion
