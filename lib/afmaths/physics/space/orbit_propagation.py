from dataclasses import replace
import math

from astronomy_types import (
    Anomaly,
    ArgumentOfPerigee,
    Coordinate2D,
    Degrees,
    Distance,
    EccentricAnomaly,
    Inclination,
    MeanAnomaly,
    MeanMotion,
    OrbitalElements,
    Radians,
    Ratio,
    RightAscension,
    StateVectors,
    Vector2D,
    Scalar,
    PositionVector,
    Vector3D,
    Position,
    TrueAnomaly,
    Eccentricity,
    SemiMajorAxis,
    GravitationalParameter,
    Velocity,
    VelocityVector,
    Second,
)

from afmaths.constants import (
    EARTH_MU_KM_CUBED,
    EXAMPLE_ELEMENTS,
    EarthCentredInertial,
    RotationMatrix,
)
from afmaths.geometry import (
    ellipse_perimeter_coordinate_from_eccentric_anomaly,
    semi_minor_axis,
)
from afmaths.operation import (
    SQUARE,
    add,
    divide_by,
    interval,
    multiply,
    square_root,
    subtract,
)
from afmaths.physics.space.astronomy.coordinate_conversion import (
    orthonormal_frame_transform,
    vector_from_direction,
)
from afmaths.physics.space.astronomy.type_conversion_helpers import (
    degrees_to_radians,
    position_vector_to_vector3d,
    velocity_vector_to_vector3d,
)
from afmaths.physics.space.celestial_mechanics import (
    eccentric_anomaly_from_true_anomaly,
    eccentric_anomaly_solved,
    kepler_equation,
    mean_anomaly_at_time,
    mean_motion,
    newtons_method,
    orbit_equation,
    orbital_elements_from_state_vectors,
    true_anomaly,
)
from afmaths.tensors import rotation_matrix, vector_multiplication_2d


def generate_angles_on_circle(resolution: int) -> list[Radians]:
    typed = []
    for val in interval(0, 2 * math.pi, resolution):
        typed.append(Radians(Scalar(val)))

    return typed


def perifocal_position_2d(
    orbital_elements: OrbitalElements,
) -> Vector2D[Scalar]:

    return vector_multiplication_2d(
        Vector2D(
            x=Scalar(math.cos(orbital_elements.true_anomaly)),
            y=Scalar(math.sin(orbital_elements.true_anomaly)),
        ),
        orbit_equation(
            orbital_elements.semi_major_axis,
            orbital_elements.eccentricity,
            orbital_elements.true_anomaly,
        ),
    )


def perifocal_position_3d(
    orbital_elements: OrbitalElements,
) -> PositionVector:
    """Calculates the position vector in the perifocal coordinate system"""

    vector = vector_from_direction(
        Vector3D(
            x=Scalar(math.cos(orbital_elements.true_anomaly)),
            y=Scalar(math.sin(orbital_elements.true_anomaly)),
            z=Scalar(0),
        ),
        orbit_equation(
            orbital_elements.semi_major_axis,
            orbital_elements.eccentricity,
            orbital_elements.true_anomaly,
        ),
    )
    return PositionVector(Position(vector.x), Position(vector.y), Position(vector.z))


def perifocal_velocity_3d(
    true_anomaly: TrueAnomaly,
    eccentricity: Eccentricity,
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter,
) -> VelocityVector:
    """Calculates the velocity vector in the perifocal coordinate system"""
    vector = vector_from_direction(
        Vector3D(
            Scalar(-math.sin(true_anomaly)),
            Scalar(add(eccentricity)(math.cos(true_anomaly))),
            Scalar(0),
        ),
        Scalar(
            square_root(
                divide_by(multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1)))(
                    gravitational_parameter
                )
            )
        ),
    )

    return VelocityVector(Velocity(vector.x), Velocity(vector.y), Velocity(vector.z))


