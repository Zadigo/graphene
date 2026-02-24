import functools
from typing import Callable, MutableMapping, Optional

from new_graphene.fields.arguments import Argument
from new_graphene.fields.helpers import ExplicitField, inspect_type
from new_graphene.fields.resolvers import source_resolver
from new_graphene.fields.structures import NonNull
from new_graphene.typings import (TypeArgument, TypeDynamic, TypeMapping,
                                  TypeObjectType, TypeResolver, TypeScalar,
                                  TypeStructure)


class Field[F = type[TypeScalar | TypeObjectType]](ExplicitField):
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
        args (MutableMapping[str, Any], optional): Arguments that can be input to the field. Prefer to use ``**extra_args``, unless you use an argument name that clashes with one of the Field arguments presented here (see :ref:`example<ResolverParamGraphQLArguments>`).
        resolver (Callable, optional): A function to get the value for a Field from the parent value object. If not set, the default resolver method for the schema is used.
        source (str, optional): Attribute name to resolve for this field from the parent value object. Alternative to resolver (cannot set both source and resolver).
        deprecation_reason (str, optional): Setting this value indicates that the field is depreciated and may provide instruction or reason on how for clients to proceed.
        required (bool, optional): Indicates this field as not null in the graphql schema. Same behavior as graphene.NonNull. Default False.
        name (str, optional): The name of the GraphQL field (must be unique in a type). Defaults to attribute name.
        description (str, optional): The description of the GraphQL field in the schema.
        default_value (TypeScalar, optional): Default value to resolve if none set from schema. Cannot be a callable, use a lambda or partial if you need lazy evaluation.
        **extra_args (TypeScalar, optional): Any additional arguments to mount on the field. This can be used to specify additional configuration options for the field, such as custom directives or extensions. These extra arguments will be passed through to the underlying GraphQL library when the schema is generated, allowing for advanced users to take advantage of features that may not be directly supported by the Field class itself.
    """

    def __init__(self, field_type: F, *, args: Optional[TypeMapping[TypeArgument | TypeDynamic]] = None, resolver: Optional[TypeResolver] = None, source: Optional[str] = None, deprecation_reason: Optional[str] = None, name: Optional[str] = None, description: Optional[str] = None, required: bool = False, default_value: Optional[TypeScalar] = None, **extra_args: TypeScalar):
        super().__init__(field_type)

        if not isinstance(field_type, type):
            raise TypeError(
                f"Expected field_type to be a type, got {type(field_type).__name__}"
            )

        if args is not None and not isinstance(args, MutableMapping):
            raise TypeError(
                f"Expected args to be a MutableMapping, got {type(args).__name__}"
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
            field_type = NonNull(field_type)

        if isinstance(name, (Argument, ExplicitField)):
            pass

        self.field_type: F | TypeStructure = field_type
        self.args = args or {}  # TODO: Remove
        self.extra_args = extra_args  # TODO: Remove
        self._arguments = Argument.translate_arguments(self)
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.name = name
        self.description = description
        self.required = required
        self.default_value = default_value

        if source is not None:
            self.resolver = functools.partial(source_resolver, source)

    def __repr__(self) -> str:
        return self.print_field(self)

    def _get_type(self):
        return inspect_type(self.field_type)

    def wrap_resolve(self, parent_resolver):
        return self.resolver or parent_resolver

    def wrap_subscribe(self, parent: Callable | None):
        return parent
        return parent
        return parent
