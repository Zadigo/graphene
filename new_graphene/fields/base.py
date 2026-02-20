from functools import total_ordering
from typing import Any, Optional

MAX_INT = 2147483647

MIN_INT = -2147483648


def source_resolver(source: str, root, info, **args):
    pass


@total_ordering
class BaseField:
    creation_counter = 1

    def __init__(self, *args, counter: Optional[int] = None, **kwargs):
        self.creation_counter = counter or self.increase_counter()
        self.args = args
        self.kwargs = kwargs

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

    def _get_type(self):  # Rename: get_field_type
        raise NotImplementedError

    def increase_counter(self):
        self.creation_counter += 1
        return self.creation_counter

    def reset_counter(self):
        self.creation_counter = self.increase_counter()