def orbit_state_vector_prediction_from_orbital_elements(
    orbital_elements: OrbitalElements,
    time_offset_s: Second = Second(Scalar(0)),
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> StateVectors:
    """Calculates the state vectors (position and velocity) of an orbit from the orbital elements at a given time offset from the current position in the orbit"""

    initial_mean_anomaly = kepler_equation(
        eccentric_anomaly_from_true_anomaly(
            orbital_elements.true_anomaly, orbital_elements.eccentricity
        ),
        orbital_elements.eccentricity,
    )

    true_anomaly_at_offset = true_anomaly_at_time(
        orbital_elements.eccentricity,
        initial_mean_anomaly,
        time_offset_s,
        mean_motion(orbital_elements.semi_major_axis, gravitational_parameter),
    )

    perifocal_position_gaussian = perifocal_position_3d(
        replace(orbital_elements, true_anomaly=true_anomaly_at_offset)
    )

    perifocal_velocity_gaussian = perifocal_velocity_3d(
        true_anomaly_at_offset,
        orbital_elements.eccentricity,
        orbital_elements.semi_major_axis,
        gravitational_parameter,
    )

    eci_rotation_matrix = perifocal_to_inertial_frame_rotation_matrix(orbital_elements)

    position_vector = transform_perifocal_to_inertial(
        eci_rotation_matrix,
        position_vector_to_vector3d(perifocal_position_gaussian),
    )

    velocity_vector = transform_perifocal_to_inertial(
        eci_rotation_matrix, velocity_vector_to_vector3d(perifocal_velocity_gaussian)
    )

    return StateVectors(
        PositionVector(
            Position(position_vector.x),
            Position(position_vector.y),
            Position(position_vector.z),
        ),
        VelocityVector(
            Velocity(velocity_vector.x),
            Velocity(velocity_vector.y),
            Velocity(velocity_vector.z),
        ),
    )


def generate_all_orbit_positions(
    orbital_elements: OrbitalElements,
    resolution: int,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> list[PositionVector]:
    if resolution < 5:
        raise ValueError("Resolution must be greater than 5.")
    position_list = []
    for true_anomaly in generate_angles_on_circle(resolution):
        position_list.append(
            orbit_state_vector_prediction_from_orbital_elements(
                replace(
                    orbital_elements,
                    true_anomaly=true_anomaly,
                ),
                gravitational_parameter=gravitational_parameter,
            ).position
        )
    return position_list


def propagate_orbit_2d(
    orbital_elements: OrbitalElements,
    target_time: Second,
) -> Coordinate2D:

    M = mean_anomaly_at_time(
        kepler_equation(
            eccentric_anomaly_from_true_anomaly(
                TrueAnomaly(Anomaly(Radians(Scalar(0)))), orbital_elements.eccentricity
            ),
            orbital_elements.eccentricity,
        ),
        target_time,
        mean_motion(
            orbital_elements.semi_major_axis,
        ),
    )

    E, _ = eccentric_anomaly_solved(newtons_method, orbital_elements.eccentricity, M)

    return ellipse_perimeter_coordinate_from_eccentric_anomaly(
        orbital_elements.semi_major_axis,
        semi_minor_axis(
            orbital_elements.semi_major_axis,
            orbital_elements.eccentricity,
        ),
        E,
    )


def true_anomaly_at_time(
    eccentricity: Eccentricity,
    mean_anomaly: MeanAnomaly,
    time: Second,
    mean_motion: MeanMotion,
) -> TrueAnomaly:
    return true_anomaly(
        eccentricity,
        mean_anomaly_at_time(mean_anomaly, time, mean_motion),
    )


def eccentric_anomaly_at_time(
    orbital_elements: OrbitalElements,
    time_seconds: Second,
    g: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> EccentricAnomaly:

    initial_mean_anomaly = kepler_equation(
        eccentric_anomaly_from_true_anomaly(
            orbital_elements.true_anomaly, orbital_elements.eccentricity
        ),
        orbital_elements.eccentricity,
    )

    return eccentric_anomaly_from_true_anomaly(
        true_anomaly_at_time(
            orbital_elements.eccentricity,
            initial_mean_anomaly,
            time_seconds,
            mean_motion(orbital_elements.semi_major_axis, g),
        ),
        orbital_elements.eccentricity,
    )


def transform_perifocal_to_inertial(
    perifocal_to_eci_rotation_matrix: RotationMatrix,
    perifocal_vector: Vector3D[Scalar],
) -> EarthCentredInertial:
    """Transforms a vector from the perifocal coordinate system to the ECI coordinate system using the provided transformation matrix"""
    # TODO: reuse
    return EarthCentredInertial(
        orthonormal_frame_transform(perifocal_to_eci_rotation_matrix, perifocal_vector)
    )


def perifocal_to_inertial_frame_rotation_matrix(
    orbital_elements: OrbitalElements,
) -> RotationMatrix:
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

    return rotation_matrix(
        Vector3D(Scalar(p[0]), Scalar(p[1]), Scalar(p[2])),
        Vector3D(Scalar(q[0]), Scalar(q[1]), Scalar(q[2])),
        Vector3D(Scalar(w[0]), Scalar(w[1]), Scalar(w[2])),
    )


if __name__ == "__main__":
    # {'position_vector': [-1753.131769017119, 1070.9950241554125, -6564.0676605044755], 'velocity_vector': [-3.478980009547892, 6.473396036204375, 1.986162313733967]}
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPerigee(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1800)),
        )
    )

    # StateVectors(position=Vector3D(x=10000.000000000027, y=39999.999999999985, z=-5000.0), velocity=Vector3D(x=-1.4999999999999996, y=1.0000000000000016, z=-0.1000000000000002))
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            orbital_elements_from_state_vectors(
                StateVectors(
                    PositionVector(
                        Position(Scalar(10000)),
                        Position(Scalar(40000)),
                        Position(Scalar(-5000)),
                    ),
                    VelocityVector(
                        Velocity(Scalar(-1.5)),
                        Velocity(Scalar(1)),
                        Velocity(Scalar(-0.1)),
                    ),
                )
            )
        )
    )

    print(
        propagate_orbit_2d(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPerigee(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1000)),
        )
    )

    print(perifocal_position_2d(EXAMPLE_ELEMENTS))
