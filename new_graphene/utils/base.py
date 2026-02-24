import enum
from typing import Callable


def get_unbound_function(func: Callable | None) -> Callable | None:
    if func is None:
        return None

    if not getattr(func, '__self__', True):
        return func.__func__

    return func


class ObjectTypesEnum(enum.Enum):
    """Enum for different GraphQL type categories."""

    FIELD = 'Field'
    ARGUMENT = 'Argument'
    OBJECT_TYPE = 'ObjectType'
    INTERFACE = 'Interface'
    UNION = 'Union'
    SCALAR = 'Scalar'
    NOT_DEFINED = 'NotDefined'
