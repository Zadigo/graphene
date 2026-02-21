import functools
import inspect
from functools import total_ordering
from typing import Any, Callable, Optional, Type

from graphql import GraphQLResolveInfo

from graphene.utils.module_loading import import_string
from new_graphene.typings import TypeField


def inspect_type(item: TypeField | Callable[..., Any] | Any):  # get_type
    """Inspect the type of an item and return it. This function is 
    used to resolve the type of a field, argument, or any other item 
    that can be defined using either a string, a callable, 
    or a direct instance."""
    if isinstance(item, str):
        return import_string(item)

    if inspect.isfunction(item) or isinstance(item, functools.partial):
        return item()

    return item


MAX_INT = 2147483647

MIN_INT = -2147483648


def source_resolver(source: str, root, info: GraphQLResolveInfo, **arguments):
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
    is_mounted: bool = False

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
        """Some fields might not have a type associated with them (e.g. ExplicitField),
        so this method should be implemented by the subclasses that require it. If a field does 
        not have a type, it should raise a NotImplementedError."""
        raise NotImplementedError

    def increase_counter(self) -> int:
        self.creation_counter += 1
        return self.creation_counter

    def reset_counter(self):
        self.creation_counter = self.increase_counter()


class ExplicitField(BaseField):  # MountedType
    """An explicit field is a field that is mounted on an object type using 
    the `Field` class. This is the standard way to define fields on an object 
    type, and allows for more control over the field's behavior and configuration.

    .. code-block:: python

        from new_graphene import ObjectType, ExplicitField, String

        class Cars(ObjectType):
            name = ExplicitField(String, description='The name of the car')

    The `Field` class inherits from `ExplicitField`, so it can be used as an explicit field which
    allows it to be used as an explicit field on an object type.

    This class is not intended to be used directly, but is inherited by other types and
    streamlines their use in different contexts:

    - Object Type
    - Scalar Type
    - Enum
    - Interface
    - Union
    """

    is_mounted: bool = True

    @classmethod
    def mount(cls, item: ImplicitField):
        """Creates a new instance of the ExplicitField class by mounting an ImplicitField. 
        This method is used to convert an ImplicitField into an ExplicitField when necessary, 
        allowing for more control over the field's behavior and configuration.

        >>> from new_graphene import String
        ... field = String(description='The name of the car')
        ... explicit_field = ExplicitField.mount(field)
        >>> isinstance(explicit_field, ExplicitField)
        """
        if not isinstance(item, ImplicitField):
            raise TypeError(
                "Expected an ImplicitField, "
                f"got {type(item).__name__}"
            )

        kwargs = item.kwargs | {'counter': item.creation_counter}
        return cls(
            item._get_type(),
            *item.args,
            **kwargs
        )


class ImplicitField(BaseField):  # UnmountedType
    """An implicit field is a field that inherits from Graphene Type and
    allows the class to be dynamically instanciated/mounted on an object type.

    An example of this behaviour would be:

    .. code-block:: python

        from new_graphene import ObjectType, String

        class Cars(ObjectType):
            name = String(description='The name of the car')

    In the above example, the String type is implicity mounted as a Field on the Cars
    ObjectType as opposed to:

    .. code-block:: python

        from new_graphene import ObjectType, Field, String

        class Cars(ObjectType):
            name = Field(String, description='The name of the car')

    This class is not intended to be used directly, but is inherited by other types and 
    streamlines their use in different contexts:

    - Object Type
    - Scalar Type
    - Enum
    - Interface
    - Union

    Args:
        counter (int, optional): The creation counter for the field. If not provided, it will be automatically assigned.
    """

    def __eq__(self, other: TypeField | Any) -> bool:
        truth_array = [
            isinstance(other, ImplicitField),
            all([
                self.get_type() == other.get_type(),
                self.args == other.args,
                self.kwargs == other.kwargs
            ])
        ]
        return any(truth_array)

    def _mount_as(self, instance):
        pass

    def _get_type(self):
        pass

    def mount_as_field(self):
        pass

    def mount_as_argument(self):
        pass


def get_field_as(value: TypeField, mount_type: Optional[ExplicitField] = None):
    """Mount an implicit field as an explicit field if required, otherwise return 
    the explicit field as is. This is useful for cases where we want to allow users 
    to define fields using either the implicit or explicit syntax, but we want to 
    ensure that we always have an explicit field to work with internally.

    .. code-block:: python
        from new_graphene import String

        result = get_field_as(String, mount_type=Field)
        assert isinstance(result, Field)
    """
    if isinstance(value, ExplicitField):
        return value
    elif isinstance(value, ImplicitField):
        if mount_type is None:
            return value
        return mount_type.mount(value)
    return None
