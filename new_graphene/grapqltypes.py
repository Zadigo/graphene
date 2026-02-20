from graphql import GraphQLObjectType, GraphQLScalarType


class GrapheneGraphQlTypeMixin:
    pass


class GrapheneGraphqlObjectType(GrapheneGraphQlTypeMixin, GraphQLObjectType):
    pass


class GrapheneGraphqlScalarType(GrapheneGraphQlTypeMixin, GraphQLScalarType):
    pass
