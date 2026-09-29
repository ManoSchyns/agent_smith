import time


def current_milli_time() -> float:
    """
    Returns the current time in milliseconds

    Return:
        float: The time in milliseconds
    """
    return round(time.time() * 1000)
