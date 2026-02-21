from typing import TYPE_CHECKING, Any, Callable, Mapping, Sequence

from graphql import (ExecutionContext, GraphQLFieldResolver,
                     GraphQLResolveInfo, GraphQLTypeResolver, Middleware,
                     Source)

if TYPE_CHECKING:
    from new_graphene.fields.arguments import Argument
    from new_graphene.fields.datatypes import Scalar
    from new_graphene.fields.helpers import ExplicitField, ImplicitField
    from new_graphene.fields.interface import Interface
    from new_graphene.fields.objecttypes import ObjectType
    from new_graphene.schema import Schema

type TypeAllTypes = str | int | float | bool | Sequence | Mapping | None

type TypeScalar[T = TypeAllTypes] = Scalar[T]

type TypeField = ExplicitField | ImplicitField

type TypeExplicitField = ExplicitField

type TypeResolver[T= TypeAllTypes] = Callable[[str, GraphQLResolveInfo, str], T]

type TypeObjectType = ObjectType

type TypeInterface = Interface

type TypeSchema = Schema

type TypeArgument = Argument

type TypeGraphqlExecuteOptions = str | bool | Source | GraphQLFieldResolver | GraphQLTypeResolver | type[
    ExecutionContext] | Middleware | Mapping[str, Any]

type TypeGraphqlExecuteKwargs[T= TypeGraphqlExecuteOptions] = Mapping[str, T]

type TypeGraphqlExecuteArgs[T = TypeGraphqlExecuteOptions] = Sequence[T]
type TypeGraphqlExecuteArgs[T = TypeGraphqlExecuteOptions] = Sequence[T]
type TypeGraphqlExecuteArgs[T = TypeGraphqlExecuteOptions] = Sequence[T]
