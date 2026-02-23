import functools
import inspect
from typing import Any, Callable, Optional, Sequence, Type

from graphql import (GraphQLArgument, GraphQLBoolean, GraphQLField,
                     GraphQLFloat, GraphQLID, GraphQLInputField, GraphQLInt,
                     GraphQLNamedType, GraphQLObjectType, GraphQLResolveInfo,
                     GraphQLSchema, GraphQLString, get_introspection_query)
from graphql import graphql as agraphql
from graphql import graphql_sync

from new_graphene.exceptions import GrapheneObjectTypeError
# from new_graphene.fields.datatypes import ID, Float, Integer, Scalar, String
from new_graphene.fields.datatypes import Scalar
from new_graphene.fields.dynamic import Dynamic
from new_graphene.fields.interface import Interface
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.resolvers import default_resolver
from new_graphene.grapqltypes import (GrapheneGraphqlObjectType,
                                      GrapheneGraphqlScalarType)
from new_graphene.typings import (TypeAllTypes, TypeGrapheneTypes,
                                  TypeGraphqlExecuteOptions, TypeGraphQlTypes,
                                  TypeObjectType, TypeResolver, TypeScalar)
from new_graphene.utils.base import get_unbound_function
from new_graphene.utils.printing import PrintingMixin


def resolve_for_subscription(root, info: GraphQLResolveInfo, **arguments):
    return root


