
from new_graphene.typings import (TypeArgument, TypeBaseOptions, TypeBaseType,
                                  TypeImplicitField, TypeScalar, TypeSchema)


class PrintingMixin:
    """Utility class to print types in a readable format."""

    @staticmethod
    def print_schema(schema: TypeSchema):
        return ''

    @staticmethod
    def print_argument(item: TypeArgument) -> str:
        field_type = item.print_implicit_field(item.field_type)
        return f"<Argument: [{item.name}] required={item.required} field_type={field_type}>"

    @staticmethod
    def print_implicit_field(item: TypeImplicitField) -> str:
        return f"<{item._meta.name}: {item.creation_counter}>"

    @staticmethod
    def print_scalar(item: TypeScalar) -> str:
        return f"<{item._meta._internal_name}: [{item.creation_counter}]>"

    @staticmethod
    def print_base_options(item: TypeBaseOptions) -> str:
        name = item.__class__.__name__
        return f"<{name} for {item.name}[{item._internal_name}]>"

    @staticmethod
    def print_base_type(item: TypeBaseType) -> str:
        name = item.__class__.__name__
        return f"<{name} [{item._meta._internal_name}]>"
