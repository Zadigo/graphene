import inspect
from typing import Any, Optional, Sequence

from graphql import (GraphQLBoolean, GraphQLFloat, GraphQLID, GraphQLInt,
                     GraphQLObjectType, GraphQLScalarType, GraphQLSchema,
                     GraphQLString)
from graphql import graphql as agraphql
from graphql import graphql_sync

from new_graphene.exceptions import GrapheneObjectTypeError
from new_graphene.fields.datatypes import (ID, Boolean, Float, Integer, Scalar,
                                           String)
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.grapqltypes import (GrapheneGraphqlObjectType,
                                      GrapheneGraphqlScalarType)
from new_graphene.typings import (TypeGraphqlExecuteOptions, TypeObjectType,
                                  TypeScalar)
from new_graphene.utils import TypesPrinterMixin


class TypesContainer(dict):
    def __init__(self, query: Optional[TypeObjectType] = None, mutation: Optional[TypeObjectType] = None, subscription: Optional[TypeObjectType] = None, types: Optional[Sequence[TypeObjectType]] = None, auto_camelcase: bool = True):
        _query = self._check_type(query)
        _mutation = self._check_type(mutation)
        _subscription = self._check_type(subscription)

        self.query = self.new(_query)
        self.mutation = self.new(_mutation)
        self.subscription = self.new(_subscription)

        self._check_types(types)
        self.types = types or []

        self.auto_camelcase = auto_camelcase

    def _check_types(self, value: Any):
        pass

    def _check_type(self, value: Any) -> Optional[TypeObjectType]:
        if value is None:
            return value

        result = any([
            inspect.isclass(value) and issubclass(value, ObjectType),
            isinstance(value, GraphQLObjectType)
        ])

        if not result:
            raise GrapheneObjectTypeError(value)

        return value

    def new(self, value: TypeObjectType | None) -> Optional[TypeObjectType]:
        if value is None:
            return value

        if inspect.isfunction(value):
            return value()

        name = getattr(value._meta, 'name', None)
        if name is None:
            raise GrapheneObjectTypeError(value)

        result = self.get(name)
        if result is not None:
            return result

        if issubclass(value, Scalar):
            grapql_type = self.translate_to_grapql_scalar(value)
        elif issubclass(value, ObjectType):
            pass
        else:
            raise GrapheneObjectTypeError(value)

        self[name] = value
        return value

    def translate_to_grapql_scalar(self, value: TypeScalar):
        scalars: dict[TypeScalar, GraphQLScalarType] = {
            String: GraphQLString,
            Integer: GraphQLInt,
            Float: GraphQLFloat,
            Boolean: GraphQLBoolean,
            ID: GraphQLID
        }

        if value in scalars:
            return scalars[value]

        parse_value = getattr(value, 'parse_value', None)
        parse_literal = getattr(value, 'parse_literal', None)

        return GrapheneGraphqlScalarType(
            value,
            description=value._meta.description,
            serialize=parse_value,
            parse_value=parse_value,
            parse_literal=parse_literal
        )
    
    def translate_to_grapql_objecttype(self, graphene_type: TypeObjectType):
        return GrapheneGraphqlObjectType(
            graphene_type,
            [],
            name=graphene_type._meta.name,
            description=graphene_type._meta.description
        )


class Schema(TypesPrinterMixin):
    """A schema can be defined as a class that contains the root types
    for the GraphQL schema, such as query, mutation, and subscription. It also can contain
    a list of additional types that are used in the schema. The Schema class is responsible
    for defining the structure of the GraphQL API and how it will be executed.

    A schema is typically defined by creating a class that inherits from the Schema class and
    defining the root types as class attributes. For example:

    .. code-block:: python
        from new_graphene import Schema, ObjectType, String

        class Query(ObjectType):
            hello = String()

        schema = Schema(query=Query)

    Args:
        query (TypeObjectType, optional): The root query type for the schema. Defaults to None.
        mutation (TypeObjectType, optional): The root mutation type for the schema. Defaults to None.
        subscription (TypeObjectType, optional): The root subscription type for the schema. Defaults to None.
        types (Sequence[TypeObjectType], optional): A list of additional types used in the schema. Defaults to None.
        auto_camelcase (bool, optional): Whether to automatically convert field names to camel case. Defaults to True.
    """

    def __init__(self, query: Optional[TypeObjectType] = None, mutation: Optional[TypeObjectType] = None, subscription: Optional[TypeObjectType] = None, types: Optional[Sequence[TypeObjectType]] = None, auto_camelcase: bool = True):
        self.query = query
        self.mutation = mutation
        self.subscription = subscription
        self.types = types or []
        self.auto_camelcase = auto_camelcase
        self._types_container: TypesContainer = TypesContainer()
        self._graphql_schema = GraphQLSchema()

    def __str__(self) -> str:
        return self.print_schema(self)

    def __getattr__(self, name: str):
        pass

    def _normalize_kwargs(self, **kwargs: TypeGraphqlExecuteOptions):
        new_kwargs: dict[str, TypeGraphqlExecuteOptions] = {}

        values = [
            ('root', 'root_value'),
            ('context', 'context_value'),
            ('variables', 'variable_values'),
            ('operation_name', 'operation_name')
        ]

        for old_key, new_key in values:
            if old_key in kwargs:
                new_kwargs[new_key] = kwargs[old_key]
            elif new_key in kwargs:
                new_kwargs[new_key] = kwargs[new_key]

        return new_kwargs

    def to_lazy(self, item):
        return lambda: item

    def instrospect(self):
        pass

    def execute(self, *args: TypeGraphqlExecuteOptions, **kwargs: TypeGraphqlExecuteOptions):
        """Executes a GraphQL query against the schema.

        Args:
            *args: Positional arguments to be passed to the graphql_sync function.
            **kwargs: Keyword arguments to be passed to the graphql_sync function. These can include:
                - query: The GraphQL query string to execute.
                - variables: A dictionary of variables to be used in the query.
                - context: A value to be passed as the context to the resolvers.
                - root: A value to be passed as the root value to the resolvers.
                - operation_name: The name of the operation to execute (if the query contains multiple operations)
        """
        normalized_kwargs = self._normalize_kwargs(**kwargs)
        return graphql_sync(self._graphql_schema, *args, **normalized_kwargs)

    def aexecute(self, *args: TypeGraphqlExecuteOptions, **kwargs: TypeGraphqlExecuteOptions):
        """Asynchronous version of the execute method. 
        This method is intended to be used in an asynchronous context, such as with 
        an async web framework or in an async resolver. It allows for executing GraphQL 
        queries asynchronously, which can be beneficial for performance and scalability when dealing 
        with I/O-bound operations or long-running tasks.

        Args:
            *args: Positional arguments to be passed to the graphql_sync function.
            **kwargs: Keyword arguments to be passed to the graphql_sync function. These can include:
                - query: The GraphQL query string to execute.
                - variables: A dictionary of variables to be used in the query.
                - context: A value to be passed as the context to the resolvers.
                - root: A value to be passed as the root value to the resolvers.
                - operation_name: The name of the operation to execute (if the query contains multiple operations)
        """
        normalized_kwargs = self._normalize_kwargs(**kwargs)
        return agraphql(self._graphql_schema, *args, **normalized_kwargs)

    def asubscribe(self, query, *args, **kwargs):
        pass

    def asubscribe(self, query, *args, **kwargs):
        pass

    def asubscribe(self, query, *args, **kwargs):
        pass
