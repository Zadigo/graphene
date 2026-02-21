from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Mapping,
                    MutableMapping, Optional, Protocol, Sequence,
                    runtime_checkable)

from graphql import (ExecutionContext, GraphQLFieldResolver,
                     GraphQLResolveInfo, GraphQLTypeResolver, Middleware,
                     Source, ValueNode)

if TYPE_CHECKING:
    from new_graphene.fields.arguments import Argument
    from new_graphene.fields.datatypes import Scalar
    from new_graphene.fields.helpers import ExplicitField, ImplicitField
    from new_graphene.fields.interface import Interface
    from new_graphene.fields.objecttypes import ObjectType
    from new_graphene.schema import Schema

type TypeAllTypes = str | int | float | bool | Sequence | MutableMapping | None

type TypeScalar[T= TypeAllTypes] = Scalar[T]

type TypeField = ExplicitField | ImplicitField

type TypeExplicitField = ExplicitField

type TypeImplicitField = ImplicitField

type TypeResolver[T = TypeAllTypes] = Callable[[str, GraphQLResolveInfo, str], T]

type TypeObjectType = ObjectType

type TypeInterface = Interface

type TypeSchema = Schema

type TypeArgument = Argument

type TypeMapping[T] = MutableMapping[str, T]

type TypeGraphqlExecuteOptions = str | bool | Source | GraphQLFieldResolver | GraphQLTypeResolver | type[
    ExecutionContext] | Middleware | Mapping[str, Any]

type TypeGraphqlExecuteKwargs[T = TypeGraphqlExecuteOptions] = MutableMapping[str, T]

type TypeGraphqlExecuteArgs[T= TypeGraphqlExecuteOptions] = Sequence[T]

type TypeImports = TypeScalar | TypeArgument | TypeInterface | TypeObjectType | TypeField | TypeSchema | Callable[
    ..., Any] | Any


@runtime_checkable
class TypeDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]


class ScalarProtocol(Protocol):
    is_scalar: ClassVar[bool]

    @staticmethod
    def parse_literal(node: ValueNode, variables: Optional[dict[str, Any]] = None):
        ...

    @staticmethod
    def resolve_value(value: Any):
        ...


class A(ScalarProtocol):
    pass
