
from new_graphene.typings import (TypeArgument, TypeBaseOptions, TypeBaseType,
                                  TypeField, TypeImplicitField, TypeScalar,
                                  TypeSchema)


class PrintingMixin:
    """Utility class to print types in a readable format."""

    @staticmethod
    def print_schema(schema: TypeSchema):
        return ''

    @staticmethod
    def print_field(item: TypeField) -> str:
        return f"<{item._meta.name or item.__class__.__name__} :: [{item.field_type.__name__}]>"

    @staticmethod
    def print_argument(item: TypeArgument) -> str:
        return f"<Argument :: {item.name} -> {item.field_type._meta._class_name}>"

    @staticmethod
    def print_implicit_field(item: TypeImplicitField) -> str:
        return f"<{item._meta.name} :: {item.creation_counter}>"

    @staticmethod
    def print_scalar(item: TypeScalar) -> str:
        return f"<{item._meta._internal_name} :: {item.creation_counter}>"

    @staticmethod
    def print_base_options(item: TypeBaseOptions) -> str:
        if item.name == item._internal_name:
            return f"<{item.name}Options for {item.name}>"
        return f"<{item.name}Options for {item._internal_name} :: {item.cls.__name__}>"

    @staticmethod
    def print_base_type(item: TypeBaseType) -> str:
        if item._meta.name == item._meta._internal_name:
            return f"<{item._meta.name}>"
        return f"<{item._meta.name} :: {item._meta._internal_name}>"
