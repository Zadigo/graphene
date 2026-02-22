from typing import Callable


def get_unbound_function(func: Callable) -> Callable:
    if not getattr(func, '__self__', True):
        return func.__func__
    return func
