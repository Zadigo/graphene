import functools
import inspect
from typing import Callable

from graphql import GraphQLSchema

from new_graphene.fields.helpers import ImplicitField
from typings import TypeScalar


class Dynamic(ImplicitField):
    """A field that can be defined with a type that is not yet defined 
    at the time of field declaration. The type is resolved at runtime when 
    the schema is generated.
    
    .. code-block:: python
        from new_graphene import ObjectType, String, Dynamic

        class User(ObjectType):
            firstname = Dynamic(lambda: String)

    """

    def __init__(self, lazy_type: Callable[..., TypeScalar] | Callable[[GraphQLSchema], TypeScalar], with_schema=False):
        super().__init__()

        if not inspect.isfunction(lazy_type) and not isinstance(lazy_type, functools.partial):
            raise TypeError("Dynamic field type must be a function.")

        self.field_type = lazy_type
        self.with_schema = with_schema

    def _get_type(self, schema: GraphQLSchema=None):
        if schema is not None and self.with_schema:
            return self.field_type(schema=schema)
        return self.field_type()
