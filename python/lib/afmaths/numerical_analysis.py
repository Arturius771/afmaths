from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def root_solver(
    iteration_function: Callable[[T], T],
    initial_guess: T,
    difference_function: Callable[[T, T], float],
    tolerance: float = 1e-6,
    max_iterations: int = 100,
) -> tuple[T, list[tuple[int, T, float | None]]]:
    """Iteratively solve until successive guesses converge."""

    history: list[tuple[int, T, float | None]] = []

    x_i = initial_guess
    delta_x = float("inf")

    iteration = 0
    history.append((iteration, x_i, None))

    while iteration < max_iterations and abs(delta_x) > tolerance:
        x_next = iteration_function(x_i)

        delta_x = difference_function(x_next, x_i)

        iteration += 1
        history.append((iteration, x_next, delta_x))

        x_i = x_next

    return x_i, history
