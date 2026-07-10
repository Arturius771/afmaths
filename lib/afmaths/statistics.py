from afmaths.operation import (
    divide_by,
    exponentiate,
    ratio,
    percentage_from_ratio,
)
from astronomy_types import Ratio


def probability_of_outcome_percentage(
    number_of_flips: int, chance_per_flip_ratio: Ratio
) -> float:
    return divide_by(
        exponentiate(number_of_flips)(
            ratio(100)(percentage_from_ratio(chance_per_flip_ratio))
        )
    )(1)
