from new_graphene.typings import TypeArgument, TypeImplicitField, TypeSchema


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
