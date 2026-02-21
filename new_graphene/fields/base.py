from functools import total_ordering
from typing import Any, Optional, Type

MAX_INT = 2147483647

MIN_INT = -2147483648


def source_resolver(source: str, root, info, **arguments):
    pass


@total_ordering
class BaseField:
    """BaseField is the base class for all field types in the Graphene library. It is a container
    that saves information about the field, such as its type, resolver, and other configuration options.

    It provides common functionality and attributes that are shared across different field types, 
    such as ObjectType fields, ScalarType fields, Enum fields, Interface fields, and Union fields. 
    This class is not intended to be used directly, but is inherited by other types and streamlines
    their use in different contexts."""

    creation_counter: int = 1

    def __init__(self, *args, counter: Optional[int] = None, **kwargs):
        self.creation_counter = counter or self.increase_counter()
        self.args = args
        self.kwargs = kwargs

    def __repr__(self) -> str:
        name = self.__class__.__name__
        return f"<{name}(args={self.args}, kwargs={self.kwargs})>"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseField):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, BaseField):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, BaseField):
            return self.creation_counter > other.creation_counter
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.creation_counter)

    def _get_type(self) -> Type:  # Rename: get_field_type
        raise NotImplementedError

    def increase_counter(self) -> int:
        self.creation_counter += 1
        return self.creation_counter

    def reset_counter(self):
        self.creation_counter = self.increase_counter()
