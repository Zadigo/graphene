import functools
from typing import Any, Mapping, Optional

from new_graphene.fields.arguments import Argument
from new_graphene.fields.helpers import (ExplicitField, inspect_type,
                                         source_resolver)
from new_graphene.typings import TypeResolver, TypeScalar


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
        self.args = args or {}, extra_args
        self.extra_args = extra_args
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.name = name
        self.description = description
        self.required = required
        self.default_value = default_value

        self._arguments = Argument.translate_arguments(
            self.args, self.extra_args)

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