class TypesContainer(dict):
    """A container for the types defined in the schema. This class is responsible 
    for managing the types and ensuring that they are properly translated to their GraphQL 
    counterparts when the schema is generated. It also provides methods for adding types to the
    container and retrieving them as needed.

    Args:
        query (Type[TypeObjectType], optional): The root query type for the schema. Defaults to None.
        mutation (Type[TypeObjectType], optional): The root mutation type for the schema. Defaults to None.
        subscription (Type[TypeObjectType], optional): The root subscription type for the schema. Defaults to None.
        types (Sequence[Type[TypeObjectType]], optional): A list of additional types used in the schema. Defaults to None.
        auto_camelcase (bool, optional): Whether to automatically convert field names to camel case. Defaults to True.
    """

    def __init__(self, query: Optional[Type[TypeObjectType]] = None, mutation: Optional[Type[TypeObjectType]] = None, subscription: Optional[Type[TypeObjectType]] = None, types: Optional[Sequence[Type[TypeObjectType]]] = None, auto_camelcase: bool = True):
        self.auto_camelcase = auto_camelcase

        _query = self._check_is_type_class(query)
        _mutation = self._check_is_type_class(mutation)
        _subscription = self._check_is_type_class(subscription)

        self.query = self.add_to_self(_query)
        self.mutation = self.add_to_self(_mutation)
        self.subscription = self.add_to_self(_subscription)

        self._check_types(types)
        self.types = types or []

    def _get_name(self, name: str) -> str:
        # if self.auto_camelcase:
        #     return ''.join(word.capitalize() for word in name.split('_'))
        return name

    def _check_types(self, value: Any):
        pass

    def _check_is_type_class(self, value: Any) -> Optional[Type[TypeObjectType]]:
        if value is None:
            return value

        result = any([
            inspect.isclass(value) and issubclass(value, ObjectType),
            isinstance(value, GraphQLObjectType)
        ])

        if not result:
            raise GrapheneObjectTypeError(value)

        return value

    def _get_field_resolver(self, graphene_type: TypeObjectType, func_name: str, field_name: str, default_value: TypeAllTypes):
        """Searches the resolve for the field on the ObjectTypes and
        interfaces implemented by the ObjectType. The search is done in the following order:
        1. The ObjectType itself
        2. The interfaces implemented by the ObjectType

        .. code-block:: python
            from new_graphene import ObjectType, String

            class User(ObjectType):
                name = String()

                def resolve_name(self, info): # This is the resolver for 'name'
                    return "John Doe"
        """
        if not issubclass(graphene_type, ObjectType):
            return None

        resolver = getattr(graphene_type, func_name, None)

        if resolver is None:
            interface_resolver = None
            for interface in graphene_type._meta.interfaces:
                if field_name not in interface._meta.fields:
                    continue

                interface_resolver = getattr(interface, func_name, None)
                if interface_resolver is not None:
                    break
            resolver = interface_resolver

        if resolver is not None:
            return get_unbound_function(resolver)

        return None

    # create_fields_for_type
    def _translate_fields(self, graphene_type: Type[TypeObjectType], is_input_field: bool = False):
        """Translates the fields of a Graphene ObjectType to GraphQL fields. 
        This involves iterating over the fields defined in the Graphene ObjectType, 
        building the corresponding GraphQL field definitions, and handling any 
        necessary conversions or mappings between the two representations. 
        The resulting GraphQL fields are then returned as a dictionary that can be 
        used to construct the GraphQL schema.

        The resolvers for the fields are also wrapped to ensure that they are properly 
        integrated with the GraphQL execution process. This may involve handling 
        default resolvers, subscription resolvers, and any custom resolvers defined by the user.
        """

        _final_fields: dict[str, GraphQLField] = {}

        if graphene_type._meta is None:
            raise TypeError(f"Expected {graphene_type} to have a Meta class.")

        for name, field_obj in graphene_type._meta.fields.items():
            if isinstance(field_obj, Dynamic):
                pass

            input_or_output_type = self.add_to_self(field_obj.field_type)

            if is_input_field:
                _final_field = GraphQLInputField(
                    input_or_output_type,
                    description=field_obj.description,
                    default_value=field_obj.default_value,
                    deprecation_reason=field_obj.deprecation_reason
                )
            else:
                # Build the field arguments
                # e.g. name(search: String)
                built_args = {}
                for name, arg in field_obj._arguments.items():
                    created_type = self.add_to_self(arg.field_type)
                    arg_name = arg.name or self.get_name(name)
                    built_args[arg_name] = GraphQLArgument(
                        created_type,
                        # description=arg.description,
                        default_value=arg.default_value,
                        deprecation_reason=arg.deprecation_reason,
                    )

                # 1. Obtain the resolver for subscription
                func_resolver = self._get_field_resolver(
                    graphene_type,
                    f"subscribe_{name}",
                    name,
                    field_obj.default_value
                )

                subscribe = field_obj.wrap_subscribe(func_resolver)

                # 2. Obtain the resolver for the field
                field_default_resolver: TypeResolver = None
                # In suscription, use the identity resolver by default
                if subscribe is not None:
                    field_default_resolver = resolve_for_subscription

                if issubclass(graphene_type, ObjectType):
                    _resolver = graphene_type._meta.default_resolver or default_resolver()
                    field_default_resolver = functools.partial(
                        _resolver, name, field_obj.default_value
                    )

                func_resolver = self._get_field_resolver(
                    graphene_type,
                    f"resolve_{name}",
                    name,
                    field_obj.default_value
                )
                partial_resolver = field_obj.wrap_resolve(
                    func_resolver or field_default_resolver
                )

                _final_field = GraphQLField(
                    input_or_output_type,
                    args=built_args,
                    resolve=partial_resolver,
                    subscribe=subscribe,
                    description=field_obj.description,
                    deprecation_reason=field_obj.deprecation_reason
                )

            field_name = field_obj.name or self._get_name(name)
            _final_fields[field_name] = _final_field

        return _final_fields

    def _resolve_type(self, resolve_type_func, type_name, root, info, _type):
        pass

    def get(self, key: str, default: Any = None) -> Optional[TypeGraphQlTypes]:
        return super().get(key, default)

    def items(self) -> Sequence[tuple[str, TypeGraphQlTypes]]:
        return tuple(super().items())

    def update(self, **kwargs: TypeGraphQlTypes) -> None:
        return super().update(**kwargs)

    def pop(self, key: str, default: Optional[TypeGraphQlTypes] = None) -> Optional[TypeGraphQlTypes]:
        return super().pop(key, default)

    def values(self) -> Sequence[TypeGraphQlTypes]:
        return tuple(super().values())

    def fromkeys(cls, iterable: Sequence[str], value: TypeGraphQlTypes) -> dict[str, TypeGraphQlTypes]:
        return super().fromkeys(iterable, value)

    def add_to_self(self, graphene_type: TypeGrapheneTypes | Callable[..., TypeGrapheneTypes] | None):
        """Checks the Graphene internal type against the existing fields in the container
        and then translates it to the corresponding GraphQL type if it is not already present.
        """
        if graphene_type is None:
            return graphene_type

        if inspect.isfunction(graphene_type):
            return graphene_type()

        name = getattr(graphene_type._meta, 'name', None)
        if name is None:
            raise ValueError(f"Expected {graphene_type} to have a name.")

        graphql_type = self.get(name)
        if graphql_type is not None:
            return graphql_type

        if issubclass(graphene_type, Scalar):
            graphql_type = self.translate_scalar(graphene_type)
        elif issubclass(graphene_type, ObjectType):
            graphql_type = self.translate_objecttype(graphene_type)
        elif issubclass(graphene_type, Interface):
            graphene_type = None
        # elif issubclass(graphene_type, Union):
        #     pass
        # elif issubclass(graphene_type, Enum):
        #     pass
        # elif issubclass(graphene_type, InputObjectType):
        #     pass

        if graphql_type is None:
            raise ValueError(
                f"Expected {graphene_type} to be a "
                "valid Graphene type."
            )

        self[name] = graphql_type
        return graphql_type

    def translate_scalar(self, value: Type[TypeScalar]):
        scalars: dict[TypeScalar, GraphQLNamedType] = {
            'String': GraphQLString,
            'Integer': GraphQLInt,
            'Float': GraphQLFloat,
            'Boolean': GraphQLBoolean,
            'ID': GraphQLID
        }

        # TODO: Use "value.internal_type.value"
        if value._meta._class_name in scalars:
            return scalars[value._meta._class_name]

        serialize = getattr(value, 'serialize', None)
        parse_value = getattr(value, 'parse_value', None)
        parse_literal = getattr(value, 'parse_literal', None)

        return GrapheneGraphqlScalarType(
            value._meta.name,
            value,
            serialize=serialize,
            parse_value=parse_value,
            parse_literal=parse_literal,
            description=value._meta.description,
            extensions=None
        )

    def translate_objecttype(self, graphene_type: Type[TypeObjectType]):
        def interfaces():
            interfaces = []
            for interface in graphene_type._meta.interfaces:
                interfaces.append(self.add_to_self(interface))
            return interfaces

        fields = self._translate_fields(graphene_type)
        return GrapheneGraphqlObjectType(
            graphene_type._meta.name,
            graphene_type,
            fields=fields,
            interfaces=interfaces,
            is_type_of=None,
            extensions=None,
            description=graphene_type._meta.description
        )

    def translate_union(self, graphene_type: TypeObjectType):
        pass

    def translate_interface(self, graphene_type: TypeObjectType):
        pass

    def translate_enum(self, graphene_type: TypeObjectType):
        pass


