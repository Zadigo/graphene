from ast import List
from functools import partial
from importlib import import_module
from typing import Any, Callable, Sequence

from new_graphene.typings import TypeImports


def import_string(dotted_path: str, attributes: Sequence[str] = []):
    """Import a dotted module path and return the attribute/class designated 
    by the last name in the path. Raise ImportError if the import failed.

    Args:
        dotted_path (str): The dotted path to the module and attribute/class to import. For example, 'new_graphene.fields.arguments.Argument' would import the Argument class from the arguments module in the fields package of the new_graphene library.
        attributes (Sequence[str], optional): A sequence of attribute names to access on the imported module or class. For example, if the dotted_path is 'new_graphene.fields.arguments' and attributes is ['Argument'], the function would import the arguments module and then access the Argument attribute on that module. Defaults to an empty list, which means no additional attributes will be accessed and the function will return the imported module or class directly.
    """
    module_path, class_name = dotted_path.rsplit('.', 1)
    try:
        module = import_module(module_path)
    except ModuleNotFoundError:
        raise

    try:
        result: TypeImports = getattr(module, class_name)
    except AttributeError:
        raise AttributeError(
            f"Module {module_path} does not "
            f"define a {class_name} attribute/class"
        )

    if not attributes:
        return result

    try:
        loaded_attributes: List[Callable[..., Any] | Any] = []

        for attribute in attributes:
            result = getattr(result, attribute)
            loaded_attributes.append(result)
    except AttributeError:
        raise AttributeError(
            f"Module {module_path} does not "
            f"define a {attribute} attribute/class"
        )
    return loaded_attributes


def lazy_import(dotted_path: str, attributes: Sequence[str] = []):
    """Return a lazy reference to an imported module or attribute/class. 
    The import will be performed when the returned function is called.

    .. seealso:: import_string
    """
    return partial(import_string, dotted_path, attributes)
