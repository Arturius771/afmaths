from afmaths.operation import (
    divide_by,
    exponentiate,
    ratio,
    ratio_to_percentage,
)
from astronomy_types import Ratio


def probability_of_outcome_percentage(
    number_of_flips: int, chance_per_flip_ratio: Ratio
) -> float:
    return divide_by(
        exponentiate(number_of_flips)(
            ratio(100)(ratio_to_percentage(chance_per_flip_ratio))
        )
    )(1)
