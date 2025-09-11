from operation import divide, exponentiate, multiply

def probability_of_outcome_percentage(number_of_flips: int, chance_of_result: float) -> float: 
    denominator = divide(multiply(100)(chance_of_result))(100)
    return divide(exponentiate(number_of_flips)(denominator))(1)

# if __name__ == '__main__':
#     print(probability_of_outcome_percentage(1000, .5))