import functools
import inspect
from typing import Any, Callable, Mapping, Optional

from graphene.utils.module_loading import import_string
from new_graphene.fields.base import BaseField, source_resolver
from new_graphene.typings import TypeField, TypeResolver, TypeScalar


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


class Field(ExplicitField):
    """The `Field` class is used explicitly to define a field on an ObjectType 
    in the Graphene library. It allows for more control over the field's behavior 
    and configuration compared to implicit fields. The `Field` class can be used to 
    specify the type of the field, any arguments it may take, a resolver function, 
    and other options such as deprecation reason, description, and default value.

    .. code-block:: python

        from new_graphene import ObjectType, Field, String

        class Cars(ObjectType):
            name = Field(String, description='The name of the car')

    Args:
        field_type (TypeScalar): The type of the field in the GraphQL schema. This can be a scalar type, an object type, an enum, an interface, or a union.
        args (Mapping[str, Any], optional): Arguments that can be input to the field. Prefer to use ``**extra_args``, unless you use an argument name that clashes with one of the Field arguments presented here (see :ref:`example<ResolverParamGraphQLArguments>`).
        resolver (Callable, optional): A function to get the value for a Field from the parent value object. If not set, the default resolver method for the schema is used.
        source (str, optional): Attribute name to resolve for this field from the parent value object. Alternative to resolver (cannot set both source and resolver).
        deprecation_reason (str, optional): Setting this value indicates that the field is depreciated and may provide instruction or reason on how for clients to proceed.
        required (bool, optional): Indicates this field as not null in the graphql schema. Same behavior as graphene.NonNull. Default False.
        name (str, optional): The name of the GraphQL field (must be unique in a type). Defaults to attribute name.
        description (str, optional): The description of the GraphQL field in the schema.
        default_value (TypeScalar, optional): Default value to resolve if none set from schema. Cannot be a callable, use a lambda or partial if you need lazy evaluation.
        **extra_args (Any, optional): Any additional arguments to mount on the field. This can be used to specify additional configuration options for the field, such as custom directives or extensions. These extra arguments will be passed through to the underlying GraphQL library when the schema is generated, allowing for advanced users to take advantage of features that may not be directly supported by the Field class itself.
    """

    def __init__(self, field_type: TypeScalar, args: Mapping[str, Any] = None, resolver: Optional[TypeResolver] = None, source: Optional[str] = None, deprecation_reason: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, required: bool = False, creation_counter: Optional[int] = None, default_value: TypeScalar = None, **extra_args: Any):
        super().__init__(counter=creation_counter)

        if args is not None and not isinstance(args, Mapping):
            raise TypeError(
                f"Expected args to be a Mapping, got {type(args).__name__}"
            )

        if source is not None and resolver is not None:
            raise ValueError(
                "Cannot specify both 'source' and 'resolver' for a Field."
            )

        if default_value is not None and callable(default_value):
            raise ValueError(
                "default_value cannot be a callable. Use a lambda or partial if you need lazy evaluation."
            )

        if required:
            pass

        self.field_type = field_type
        self.args = args or {}
        self.extra_args = extra_args
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.name = name
        self.description = description
        self.required = required
        self.default_value = default_value

        if source is not None:
            self.resolver = functools.partial(source_resolver, source)

    # def __repr__(self):
    #     return f"<Field: {self.name or self.field_type._meta.name}>"

    def _get_type(self):
        return inspect_type(self.field_type)

    def wrap_resolve(self, parent):
        pass

    def wrap_subscribe(self, parent):
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
