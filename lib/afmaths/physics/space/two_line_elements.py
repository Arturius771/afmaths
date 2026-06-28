from astronomy_types import (
    Coordinate3D,
    Day,
    Distance,
    MeanMotion,
    PositionVector,
    Scalar,
)

from afmaths.operation import divide_by
from afmaths.physics.space.type_conversion_helpers import make_vector3d
from afmaths.tensors import vector_magnitude, vector_subtract


def orbital_period_mean_motion(n_per_day: MeanMotion) -> Day:
    return divide_by(n_per_day)(1)


def distance_to_satellite(
    itrs_position: PositionVector, observer: Coordinate3D
) -> Distance:
    return Distance(
        Scalar(
            vector_magnitude(
                vector_subtract(
                    itrs_position, make_vector3d(observer.x, observer.y, observer.z)
                )
            )
        )
    )
