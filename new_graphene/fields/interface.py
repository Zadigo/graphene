from typing import ClassVar

from graphql import GraphQLResolveInfo
from typings import TypeInterface

from new_graphene.base import BaseType
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.utils.base import ObjectTypesEnum


class Interface(BaseType):
    """An interface is an abstract type that includes a certain set of 
    fields that a type must use in order to resolve the possible types that
    the field can resolve to. An `Interface` simply defines what types
    are possible for the field resolution.

    .. code:: python

        from new_graphene import Interface, String

        class HasAddress(Interface):
            class Meta:
                description = "Address fields"

            address1 = String()
            address2 = String()

    The example above defines an interface `HasAddress` with two fields, `address1` and `address2`. 
    Any type that implements this interface must include these fields. When a field returns an 
    `Interface` type, the actual type of the object can be determined using the `resolve_type` method on 
    the `Interface` or by defining possible types in the `Meta` class of an `ObjectType` that implements 
    the interface.

    .. code:: python

        from new_graphene import ObjectType, String

        class User(ObjectType):
            class Meta:
                interfaces = (HasAddress,)

            name = String()


    Meta class options (optional):
        name (str): Name of the GraphQL type (must be unique in schema). Defaults to class name.
        description (str): Description of the GraphQL type in the schema. Defaults to class docstring.
    """

    is_interface_type = True  # TODO: Remove
    internal_type: ClassVar[ObjectTypesEnum] = ObjectTypesEnum.INTERFACE

    def __init__(self, *args, **kwargs):
        raise TypeError("Interfaces cannot be instantiated directly.")

    @classmethod
    def resolve_type(cls, instance: TypeInterface, info: GraphQLResolveInfo):
        if isinstance(instance, ObjectType):
            return type(instance)
        return None
