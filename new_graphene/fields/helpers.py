import functools
import inspect
from functools import total_ordering
from typing import Any, Callable, Optional, Type
from warnings import deprecated

from new_graphene.typings import (TypeArgument, TypeFieldType, TypeObjectType,
                                  TypeScalar)
from new_graphene.utils.base import ObjectTypesEnum
from new_graphene.utils.module_loading import import_string
from new_graphene.utils.printing import PrintingMixin


# get_type
@deprecated('We will be importing the items directly in _get_type instead of using this helper function.')
def inspect_type(item: TypeFieldType | TypeScalar | Callable[..., Any] | Any):
    """Inspect the type of an item and return it. This function is 
    used to resolve the type of an item that can be defined by
    a Python path string, a callable, or a direct instance."""
    if isinstance(item, str):
        return import_string(item)

    if inspect.isfunction(item) or isinstance(item, functools.partial):
        return item()

    return item


MAX_INT = 2147483647

MIN_INT = -2147483648


class BaseFieldOptions:
    def __init__(self, name: str, cls: TypeFieldType):
        self.cls = cls
        self.name: str = None
        self.description: Optional[str] = None
        self._internal_name: str = None
        self._class_name: str = name

        if self.name is None:
            self.name = self._class_name
            self._internal_name = self._class_name

    def __repr__(self):
        return f"<{self.name or self._class_name}Options [{self.cls}]>"


class BaseFieldType(type):
    def __new__(cls, name: str, bases: tuple[Type], attrs: dict):
        super_new = super().__new__
        options = BaseFieldOptions(name, cls)
        attrs['_meta'] = options
        return super_new(cls, name, bases, attrs)


@total_ordering
class BaseField(PrintingMixin):
    """BaseField is the base class for all field types in the Graphene library. It is a container
    that saves information about the field, such as its type, resolver, and other configuration options.

    It provides common functionality and attributes that are shared across different field types, 
    such as ObjectType fields, ScalarType fields, Enum fields, Interface fields, and Union fields. 
    This class is not intended to be used directly, but is inherited by other types and streamlines
    their use in different contexts.

    Args:
        *args: Positional arguments that can be passed to the field. These are typically used to define the type of the field and any additional configuration options.
        **kwargs: Keyword arguments that can be passed to the field. These are typically used to define additional configuration options for the field, such as a resolver function, description, deprecation reason, etc.
        counter (int, optional): The creation counter for the field. If not provided, it will be automatically assigned. This counter is used to maintain the order of field definitions, ensuring that fields are processed in the order they were defined in the class.
    """

    creation_counter: int = 1
    is_mounted: bool = False
    internal_type: Optional[ObjectTypesEnum] = ObjectTypesEnum.FIELD
    _meta: Optional[BaseFieldOptions]

    def __init__(self, *args: TypeArgument, **kwargs: TypeArgument):
        self.args = args
        self.kwargs = kwargs
        self._arguments: dict[str, TypeArgument] = {}

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

    @deprecated("This methods will be remaed to 'get_field_typ'")
    def _get_type(self) -> TypeScalar | TypeObjectType:  # TypeScalar ??
        """Some fields might not have a `field_type` associated with them (e.g. ExplicitField),
        so this method should be implementedin order to return the underlying field type associated
        with the field. If a field does not have a type, it should raise a NotImplementedError."""
        raise NotImplementedError

    @deprecated("This method will be removed in a future version.")
    def reset_counter(self):
        self.creation_counter = self.increase_counter()


class ExplicitField(BaseField, metaclass=BaseFieldType):  # MountedType
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

    def __init__(self, field_type: Type[TypeScalar | TypeObjectType], *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not inspect.isclass(field_type) and not issubclass(field_type, (TypeScalar, TypeObjectType)):
            raise TypeError(
                f"Expected a class of type TypeScalar or TypeObjectType, "
                f"got {type(field_type).__name__}"
            )

        self.field_type = field_type

    def __repr__(self) -> str:
        return self.print_field(self)

    @classmethod
    def create_new_field(cls, item: ImplicitField):
        """Creates a new instance of an `ExplicitField` class with an `ImplicitField`. 
        This method is used to convert an `ImplicitField` into an `ExplicitField` when necessary, 
        allowing for more control over the field's behavior and configuration.

        >>> from new_graphene import String
        ... explicit_field = ExplicitField.create_new_field(String())
        Field
        """
        if not isinstance(item, ImplicitField):
            raise TypeError(
                "Expected an ImplicitField, "
                f"got {type(item).__name__}"
            )

        # FIXME: This raises a "TypeError: Field.__init__() takes 2 positional arguments but 3 were given" error in the case
        # of List(User) for example because the "field_type" is
        # the args. The correct writing would then be:
        # cls(*item.args, **item.kwargs)
        instance = cls(
            item._get_type(),
            *item.args,
            **item.kwargs
        )

        return instance

    def _get_type(self):
        return self.field_type


class ImplicitField(BaseField, metaclass=BaseFieldType):  # UnmountedType
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

    def __repr__(self):
        return self.print_field(self)

    def __eq__(self, other: TypeFieldType | Any) -> bool:
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
        return self.__class__

    def mount_as_field(self):
        pass

    def mount_as_argument(self):
        pass


def mount_type_as(value: TypeFieldType, mount_type: Optional[ExplicitField] = None):
    """Mount an `ImplicitField` as an `ExplicitField` (e.g. `Field`).

    .. code-block:: python
        from new_graphene import String

        result = mount_type_as(String, mount_type=Field)
        assert isinstance(result, Field)
    """
    if isinstance(value, ExplicitField):
        return value
    elif isinstance(value, ImplicitField):
        if mount_type is None:
            return value
        return mount_type.create_new_field(value)
    return None
