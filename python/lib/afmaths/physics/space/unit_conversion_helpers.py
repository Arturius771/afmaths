def metres_from_kilometres(kilometres: float) -> float:
    """Convert kilometres to metres."""
    return kilometres * 1000.0


def kilometres_from_metres(metres: float) -> float:
    """Convert metres to kilometres."""
    return metres / 1000.0


def kilometres_per_second_from_metres_per_second(metres_per_second: float) -> float:
    """Convert metres per second to kilometres per second."""
    return kilometres_from_metres(metres_per_second)


def metres_per_second_from_kilometres_per_second(kilometres_per_second: float) -> float:
    """Convert kilometres per second to metres per second."""
    return metres_from_kilometres(kilometres_per_second)
