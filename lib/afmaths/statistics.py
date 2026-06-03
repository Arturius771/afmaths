from .operation import divide, exponentiate, multiply


def probability_of_outcome_percentage(
    number_of_flips: int, chance_per_flip: float
) -> float:
    return divide(
        exponentiate(number_of_flips)(divide(multiply(100)(chance_per_flip))(100))
    )(1)


# if __name__ == '__main__':
#     print(probability_of_outcome_percentage(1000, .5))
