import math
import statistics
from afmaths.operation import add, divide_by, subtract, summation


def list_sort(number_list: list[float]) -> list[float]:
    return sorted(number_list)


def list_length(number_list: list[float]) -> int:
    return len(number_list)


def list_sum(number_list: list[float]) -> float:
    def value_at_index(i: int) -> float:
        return number_list[i]

    return summation(value_at_index, 0, list_length(number_list) - 1)


def list_min(number_list: list[float]) -> float:
    return min(number_list)


def list_max(number_list: list[float]) -> float:
    return max(number_list)


def list_range(number_list: list[float]) -> float:
    return subtract(list_min(number_list))(list_max(number_list))


def list_mean(number_list: list[float]) -> float:
    return divide_by(list_length(number_list))(list_sum(number_list))


def list_median(number_list: list[float]) -> float:
    return statistics.median(number_list)


def quartiles(number_list: list[float]) -> tuple[float, float, float]:
    """Calculates the quartiles of a list of numbers"""
    number_list = sorted(number_list)
    q1_index = int(math.ceil(list_length(number_list) * 0.25))
    q1_result = number_list[q1_index - 1]
    number_list[0 : list_length(number_list) // 2]
    q3_result = list_median(number_list)
    iqr_result = subtract(q1_result)(q3_result)

    return q1_result, q3_result, iqr_result


def dataplotter(number_list: list[float]) -> tuple:
    ##MU123
    """
    Runs some useful functions on a provided list
    """
    return (
        list_sort(number_list),
        list_length(number_list),
        list_sum(number_list),
        list_min(number_list),
        list_max(number_list),
        list_range(number_list),
        list_mean(number_list),
        list_median(number_list),
        quartiles(number_list),
    )


# TODO: make function which returns entries of a list according to multiples of an index value
# def get_
# Source - https://stackoverflow.com/q/18272160
# Retrieved 2026-07-13, License - CC BY-SA 3.0

# a = [-2, 1, 5, 3, 8, 5, 6]
# b = [1, 2, 5]
# return [gcrs_positions[i] for i in b]
