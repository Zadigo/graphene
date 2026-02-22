import datetime
from decimal import Decimal as PythonDecimal
from typing import Any, ClassVar, Optional, Type

import graphql
from graphql import (BooleanValueNode, FloatValueNode, IntValueNode,
                     StringValueNode, Undefined, ValueNode)
from graphql.error import GraphQLError

from new_graphene.base import BaseType
from new_graphene.fields.helpers import ImplicitField
from new_graphene.utils.base import ObjectTypesEnum

MAX_INT = 2147483647

MIN_INT = -2147483648


class Scalar[T= Any](ImplicitField, BaseType):
    """A scalar type represents a primitive value in GraphQL. It is used to define fields 
    that return simple values such as strings, numbers, or booleans. Each specific scalar 
    type (e.g., Integer, String, Boolean) will implement the parsing and resolution logic 
    for that type.

    As an `ImplicitField` it can then be used directly in `ObjectType` definitions without 
    needing to be wrapped in a `Field`. For example:

    .. code:: python
        from new_graphene import ObjectType, Scalar

        class Query(ObjectType):
            age = Scalar()
    """

    is_scalar: ClassVar[bool] = True # TODO: Remove
    internal_type: ClassVar[ObjectTypesEnum] = ObjectTypesEnum.SCALAR

    def __repr__(self):
        return self.print_scalar(self)

    @staticmethod
    def parse_literal(node: ValueNode, variables: Optional[dict[str, Any]] = None) -> T:
        """Parse a GraphQL literal value into a Python value. This method should be
        implemented by each specific scalar type to handle the parsing logic for that type.

        This method is used in `GrapheneGraphqlScalarType.parse_literal` to convert GraphQL literals 
        into Python values when processing queries.

        :param node: The GraphQL AST node representing the literal value.
        :param variables: Optional dictionary of variables that may be used in the parsing process.
        :return: The parsed Python value corresponding to the GraphQL literal.
        """
        raise NotImplementedError(f"parse_literal not implemented")

    @staticmethod
    def resolve_value(value: Any) -> T:
        """Resolve a Python value into the appropriate type for this scalar. This method should be
        implemented by each specific scalar type to handle the resolution logic for that type.

        This method is used in `GrapheneGraphqlScalarType.serialize` to convert Python values
        into a format suitable for GraphQL responses.

        :param value: The Python value to be resolved.
        :return: The resolved value in the appropriate format for this scalar type.
        """
        return value

    def _get_type(self) -> Type[Scalar]:
        return self.__class__


class Generic(Scalar[Any]):
    """A generic scalar type that can represent any value. It will be translated 
    to a GraphQL String, but it can accept any Python value.

    .. code:: python

        from new_graphene import ObjectType, Generic

        class Query(ObjectType):
            age = Generic()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        match node:
            case StringValueNode():
                return node.value
            case graphql.language.ast.BooleanValueNode():
                return node.value
            case IntValueNode():
                num = int(node.value)
                if MIN_INT <= num <= MAX_INT:
                    return num
            case graphql.language.ast.FloatValueNode():
                return float(node.value)
            case graphql.language.ast.ListValueNode():
                return [Generic.parse_literal(value) for value in node.values]
            case graphql.language.ast.ObjectValueNode():
                return {
                    field.name.value: Generic.parse_literal(field.value)
                    for field in node.fields
                }
            case _:
                return None


class Integer(Scalar[int]):
    """Graphene Integer type which will be translated to a GraphQL Int. 
    It is a 32-bit signed integer. Values outside this range will be rejected.

    .. Note:: If you need to represent larger integers, consider using the BigInteger type instead.

    .. code:: python

        from new_graphene import ObjectType, Integer

        class Query(ObjectType):
            age = Integer()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, IntValueNode):
            value = int(node.value)
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
    """Graphene BigInteger type which will be translated to a GraphQL Int. 
    It can represent integers of arbitrary size, but be aware that some GraphQL 
    implementations may not support it.

    .. code:: python

        from new_graphene import ObjectType, BigInteger

        class Query(ObjectType):
            age = BigInteger()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, IntValueNode):
            return int(node.value)
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
    """Graphene Float type which will be translated to a GraphQL Float.

    .. code:: python

        from new_graphene import ObjectType, Float

        class Query(ObjectType):
            value = Float()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, (FloatValueNode, IntValueNode)):
            return float(node.value)
        return Undefined

    @staticmethod
    def resolve_value(value):
        try:
            value = float(value)
        except ValueError:
            return Undefined


class String(Scalar[str]):
    """Graphene String type which will be translated to a GraphQL String. 

    .. code:: python

        from new_graphene import ObjectType, String

        class Query(ObjectType):
            name = String()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, StringValueNode):
            return node.value
        return Undefined

    @staticmethod
    def resolve_value(value):
        if isinstance(value, bool):
            return 'true' if value else 'false'
        return str(value)


class Boolean(Scalar[bool]):
    """Graphene Boolean type which will be translated to a GraphQL Boolean. 

    .. code:: python

        from new_graphene import ObjectType, Boolean

        class Query(ObjectType):
            is_active = Boolean()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, BooleanValueNode):
            return node.value
        return Undefined


class ID(Scalar[str]):
    """Graphene ID type which will be translated to a GraphQL ID. 

    .. code:: python

        from new_graphene import ObjectType, ID

        class Query(ObjectType):
            id = ID()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, (StringValueNode, IntValueNode)):
            return node.value
        return Undefined


class Date(Scalar[str]):
    """Graphene Date type which will be translated to a GraphQL String. 
    It can represent dates in ISO 8601 format.

    .. code:: python

        from new_graphene import ObjectType, Date

        class Query(ObjectType):
            date = Date()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, StringValueNode):
            return node.value
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
    """Graphene DateTime type which will be translated to a GraphQL String. 
    It can represent dates in ISO 8601 format.

    .. code:: python

        from new_graphene import ObjectType, DateTime

        class Query(ObjectType):
            date = DateTime()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, StringValueNode):
            return node.value
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
    """Graphene Time type which will be translated to a GraphQL String.
    It can represent times in ISO 8601 format.

    .. code:: python

        from new_graphene import ObjectType, Time

        class Query(ObjectType):
            time = Time()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, StringValueNode):
            return node.value
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


class Decimal(Scalar[str]):
    """Graphene Decimal type which will be translated to a GraphQL String. 
    It can represent decimal numbers with arbitrary precision.

    .. code:: python

        from new_graphene import ObjectType, Decimal

        class Query(ObjectType):
            price = Decimal()
    """

    @staticmethod
    def parse_literal(node, variables=None):
        if isinstance(node, (IntValueNode, StringValueNode)):
            return node.value
        return Undefined

    @staticmethod
    def resolve_value(value):
        try:
            return PythonDecimal(value)
        except Exception:
            return Undefined
