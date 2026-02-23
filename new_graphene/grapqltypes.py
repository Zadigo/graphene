from typing import Any

from graphql import (GraphQLEnumType, GraphQLInputObjectType,
                     GraphQLInterfaceType, GraphQLObjectType,
                     GraphQLScalarType)

from new_graphene.typings import TypeGraphQlTypes


class GrapheneGraphQlTypeMixin:
    def __init__(self, name: str, graphene_type: type[TypeGraphQlTypes], *args: Any, **kwargs: Any):
        self.graphene_type = graphene_type
        super().__init__(name, *args, **kwargs)


class GrapheneGraphqlObjectType(GrapheneGraphQlTypeMixin, GraphQLObjectType):
    """Extends GraphQLObjectType with the related graphene_type"""


class GrapheneGraphqlScalarType(GrapheneGraphQlTypeMixin, GraphQLScalarType):
    """Extends GraphQLScalarType with the related graphene_type"""


class GrapheneEnumType(GrapheneGraphQlTypeMixin, GraphQLEnumType):
    """Extends GraphQLEnumType with the related graphene_type"""


class GrapheneInputObjectType(GrapheneGraphQlTypeMixin, GraphQLInputObjectType):
    """Extends GraphQLInputObjectType with the related graphene_type"""


class GrapheneInterfaceType(GrapheneGraphQlTypeMixin, GraphQLInterfaceType):
    """Extends GraphQLInterfaceType with the related graphene_type"""
