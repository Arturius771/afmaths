import math

from astronomy_types import (
    Distance,
    EquatorialCoordinates,
    GravitationalParameter,
    OrbitalElements,
    Position,
    PositionVector,
    Radians,
    Scalar,
    StateVectors,
    Vector3D,
    Velocity,
    VelocityVector,
)

from afmaths.constants import EARTH_MU_KM_CUBED, EARTH_RADIUS_KM, DeltaV
from afmaths.geometry import semi_major_axis_from_vertex_distances
from afmaths.operation import add, divide_by, multiply, negate
from afmaths.physics.space.astronomy.coordinate_conversion import (
    nadir_vector,
    zenith_vector,
)
from afmaths.physics.space.celestial_mechanics import (
    angular_momentum,
    orbit_radius,
    orbital_elements_from_state_vectors,
    periapsis,
    velocity_difference,
    velocity_for_altitude,
    vis_viva,
)
from afmaths.tensors import (
    dot_product_3d,
    vector_magnitude,
    vector_negate,
    vector_normalise,
)


def radial(position: PositionVector) -> Vector3D:
    return zenith_vector(position)


def anti_radial(position: PositionVector) -> Vector3D:
    return nadir_vector(position)


def prograde(velocity: VelocityVector) -> Vector3D:
    return vector_normalise(velocity)


def retrograde(velocity: VelocityVector) -> Vector3D:
    return vector_negate(prograde(velocity))


def normal(state: StateVectors) -> Vector3D:
    return vector_normalise(angular_momentum(state))


def anti_normal(state: StateVectors) -> Vector3D:
    return vector_negate(normal(state))


def flight_path_angle(
    state: StateVectors, mu: GravitationalParameter = EARTH_MU_KM_CUBED
) -> Radians:
    elements = orbital_elements_from_state_vectors(state)
    r_p = periapsis(elements.semi_major_axis, elements.eccentricity)
    velocity_at_periapsis = vis_viva(mu, r_p, elements.semi_major_axis)

    return Radians(
        Scalar(
            math.acos(
                divide_by(
                    multiply(
                        vector_magnitude(
                            Vector3D(
                                state.position.x, state.position.y, state.position.z
                            )
                        )
                    )(
                        vector_magnitude(
                            Vector3D(
                                state.velocity.x, state.velocity.y, state.velocity.z
                            )
                        )
                    )
                )(multiply(r_p)(velocity_at_periapsis))
            )
        )
    )


def signed_flight_path_angle(state: StateVectors) -> Radians:
    r = vector_magnitude(Vector3D(state.position.x, state.position.y, state.position.z))
    v = vector_magnitude(Vector3D(state.velocity.x, state.velocity.y, state.velocity.z))

    return Radians(
        Scalar(
            math.asin(
                divide_by(multiply(r)(v))(
                    dot_product_3d(
                        Vector3D(
                            state.position.x,
                            state.position.y,
                            state.position.z,
                        ),
                        Vector3D(state.velocity.x, state.velocity.y, state.velocity.z),
                    )
                )
            )
        )
    )


def hohmann_transfer(
    initial_altitude_km: Distance,
    target_altitude_km: Distance,
    initial_body_radius: Distance = EARTH_RADIUS_KM,
    gravitational_parameter: GravitationalParameter = EARTH_MU_KM_CUBED,
) -> tuple[DeltaV, Velocity, Velocity]:
    """Calculates the delta-v required for a Hohmann transfer"""
    # www.braeunig.us/space/problem.htm#4.19

    r_a = orbit_radius(initial_altitude_km, initial_body_radius)
    r_b = orbit_radius(target_altitude_km, initial_body_radius)

    semi_major_axis_transfer_ellipse = semi_major_axis_from_vertex_distances(r_a, r_b)
    initial_velocity = velocity_for_altitude(r_a, gravitational_parameter)
    final_velocity = velocity_for_altitude(r_b, gravitational_parameter)
    velocity_on_orbit_at_initial_orbit = vis_viva(
        gravitational_parameter, r_a, semi_major_axis_transfer_ellipse
    )
    velocity_on_orbit_at_final_orbit = vis_viva(
        gravitational_parameter, r_b, semi_major_axis_transfer_ellipse
    )
    initial_velocity_change = velocity_difference(
        initial_velocity, Velocity(Scalar(velocity_on_orbit_at_initial_orbit))
    )
    final_velocity_change = velocity_difference(
        velocity_on_orbit_at_final_orbit, final_velocity
    )
    delta_v = DeltaV(add(initial_velocity_change)(final_velocity_change))
    return (delta_v, initial_velocity_change, final_velocity_change)


def angle_above_orbital_plane(
    target_object: EquatorialCoordinates,
    orbit: OrbitalElements,
) -> Radians:
    value = math.cos(target_object.declination) * math.sin(
        orbit.inclination
    ) * math.sin(
        orbit.right_ascension_of_ascending_node - target_object.right_ascension
    ) + math.sin(
        target_object.declination
    ) * math.cos(
        orbit.inclination
    )

    # Prevent floating point drift errors at values close to +/-1.
    value = max(-1.0, min(1.0, value))

    return Radians(Scalar(math.asin(value)))


if __name__ == "__main__":

    # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)
    print(hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000))))

    position = PositionVector(
        Position(Scalar(7000)), Position(Scalar(0.1)), Position(Scalar(0.1))
    )

    velocity = VelocityVector(
        Velocity(Scalar(0.1)), Velocity(Scalar(7.5)), Velocity(Scalar(0.1))
    )

    print(f"Radial      : {radial(position)}")
    print(f"Anti-radial : {anti_radial(position)}")
    print(f"Zenith      : {zenith_vector(position)}")
    print(f"Nadir       : {nadir_vector(position)}")
    print(f"Prograde    : {prograde(velocity)}")
    print(f"Retrograde  : {retrograde(velocity)}")
    print(f"Normal      : {normal(StateVectors(position, velocity))}")
    print(f"Anti-normal : {anti_normal(StateVectors(position, velocity))}")
    print(
        f"Flight path angle (deg): {math.degrees(flight_path_angle(StateVectors(position, velocity)))}"
    )
    print(
        f"Flight path angle (deg): {math.degrees(signed_flight_path_angle(StateVectors(position, velocity)))}"
    )
