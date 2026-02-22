from typing import ClassVar

from new_graphene.base import BaseType
from new_graphene.utils.base import ObjectTypesEnum


class ObjectType(BaseType):
    """An ObjectType is a type that represents an object in the GraphQL schema. 
    It can have fields and interfaces. An ObjectType works like a dataclass, where the fields 
    are defined as class attributes.

    .. code-block:: python

        from new_graphene import ObjectType, String, Field

        class Person(ObjectType):
            name = String()
            age = Field(Integer)

    An ObjectType can also have a Meta inner class to define additional options, 
    such as description and interfaces.

    .. code-block:: python

        from new_graphene import ObjectType, String, Field

        class Person(ObjectType):
            name = String()
            age = Field(Integer)

            class Meta:
                description = "A person object"

    Acting like a dataclass, it can also be used as a regular dataclass instance with the defined fields.

    .. code-block:: python

        person = Person(name="Alice", age=30)
        print(person.name)  # Output: Alice
        print(person.age)   # Output: 30

    Meta class options (optional):
        name (str): Name of the GraphQL type (must be unique in schema). Defaults to class name.
        description (str): Description of the GraphQL type in the schema. Defaults to class docstring.
        interfaces (Iterable[graphene.Interface]): GraphQL interfaces to extend with this object. All fields from interface will be included in this object's schema.
        possible_types (Iterable[graphene.ObjectType]): GraphQL object types that implement this interface. Used for type resolution in interfaces and unions.
        default_resolver (Callable): Default resolver function for fields in this object type. If not provided, the default resolver will be used.
        fields (Dict[str, graphene.Field]): A dictionary of field names to Field instances. This is used to define the fields of the object type.
    """

    is_object_type: ClassVar[bool] = True # TODO: Remove
    internal_type: ClassVar[ObjectTypesEnum] = ObjectTypesEnum.OBJECT_TYPE
