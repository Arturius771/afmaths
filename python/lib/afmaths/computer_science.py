import math

from afmaths.geometry.geometry import pythagoras_theorem

from .list import list_sum
from .operation import (
    HALF,
    add,
    divide_by,
    exponentiate,
    factorial,
    multiply,
    subtract,
)


def file_compression_ratio(uncompressed_size: float):
    """Calculates the file compression ratio given the uncompressed size and compressed size."""
    return lambda compressed_size: divide_by(compressed_size)(uncompressed_size)


def compressed_file_size(uncompressed_size):
    """Calculates the compressed file size given the uncompressed size and compression ratio."""
    return lambda compression_ratio: divide_by(compression_ratio)(uncompressed_size)


def diagonal_pixel_length(length_in_pixels):
    """Calculates the diagonal pixel length of a screen given its length and width in pixels."""
    return lambda width_in_pixels: math.floor(
        pythagoras_theorem(length_in_pixels)(width_in_pixels)
    )


def travelling_salesman_problem_total_routes(number_of_cities) -> float:
    """Calculates the total number of possible routes for the travelling salesman problem given the number of cities."""
    ##(n - 1)!/2
    total_routes = HALF(factorial(subtract(1)(number_of_cities)))

    return total_routes


def check_drive_clusters(
    sectors_per_cluster, sector_size_bytes, physical_file_size_bytes
) -> tuple[int, float]:
    """Calculates the number of clusters and slack space for a given physical file size, sector size, and sectors per cluster."""
    ## TM255
    if (
        physical_file_size_bytes % (multiply(sectors_per_cluster)(sector_size_bytes))
        == 0
    ):
        number_of_clusters = physical_file_size_bytes // multiply(sectors_per_cluster)(
            sector_size_bytes
        )
    else:
        number_of_clusters = (
            physical_file_size_bytes // (sectors_per_cluster * sector_size_bytes)
        ) + 1

    multiply_number_of_clusters = multiply(number_of_clusters)
    multiply_number_of_clusters_by_sectors_per_cluster = multiply(
        multiply_number_of_clusters(sectors_per_cluster)
    )
    slack_space_bytes = subtract(physical_file_size_bytes)(
        multiply_number_of_clusters_by_sectors_per_cluster(sector_size_bytes)
    )

    return (number_of_clusters, slack_space_bytes)


def ml_f1_score(precision: float, recall: float) -> float:
    """F1 score: related to the harmonic mean of precision and recall. Calculated as F1 = 2/[(1/Precision) + (1/Recall)] = 2/[(TP + FP)/TP + (TP + FN)/TP] = 2/[(2TP + FP + FN)/TP] = 2TP/[2TP + FP + FN] . A high F1 score implies the system has low numbers of false positives and false negatives. - TM358"""
    f1 = divide_by(add(divide_by(precision)(1))(divide_by(recall)(1)))(2)

    return f1


def ml_precesion(true_positives):
    """Calculates the precision given the number of true positives and false positives."""
    return lambda false_positives: divide_by(add(true_positives)(false_positives))(
        true_positives
    )


def ml_recall(true_positives):
    """Fraction of total positives out of both true and false positives - also known as the true positive rate."""
    return lambda false_negatives: divide_by(add(true_positives)(false_negatives))(
        true_positives
    )  # TM358


def ml_false_positive_rate(false_positives):
    """Calculates the false positive rate given the number of false positives and true negatives."""
    return lambda true_negatives: divide_by(add(false_positives)(true_negatives))(
        false_positives
    )


def ml_weighted_inputs(inputs: list[float], weights: list[float]) -> list[float] | None:
    """Multiply the inputs by the weights - TM358 Block 1"""
    weighted_inputs = []
    if len(inputs) != len(weights):
        return None
    for index, x in enumerate(inputs):
        weighted_inputs.append(multiply(x)(weights[index]))

    return weighted_inputs


def ml_perceptron(inputs: list[float], weights: list[float], bias: float = 0) -> float:
    """Implements a simple perceptron model with given inputs, weights, and an optional bias."""
    x = ml_weighted_inputs(inputs, weights)
    if x == None:
        return 0  # TODO: this is dangerous
    return ml_activation_function(add(list_sum(x))(bias))


def ml_activation_function(input: float, threshold: float = 0):
    """Implements a simple threshold activation function for a perceptron."""
    if input > threshold:
        return 1
    else:
        return 0


def ascii_text_from_byte(input: int) -> str:
    """Converts an 8-bit binary value to its corresponding ASCII character."""
    # https://www.rapidtables.com/convert/number/binary-to-ascii.html

    return chr(decimal_from_byte(input))


def decimal_from_byte(input: int) -> int:
    """Converts an 8-bit binary value to its decimal representation."""
    value = 0
    tracker = len(str(input)) - 1

    for bit in str(input):
        if int(bit) != 0:
            exponentiateByTracker = exponentiate(tracker)
            value += exponentiateByTracker(2)
        tracker -= 1
    return value


def hex_from_byte(input: int) -> str:
    """Converts an 8-bit binary string to its hexadecimal representation."""
    str_input = str(input)
    length = len(str_input)

    if length == 8:
        return f"{hex_from_bit(str_input[:4])}{hex_from_bit(str_input[4:])}"
    if length == 7:
        return f"{hex_from_bit(str_input[:3])}{hex_from_bit(str_input[3:])}"
    if length == 6:
        return f"{hex_from_bit(str_input[:2])}{hex_from_bit(str_input[2:])}"
    if length == 5:
        return f"{hex_from_bit(str_input[:1])}{hex_from_bit(str_input[1:])}"
    if length <= 4:
        return f"{hex_from_bit(str_input)}"

    return str_input


def hex_from_bit(bit_string: str) -> str:
    """Converts a binary string to its hexadecimal representation."""
    if bit_string == "0":
        return "0"
    if bit_string == "1":
        return "1"
    if bit_string == "10":
        return "2"
    if bit_string == "11":
        return "3"
    if bit_string == "100":
        return "4"
    if bit_string == "101":
        return "5"
    if bit_string == "110":
        return "6"
    if bit_string == "111":
        return "7"
    if bit_string == "1000":
        return "8"
    if bit_string == "1001":
        return "9"
    if bit_string == "1010":
        return "A"
    if bit_string == "1011":
        return "B"
    if bit_string == "1100":
        return "C"
    if bit_string == "1101":
        return "D"
    if bit_string == "1110":
        return "E"
    if bit_string == "1111":
        return "F"

    return bit_string
