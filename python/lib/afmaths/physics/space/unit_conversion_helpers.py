def metres_from_kilometres(kilometres: float) -> float:
    return kilometres * 1000.0


def kilometres_from_metres(metres: float) -> float:
    return metres / 1000.0


def kilometres_per_second_from_metres_per_second(metres_per_second: float) -> float:
    return kilometres_from_metres(metres_per_second)


def metres_per_second_from_kilometres_per_second(kilometres_per_second: float) -> float:
    return metres_from_kilometres(kilometres_per_second)
