from dataclasses import replace
import math

from astronomy_types import (
    Anomaly,
    ArgumentOfPeriapsis,
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
)
from afmaths.geometry.geometry import (
    semi_minor_axis,
)
from afmaths.geometry.transformations import (
    ellipse_perimeter_coordinate_from_eccentric_anomaly,
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
from afmaths.physics.space.transformations import (
    perifocal_to_inertial_frame_rotation_matrix,
    transform_perifocal_to_inertial,
)
from afmaths.physics.space.type_conversion_helpers import (
    degrees_to_radians,
    make_position_vector,
    make_true_anomaly,
    position_vector_to_vector3d,
    make_state_vector,
    vector2d,
    vector3d,
    make_velocity_vector,
    velocity_vector_to_vector3d,
)
from afmaths.physics.space.celestial_mechanics import (
    eccentric_anomaly_from_true_anomaly,
    eccentric_anomaly_solved,
    kepler_equation,
    mean_motion,
    newtons_method,
    orbit_equation,
    orbital_elements_from_state_vectors,
    true_anomaly,
)
from afmaths.tensors import (
    vector_multiplication_2d,
    vector_multiplication_3d,
)

# region Helpers


def generate_angles_on_circle(resolution: int) -> list[Radians]:
    typed = []
    for val in interval(0, 2 * math.pi, resolution):
        typed.append(Radians(Scalar(val)))

    return typed


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


def vector_from_direction(
    direction: Vector3D[Scalar],
    magnitude: Scalar,
) -> Vector3D[Scalar]:
    return vector_multiplication_3d(direction, magnitude)


# endregion


# region Propagation logic


def propagate_orbit_2d(
    orbital_elements: OrbitalElements,
    target_time: Second,
) -> Coordinate2D:

    M = mean_anomaly_at_time(
        kepler_equation(
            eccentric_anomaly_from_true_anomaly(
                make_true_anomaly(0), orbital_elements.eccentricity
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


# endregion

# region Instanteneous Properties


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

    return make_state_vector(
        make_position_vector(
            transform_perifocal_to_inertial(
                eci_rotation_matrix,
                position_vector_to_vector3d(perifocal_position_gaussian),
            )
        ),
        make_velocity_vector(
            transform_perifocal_to_inertial(
                eci_rotation_matrix,
                velocity_vector_to_vector3d(perifocal_velocity_gaussian),
            )
        ),
    )


def perifocal_position_2d(
    orbital_elements: OrbitalElements,
) -> Vector2D[Scalar]:

    return vector_multiplication_2d(
        vector2d(
            Scalar(math.cos(orbital_elements.true_anomaly)),
            Scalar(math.sin(orbital_elements.true_anomaly)),
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
    return make_position_vector(
        vector_from_direction(
            vector3d(
                Scalar(math.cos(orbital_elements.true_anomaly)),
                Scalar(math.sin(orbital_elements.true_anomaly)),
                Scalar(0),
            ),
            orbit_equation(
                orbital_elements.semi_major_axis,
                orbital_elements.eccentricity,
                orbital_elements.true_anomaly,
            ),
        )
    )


def perifocal_velocity_3d(
    true_anomaly: TrueAnomaly,
    eccentricity: Eccentricity,
    semi_major_axis: SemiMajorAxis,
    gravitational_parameter: GravitationalParameter,
) -> VelocityVector:
    """Calculates the velocity vector in the perifocal coordinate system"""

    return make_velocity_vector(
        vector_from_direction(
            vector3d(
                Scalar(-math.sin(true_anomaly)),
                Scalar(add(eccentricity)(math.cos(true_anomaly))),
                Scalar(0),
            ),
            Scalar(
                square_root(
                    divide_by(
                        multiply(semi_major_axis)(subtract(SQUARE(eccentricity))(1))
                    )(gravitational_parameter)
                )
            ),
        )
    )


def mean_anomaly_at_time(
    mean_anomaly: MeanAnomaly, time_offset_s: Second, mean_motion: MeanMotion
) -> MeanAnomaly:
    """Calculates the mean anomaly at a given time offset from the current mean motion and mean anomaly"""
    return add(mean_anomaly)(multiply(mean_motion)(time_offset_s))


def orbital_position_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset_s: Second = Second(Scalar(0)),
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> PositionVector:
    return orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements, time_offset_s, gravitational_parameter
    ).position


def orbital_velocity_vector_at_time(
    orbital_elements: OrbitalElements,
    time_offset_s: Second = Second(Scalar(0)),
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> VelocityVector:
    return orbit_state_vector_prediction_from_orbital_elements(
        orbital_elements, time_offset_s, gravitational_parameter
    ).velocity


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


# endregion

if __name__ == "__main__":
    # {'position_vector': [-1753.131769017119, 1070.9950241554125, -6564.0676605044755], 'velocity_vector': [-3.478980009547892, 6.473396036204375, 1.986162313733967]}
    print(
        orbit_state_vector_prediction_from_orbital_elements(
            OrbitalElements(
                Inclination(degrees_to_radians(Degrees(Scalar(98.371)))),
                RightAscension(degrees_to_radians(Degrees(Scalar(120.534)))),
                ArgumentOfPeriapsis(degrees_to_radians(Degrees(Scalar(10.598)))),
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
                ArgumentOfPeriapsis(degrees_to_radians(Degrees(Scalar(10.598)))),
                SemiMajorAxis(Distance(Scalar(6878.1))),
                Eccentricity(Ratio(Scalar(10e-5))),
                TrueAnomaly(Anomaly(Radians(Scalar(2.8022276030554347)))),
            ),
            Second(Scalar(1000)),
        )
    )

    print(perifocal_position_2d(EXAMPLE_ELEMENTS))
