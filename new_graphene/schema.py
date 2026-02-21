import functools
import inspect
from typing import Any, Optional, Sequence
from xmlrpc.client import Boolean

from graphql import (GraphQLArgument, GraphQLBoolean, GraphQLField,
                     GraphQLFloat, GraphQLID, GraphQLInputField, GraphQLInt,
                     GraphQLObjectType, GraphQLScalarLiteralParser,
                     GraphQLScalarType, GraphQLScalarValueParser,
                     GraphQLSchema, GraphQLString)
from graphql import graphql as agraphql
from graphql import graphql_sync

from new_graphene.exceptions import GrapheneObjectTypeError
from new_graphene.fields.datatypes import ID, Float, Integer, Scalar, String
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.resolvers import default_resolver
from new_graphene.grapqltypes import (GrapheneGraphqlObjectType,
                                      GrapheneGraphqlScalarType)
from new_graphene.typings import (TypeGraphqlExecuteOptions, TypeObjectType,
                                  TypeScalar)
from new_graphene.utils import TypesPrinterMixin


def resolve_for_subscription(root, info, **arguments):
    return root


class TypesContainer(dict):
    """A container for the types defined in the schema. This class is responsible 
    for managing the types and ensuring that they are properly translated to their GraphQL 
    counterparts when the schema is generated. It also provides methods for adding types to the
    container and retrieving them as needed.

    Args:
        query (TypeObjectType, optional): The root query type for the schema. Defaults to None.
        mutation (TypeObjectType, optional): The root mutation type for the schema. Defaults to None.
        subscription (TypeObjectType, optional): The root subscription type for the schema. Defaults to None.
        types (Sequence[TypeObjectType], optional): A list of additional types used in the schema. Defaults to None.
        auto_camelcase (bool, optional): Whether to automatically convert field names to camel case. Defaults to True.
    """

    def __init__(self, query: Optional[TypeObjectType] = None, mutation: Optional[TypeObjectType] = None, subscription: Optional[TypeObjectType] = None, types: Optional[Sequence[TypeObjectType]] = None, auto_camelcase: bool = True):
        _query = self._check_type(query)
        _mutation = self._check_type(mutation)
        _subscription = self._check_type(subscription)

        self.query = self.add_to_self(_query)
        self.mutation = self.add_to_self(_mutation)
        self.subscription = self.add_to_self(_subscription)

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

    def _get_function_for_type(self, value: TypeObjectType):
        pass

    # create_fields_for_type
    def _translate_fields_to_graphql(self, graphene_type: TypeObjectType, is_input_field: bool = False):
        """Translates the fields of a Graphene ObjectType to GraphQL fields. 
        This involves iterating over the fields defined in the Graphene ObjectType, 
        building the corresponding GraphQL field definitions, and handling any 
        necessary conversions or mappings between the two representations. 
        The resulting GraphQL fields are then returned as a dictionary that can be 
        used to construct the GraphQL schema.

        The resolvers for the fields are also wrapped to ensure that they are properly 
        integrated with the GraphQL execution process. This may involve handling 
        default resolvers, subscription resolvers, and any custom resolvers defined by the user.

        .. code-block:: python
            from new_graphene import ObjectType, String

            class User(ObjectType):
                name = String()

                def resolve_name(self, info):
                    return "John Doe"
        """

        _final_fields: dict[str, GraphQLField] = {}

        for name, field_obj in graphene_type._meta.fields.items():
            # if isinstance(value, Dynamic):
            #     pass

            field_type = self.add_to_self(field_obj.field_type)

            if is_input_field:
                _final_field = GraphQLInputField(
                    field_type,
                    description=field_obj.description,
                    default_value=field_obj.default_value,
                    deprecation_reason=field_obj.deprecation_reason
                )
            else:
                # Build the GraphQl args
                built_args = {}
                for name, arg in field_obj.args.items():
                    created_type = self.add_to_self(arg.field_type)
                    arg_name = arg.name or self.get_name(name)
                    built_args[arg_name] = GraphQLArgument(
                        created_type,
                        description=arg.description,
                        default_value=arg.default_value,
                        deprecation_reason=arg.deprecation_reason,
                    )

                subscribe = field_obj.wrap_subscribe(
                    self._get_function_for_type(
                        graphene_type,
                        f"subscribe_{name}",
                        name,
                        field_obj.default_value
                    )
                )

                default_field_resolver = resolve_for_subscription if subscribe else None

                field_default_resolver = None
                if issubclass(graphene_type, ObjectType):
                    _resolver = graphene_type._meta.default_resolver or default_resolver()
                    field_default_resolver = functools.partial(
                        _resolver, name, field_obj.default_value
                    )

                partial_resolver = field_obj.wrap_resolve(
                    self._get_function_for_type(
                        graphene_type,
                        f"resolve_{name}",
                        name,
                        field_obj.default_value
                    ) or field_default_resolver
                )

                _final_field = GraphQLField(
                    field_type,
                    args=built_args,
                    resolve=partial_resolver,
                    subscribe=subscribe,
                    description=field_obj.description,
                    deprecation_reason=field_obj.deprecation_reason
                )

            field_name = field_obj.name or self.get_name(name)
            _final_fields[field_name] = _final_field

        return _final_fields

    def _resolve_type(self, resolve_type_func, type_name, root, info, _type):
        pass

    def add_to_self(self, value: TypeObjectType | None) -> Optional[TypeObjectType]:
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
            grapql_type = self.translate_scalar_to_grapql(value)
        elif issubclass(value, ObjectType):
            grapql_type = self.translate_objecttype_to_grapql(value)
        else:
            raise GrapheneObjectTypeError(value)

        self[name] = value
        return value

    def translate_scalar_to_grapql(self, value: TypeScalar):
        scalars: dict[TypeScalar, GraphQLScalarType] = {
            String: GraphQLString,
            Integer: GraphQLInt,
            Float: GraphQLFloat,
            Boolean: GraphQLBoolean,
            ID: GraphQLID
        }

        if value in scalars:
            return scalars[value]

        parse_value: GraphQLScalarValueParser = getattr(
            value,
            'parse_value',
            None
        )

        parse_literal: GraphQLScalarLiteralParser = getattr(
            value,
            'parse_literal',
            None
        )

        return GrapheneGraphqlScalarType(
            value,
            description=value._meta.description,
            serialize=parse_value,
            parse_value=parse_value,
            parse_literal=parse_literal
        )

    def translate_objecttype_to_grapql(self, graphene_type: TypeObjectType):
        def interfaces():
            return []

        return GrapheneGraphqlObjectType(
            graphene_type._meta.name,
            self._translate_fields_to_graphql(graphene_type),
            interfaces=interfaces,
            is_type_of=None,
            description=graphene_type._meta.description
        )

    def translate_union_to_grapql(self, graphene_type: TypeObjectType):
        pass

    def translate_interface_to_grapql(self, graphene_type: TypeObjectType):
        pass

    def translate_enum_to_grapql(self, graphene_type: TypeObjectType):
        pass


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
        directives (Sequence, optional): A list of directives used in the schema. Defaults to None. 
        auto_camelcase (bool, optional): Whether to automatically convert field names to camel case. Defaults to True.
    """

    def __init__(self, query: Optional[TypeObjectType] = None, mutation: Optional[TypeObjectType] = None, subscription: Optional[TypeObjectType] = None, types: Optional[Sequence[TypeObjectType]] = None, directives: Optional[Sequence] = None, auto_camelcase: bool = True):
        self.query = query
        self.mutation = mutation
        self.subscription = subscription
        self.types = types or []
        self.auto_camelcase = auto_camelcase
        self._types_container: TypesContainer = TypesContainer(
            query=query,
            mutation=mutation,
            subscription=subscription,
            types=types,
            auto_camelcase=auto_camelcase
        )
        self._graphql_schema = GraphQLSchema(
            query=self._types_container.query,
            mutation=self._types_container.mutation,
            subscription=self._types_container.subscription,
            types=self._types_container.types,
            directives=directives
        )

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
    