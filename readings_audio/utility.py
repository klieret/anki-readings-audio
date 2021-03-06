#!/usr/bin/env python
# -*- coding: utf-8 -*-

# todo: signal will not work under windows
import signal


def remove_intersection(list_a, list_b):
    """ Returns a (new) list that contains all items from list_b except for
    the ones already included in list_a. Preserves ordering.
    :param list_a
    :param list_b
    :return subset of list_b
    """
    return [item for item in list_b if not item in list_a]


def remove_duplicates(seq):
    """Returns a list that equals $seq except that there are no duplicates.
    Preserves ordering.
    :param seq: A sequence
    :return: new sequence with no duplicates
    """
    # from stackoverflow:
    # http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
    seen = set()
    seen_add = seen.add  # don't remove, faster!
    return [x for x in seq if not (x in seen or seen_add(x))]


class TimeoutError(Exception):
    pass


def timeout_wrap(func, args=None, kwargs=None, timeout=10):
    """Runs a function normally. If however the execution time exceeds
    timeout, an exception is raised instead.
    :param func: Function to run
    :param args: positional arguments for the function
    :param kwargs: keyword arguments for the function
    :param timeout: timeout time in seconds
    :return:The return Value of the function.
    """
    if not args:
        args = []
    if not kwargs:
        kwargs = {}

    def handler(signum, frame):
        raise TimeoutError

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        ret = func(*args, **kwargs)
    except TimeoutError:
        raise RuntimeError
    else:
        # deactivate alarm
        signal.alarm(0)
        return ret


if __name__ == "__main__":
    # testing timeout function

    import time

    def test_successfull():
        time.sleep(1)

    def test_unsuccessfull():
        time.sleep(5)

    timeout_wrap(test_successfull, timeout=3)
    timeout_wrap(test_unsuccessfull, timeout=3)