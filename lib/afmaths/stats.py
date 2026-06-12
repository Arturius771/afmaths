from afmaths.operation import divide_by, exponentiate, multiply


def probability_of_outcome_percentage(
    number_of_flips: int, chance_per_flip: float
) -> float:
    return divide_by(
        exponentiate(number_of_flips)(divide_by(multiply(100)(chance_per_flip))(100))
    )(1)


if __name__ == "__main__":
    print(probability_of_outcome_percentage(1000, 0.5))
