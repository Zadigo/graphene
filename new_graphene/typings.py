from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Mapping,
                    MutableMapping, Protocol, Sequence, Type,
                    runtime_checkable)

from graphql import (ExecutionContext, GraphQLFieldResolver,
                     GraphQLInterfaceType, GraphQLObjectType,
                     GraphQLResolveInfo, GraphQLScalarType,
                     GraphQLTypeResolver, Middleware, Source)

if TYPE_CHECKING:
    from new_graphene.base import BaseOptions, BaseType
    from new_graphene.fields.arguments import Argument
    from new_graphene.fields.base import Field
    from new_graphene.fields.helpers import ExplicitField, ImplicitField
    from new_graphene.fields.interface import Interface
    from new_graphene.fields.objecttypes import ObjectType
    from new_graphene.fields.scalars import Scalar
    from new_graphene.schema import Schema

type TypeAllTypes = str | int | float | bool | Sequence | MutableMapping | None

type TypeScalar[T= TypeAllTypes] = Scalar[T]

type TypeFieldType = ExplicitField | ImplicitField

type TypeField = Field

type TypeBaseType = BaseType

type TypeExplicitField = ExplicitField

type TypeImplicitField = ImplicitField

type TypeBaseOptions = BaseOptions

type TypeResolver[T = TypeAllTypes] = Callable[[str, TypeAllTypes, GraphQLResolveInfo, dict[str, Any]], T]

type TypeObjectType = ObjectType

type TypeInterface = Interface

type TypeSchema = Schema

type TypeArgument = Argument

type TypeGrapheneTypes = Type[TypeObjectType |
                              TypeInterface | TypeScalar | TypeArgument]

type TypeMapping[T] = MutableMapping[str, T]

type TypeGraphqlExecuteOptions = str | bool | Source | GraphQLFieldResolver | GraphQLTypeResolver | type[
    ExecutionContext] | Middleware | Mapping[str, Any]

type TypeGraphqlExecuteKwargs[T = TypeGraphqlExecuteOptions] = MutableMapping[str, T]

type TypeGraphqlExecuteArgs[T= TypeGraphqlExecuteOptions] = Sequence[T]

type TypeImports = TypeScalar | TypeArgument | TypeInterface | TypeObjectType | TypeFieldType | TypeSchema | Callable[
    ..., Any] | Any

type TypeGraphQlTypes = GraphQLInterfaceType | GraphQLObjectType | GraphQLObjectType | GraphQLScalarType


@runtime_checkable
class TypeDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]

    def __getattr__(self, name: str) -> TypeAllTypes: ...

    def as_dict(self) -> dict[str, TypeAllTypes]: ...

# class ScalarProtocol(Protocol):
#     is_scalar: ClassVar[bool]

#     @staticmethod
#     def parse_literal(node: ValueNode, variables: Optional[dict[str, Any]] = None):
#         ...

#     @staticmethod
#     def resolve_value(value: Any):
#         ...


# class A(ScalarProtocol):
#     pass
#     pass
#     pass
#     pass
