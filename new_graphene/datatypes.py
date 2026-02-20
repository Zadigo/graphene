import datetime
from functools import total_ordering
import functools
from typing import Any, Mapping, Optional

import graphql
from graphql import Undefined

from new_graphene.base import BaseType
from graphql.error import GraphQLError

MAX_INT = 2147483647

MIN_INT = -2147483648


def source_resolver(source: str, root, info, **args):
    pass


@total_ordering
class BaseField:
    creation_counter = 1

    def __init__(self, counter: int = None):
        self.creation_counter = counter or self.increase_counter()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseField):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, BaseField):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, BaseField):
            return self.creation_counter > other.creation_counter
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.creation_counter)

    def increase_counter(self):
        self.creation_counter += 1
        return self.creation_counter

    def reset_counter(self):
        self.creation_counter = self.increase_counter()

    def get_type(self):
        raise NotImplementedError

    def _mount_as(self, instance):
        pass


class ExplicitField(BaseField):
    pass


class ImplicitField(BaseField):
    """An implicit field is a field that inherits from Graphene Type and
    allows the class to be dynamically instanciated/mounted on an object type.

    An exampmple of this behaviour would be:

    .. code-block:: python

        from new_graphene import ObjectType, String

        class Cars(ObjectType):
            name = String(description='The name of the car')

    In this example, the String type is implicitly mounted as a Field on the Cars ObjectType. As opposed to:

    .. code-block:: python

        from new_graphene import ObjectType, Field, String

        class Cars(ObjectType):
            name = Field(String, description='The name of the car')

    This class is not intended to be used directly, but is inherited by other types and 
    streamlines their use in different contexts:

    - Object Type
    - Scalar Type
    - Enum
    - Interface
    - Union

    Args:
        counter (int, optional): The creation counter for the field. If not provided, it will be automatically assigned.
    """
    creation_counter = 1

    def __init__(self, *args, counter: Optional[int] = None, **kwargs):
        super().__init__(counter=counter, *args, **kwargs)


class Field(ExplicitField):
    def __init__(self, field_type: str, args: Mapping[str, Any] = None, resolver=None, source=None, deprecation_reason=None, name: Optional[str] = None, description: Optional[str] = None, required: bool = False, creation_counter: Optional[int] = None, default_value=None, **extra_args):
        super().__init__(counter=creation_counter)

        if args is not None and not isinstance(args, Mapping):
            raise TypeError(
                f"Expected args to be a Mapping, got {type(args).__name__}")

        if source is not None and resolver is not None:
            raise ValueError(
                "Cannot specify both 'source' and 'resolver' for a Field.")

        if default_value is not None and callable(default_value):
            raise ValueError(
                "default_value cannot be a callable. Use a lambda or partial if you need lazy evaluation.")

        if required:
            pass

        self.field_type = field_type
        self.args = args or {}
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.name = name
        self.description = description
        self.required = required
        self.default_value = default_value
        self.extra_args = extra_args

        if source is not None:
            self.resolver = functools.partial(source_resolver, source)


class Scalar[T](ImplicitField, BaseType):
    @staticmethod
    def parse_literal(ast: graphql.language.ast.ValueNode, variables=None) -> T:
        raise NotImplementedError(f"parse_literal not implemented")

    @staticmethod
    def resolve_value(value: Any) -> T:
        return value


class Generic(Scalar[Any]):
    @staticmethod
    def parse_literal(ast: graphql.language.ast.ValueNode, variables=None):
        match ast:
            case graphql.language.ast.StringValueNode():
                return ast.value
            case graphql.language.ast.BooleanValueNode():
                return ast.value
            case graphql.language.ast.IntValueNode():
                num = int(ast.value)
                if MIN_INT <= num <= MAX_INT:
                    return num
            case graphql.language.ast.FloatValueNode():
                return float(ast.value)
            case graphql.language.ast.ListValueNode():
                return [Generic.parse_literal(value) for value in ast.values]
            case graphql.language.ast.ObjectValueNode():
                return {
                    field.name.value: Generic.parse_literal(field.value)
                    for field in ast.fields
                }
            case _:
                return None


class Integer(Scalar[int]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.IntValueNode):
            value = int(ast.value)
            if MIN_INT <= value <= MAX_INT:
                return value
        return Undefined

    @staticmethod
    def resolve_value(value):
        try:
            value = int(value)
        except ValueError:
            try:
                value = int(float(value))
            except ValueError:
                return Undefined

        if MIN_INT <= value <= MAX_INT:
            return value

        return Undefined


class BigInteger(Scalar[int]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.IntValueNode):
            return int(ast.value)
        return Undefined

    @staticmethod
    def resolve_value(value):
        _value = Undefined

        try:
            _value = int(value)
        except ValueError:
            pass

        if _value is not Undefined:
            return _value

        try:
            _value = int(float(value))
        except ValueError:
            pass

        return _value


class Float(Scalar[float]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, (graphql.language.ast.FloatValueNode, graphql.language.ast.IntValueNode)):
            return float(ast.value)
        return Undefined

    @staticmethod
    def resolve_value(value):
        try:
            value = float(value)
        except ValueError:
            return Undefined


class String(Scalar[str]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.StringValueNode):
            return ast.value
        return Undefined

    @staticmethod
    def resolve_value(value):
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value)


class Boolean(Scalar[bool]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.BooleanValueNode):
            return ast.value
        return Undefined


class ID(Scalar[str]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, (graphql.language.ast.StringValueNode, graphql.language.ast.IntValueNode)):
            return ast.value
        return Undefined


class Date(Scalar[str]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.StringValueNode):
            return ast.value
        return Undefined

    @staticmethod
    def resolve_value(value):
        if isinstance(value, datetime.date):
            return value

        if not isinstance(value, str):
            raise GraphQLError(
                "Date cannot represent "
                f"non-string value: {repr(value)}"
            )

        try:
            return datetime.date.fromisoformat(value)
        except ValueError:
            raise GraphQLError(f"Date cannot represent value: {repr(value)}")


class DateTime(Scalar[str]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.StringValueNode):
            return ast.value
        return Undefined

    @staticmethod
    def resolve_value(value):
        if isinstance(value, (datetime.datetime, datetime.date)):
            return value

        if not isinstance(value, str):
            raise GraphQLError(
                "DateTime cannot represent "
                f"non-string value: {repr(value)}"
            )

        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            raise GraphQLError(
                f"DateTime cannot represent value: {repr(value)}")


class Time(Scalar[str]):
    @staticmethod
    def parse_literal(ast, variables=None):
        if isinstance(ast, graphql.language.ast.StringValueNode):
            return ast.value
        return Undefined

    @staticmethod
    def resolve_value(value):
        if isinstance(value, datetime.time):
            return value

        if not isinstance(value, str):
            raise GraphQLError(
                "Time cannot represent "
                f"non-string value: {repr(value)}"
            )

        try:
            return datetime.time.fromisoformat(value)
        except ValueError:
            raise GraphQLError(
                f"Time cannot represent value: {repr(value)}")
