from typing import Callable

from graphql import GraphQLResolveInfo

from new_graphene.typings import TypeResolver


def attribute_resolver(name: str, default_value, root, info: GraphQLResolveInfo, **arguments):
    return getattr(root, name, default_value)


def dict_resolver(name: str, default_value, root, info: GraphQLResolveInfo, **arguments):
    return root.get(name, default_value)


def default_resolver(name: str, default_value, root, info: GraphQLResolveInfo, **arguments) -> Callable[..., TypeResolver]:
    """The default resolver function used by Graphene to resolve field values. 
    It first checks if the root object is a dictionary and attempts to retrieve the 
    value using the dict_resolver. If the root object is not a dictionary, 
    it falls back to using the attribute_resolver to retrieve the value as 
    an attribute of the root object. This allows for flexible resolution of field 
    values regardless of whether the root object is a dictionary or a regular 
    Python object with attributes.

    Args:
        name (str): The name of the field being resolved.
        default_value (Any): The default value to return if the field cannot be resolved.
        root (Any): The root object from which to resolve the field value. This can be a dictionary or a regular Python object.
        info (GraphQLResolveInfo): An object containing information about the execution state of the query, including the field being resolved, the path to the field, and any arguments passed to the field.
        **arguments (Any): Any additional arguments passed to the field resolver. These can be used to customize the resolution logic.
    """
    def resolver():
        func = dict_resolver if isinstance(root, dict) else attribute_resolver
        return func(name, default_value, root, info, **arguments)
    return resolver
