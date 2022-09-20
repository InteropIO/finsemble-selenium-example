import time
from typing import Callable


def wait_until(predicate: Callable, timeout_in_seconds: int, *args, **kwargs):
    """
    Repeatedly call and wait for the specified callable predicate to return a "truth-y" value.

    :param predicate: A callable method or function that you wish to wait on. This method will be called repeatedly.
                      If the result resolves to a "false-y" value, then the method will continue to be called.
                      If the result resolves to a "truth-y" value, then the result of the predicate will be
                      immediately returned.
    :type predicate: Callable

    :param timeout_in_seconds: The maximum time, in seconds, to wait for the specified predicate to eventually
                               return a "truth-y" value.
    :type timeout_in_seconds: int

    :param args: Arbitrary non-keyworded args to pass into the callable predicate when it is invoked.

    :param kwargs: Arbitrary keyworded args to pass into the callable predicate when it is invoked.

    :return: The return value of the given callable predicate once it resolves to a "truth-y" value.

    :raises TimeoutError: If the given callable predicate does not resolve to a "truth-y" value before the given
                          timeout elapses.
    """

    # Invoke the method once first before starting any countdown, to guarantee that we can call the method at
    # least twice before timing out with an error.
    # (Handle cases in which the duration to execute the given predicate is longer than the allotted timeout.)
    result = predicate(*args, **kwargs)
    if bool(result):
        return result

    # Begin to repeatedly invoke the predicate within a countdown.
    end_time = time.time() + timeout_in_seconds
    while time.time() < end_time:
        result = predicate(*args, **kwargs)
        if bool(result):
            return result
        else:
            time.sleep(0.25)
    raise TimeoutError()
