from typing import Any

from new_graphene.fields.helpers import ImplicitField
from new_graphene.typings import TypeObjectType, TypeScalar


class Structure(ImplicitField):
    """Wrap a type within a structure. This is used for `List` and `NonNull` types, 
    which are wrappers around other types to indicate that they are lists 
    or non-nullable
    """

    def __init__(self, field_type: type[TypeScalar | TypeObjectType], *args, **kwargs):
        super().__init__(field_type, *args, **kwargs)

        if not isinstance(field_type, Structure) and isinstance(field_type, ImplicitField):
            raise TypeError(
                f"{type(self).__name__} could not have a mounted {type(field_type).__name__}()"
                f" as inner type. Try with {type(self).__name__}({type(field_type).__name__})."
            )

        self.field_type = field_type

    def __eq__(self, other: Any):
        return super().__eq__(other)


class List(Structure):
    """Indicates that the field is a list of the given type. For example, `List(String)` 
    indicates that the field is a list of strings.

    .. code:: python

        from new_graphene import NonNull, String, ObjectType

        class Cars(ObjectType):
            firstname = List(String) # Field will be a list of strings
    """

    def __str__(self):
        return f"[{self.field_type}]"

    def __eq__(self, other):
        return all([
            isinstance(other, List),
            super().__eq__(other)
        ])


class NonNull(Structure):
    """Indicates that the field is non-nullable. For example, `NonNull(String)` indicates 
    that the field is a non-nullable string.

    .. code:: python

        from new_graphene import NonNull, String, ObjectType

        class Cars(ObjectType):
            firstname = NonNull(String) # Field will not be null
            lastname = String(required=True) # Equivalent
    """

    def __str__(self):
        return f"{self.field_type}!"

    def __eq__(self, other):
        return all([
            isinstance(other, NonNull),
            super().__eq__(other)
        ])