class Schema(PrintingMixin):
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
        query (Type[TypeObjectType], optional): The root query type for the schema. Defaults to None.
        mutation (Type[TypeObjectType], optional): The root mutation type for the schema. Defaults to None.
        subscription (Type[TypeObjectType], optional): The root subscription type for the schema. Defaults to None.
        types (Sequence[Type[TypeObjectType]], optional): A list of additional types used in the schema. Defaults to None.
        directives (Sequence, optional): A list of directives used in the schema. Defaults to None. 
        auto_camelcase (bool, optional): Whether to automatically convert field names to camel case. Defaults to True.
    """

    def __init__(self, query: Optional[Type[TypeObjectType]] = None, mutation: Optional[Type[TypeObjectType]] = None, subscription: Optional[Type[TypeObjectType]] = None, types: Optional[Sequence[Type[TypeObjectType]]] = None, directives: Optional[Sequence] = None, auto_camelcase: bool = True):
        self.query = query
        self.mutation = mutation
        self.subscription = subscription
        self.types = types or []
        self.auto_camelcase = auto_camelcase

        self._types_container = TypesContainer(
            query=query,
            mutation=mutation,
            subscription=subscription,
            types=types,
            auto_camelcase=auto_camelcase
        )

        self.graphql_schema = GraphQLSchema(
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
        """Performs an introspection query against the schema to 
        retrieve information about the types, fields, and other 
        elements defined in the GraphQL schema. This method is 
        useful for tools that need to understand the structure of 
        the schema, such as GraphQL clients or documentation 
        generators. The introspection query is a special GraphQL 
        query that is designed to return metadata about the schema itself, 
        allowing clients to dynamically discover the capabilities of the API."""
        result = self.execute(get_introspection_query())
        if result.errors:
            raise Exception(
                "Introspection query failed with "
                f"errors: {result.errors}"
            )
        return result.data

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
        return graphql_sync(self.graphql_schema, *args, **normalized_kwargs)

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
        return agraphql(self.graphql_schema, *args, **normalized_kwargs)

    def asubscribe(self, query, *args, **kwargs):
        pass
