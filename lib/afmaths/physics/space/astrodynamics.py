from typing import NewType

from astronomy_types import Distance, GravitationalParameter, Scalar, Velocity

from afmaths.geometry import semi_major_axis_from_axes
from afmaths.operation import add
from afmaths.physics.space.celestial_mechanics import (
    EARTH_MU_KM_CUBED,
    EARTH_RADIUS_KM,
    orbit_radius,
    velocity_difference,
    velocity_for_altitude,
    vis_viva,
)

DeltaV = NewType("DeltaV", Velocity)


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

    semi_major_axis_transfer_ellipse = semi_major_axis_from_axes(r_a, r_b)
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


if __name__ == "main":

    # (0.37539955175032447, 0.19003921507073027, 0.18536033667959417)
    print(hohmann_transfer(Distance(Scalar(300)), Distance(Scalar(1000))))
