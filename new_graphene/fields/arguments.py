import itertools
from collections import OrderedDict
from typing import Any, MutableMapping, Optional

from new_graphene.fields.dynamic import Dynamic
from new_graphene.fields.helpers import ExplicitField, ImplicitField
from new_graphene.typings import TypeField, TypeScalar


class Argument(ExplicitField):
    """An argument is a special type of field that is used to define the arguments of a field in a 
    GraphQL schema. Arguments are defined using the `Argument` class, and can be used to specify the type, 
    default value, and other configuration options for the argument.

    The `args` and `extra_args` parameters of the `Field` class can be used to specify the arguments for a field. 
    The `translate_arguments` class method is responsible for translating the provided arguments into 
    instances of the `Argument` class, which can then be used in the GraphQL schema.

    .. code-block:: python
        from new_graphene import ObjectType, Field, String, Argument

        class Cars(ObjectType):
            name = Field(String, args={'search': Argument(String)})
            lastname = Field(String, search=Argument(String))

    Providing an argument on an ImplicitField does the exact same thing as the above example, but is more concise:

    .. code-block:: python
        from new_graphene import ObjectType, String

        class Cars(ObjectType):
            name = String(search=String(description="The name of the car"))

    Which is equivalent to:

    .. code-block:: python
        from new_graphene import ObjectType, String, Argument

        class Cars(ObjectType):
            name = String(search=Argument(String))

    Args:
        field_type (TypeScalar): The type of the argument in the GraphQL schema. This can be a scalar type, an object type, an enum, an interface, or a union.
        default_value (Any, optional): The value to be provided if the user does not set this argument in the operation.
        deprecation_reason (str, optional): Setting this value indicates that the argument is deprecated and may provide instruction or reason on how for clients to proceed. Cannot be set if the argument is required (see spec).
        name (str, optional): The name of the argument. Defaults to parameter name.
        required (bool, optional): Indicates this argument as not null in the graphql schema. Same behavior as graphene.NonNull. Default False.
        counter (int, optional): The creation counter for the argument. If not provided, it will be automatically assigned.
    """

    def __init__(self, field_type: type[TypeScalar], default_value: Optional[Any] = None, deprecation_reason: Optional[str] = None, name: Optional[str] = None, required: bool = False, counter: Optional[int] = None):
        super().__init__(field_type, counter=counter)

        self.field_type = field_type
        self.default_value = default_value
        self.deprecation_reason = deprecation_reason
        self.name = name
        self.required = required

    def __repr__(self):
        return self.print_argument(self)

    def __eq__(self, other: Any) -> bool:
        return all([
            isinstance(other, Argument),
            self.name == other.name,
            self.field_type == other.field_type,
            self.default_value == other.default_value,
            self.deprecation_reason == other.deprecation_reason,
            self.required == other.required
        ])

    @classmethod
    def translate_arguments(cls, field_obj: TypeField) -> MutableMapping[str, 'Argument']:
        """Translate a set of arguments provided to a field into instances of the `Argument` class.
        Invalid arguments will raise `ValueError`."""
        from new_graphene.fields.base import Field
        from new_graphene.fields.input import InputField

        all_args = list(
            itertools.chain(
                field_obj.args.items(),
                field_obj.extra_args.items()
            )
        )

        final_arguments = OrderedDict()

        for key, value in all_args:
            if isinstance(value, Dynamic):
                field_type = value._get_type()
                if field_type is None:
                    continue

            instance: Optional[Argument] = None

            if isinstance(value, ImplicitField):
                instance = cls.create_new_field(value)

            if isinstance(value, (Field, InputField)):
                raise ValueError(
                    f"Expected {key} to be Argument, but received {type(value).__name__}. Try using Argument({value.field_type})."
                )
            
            if instance is None and isinstance(value, cls):
                instance = value

            if instance is not None:
                if not isinstance(instance, Argument):
                    raise ValueError(f'Unknown argument "{key}".')

                default_name = instance.name or key
                if instance.name is None:
                    instance.name = default_name

                if default_name in final_arguments:
                    raise ValueError(
                        f'More than one Argument have same name "{default_name}".')

                final_arguments[default_name] = instance

        return final_arguments

    # def _get_type(self):
    #     return None
