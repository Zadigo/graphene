import datetime
from typing import Any

import graphql
from graphql import Undefined
from graphql.error import GraphQLError

from new_graphene.base import BaseType
from new_graphene.fields.helpers import ImplicitField

MAX_INT = 2147483647

MIN_INT = -2147483648


class Scalar[T](ImplicitField, BaseType):
    @staticmethod
    def parse_literal(ast: graphql.language.ast.ValueNode, variables=None) -> T:
        raise NotImplementedError(f"parse_literal not implemented")

    @staticmethod
    def resolve_value(value: Any) -> T:
        return value
    
    def _get_type(self):
        return self.__class__


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
            return datetime.time.fromisoformat(value)
        except ValueError:
            raise GraphQLError(
                f"Time cannot represent value: {repr(value)}")
            return datetime.time.fromisoformat(value)
        except ValueError:
            raise GraphQLError(
                f"Time cannot represent value: {repr(value)}")
