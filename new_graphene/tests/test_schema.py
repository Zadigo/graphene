import unittest

from graphql import GraphQLObjectType

from new_graphene.fields.datatypes import String
from new_graphene.fields.helpers import Field
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.schema import Schema


class SimpleType(ObjectType):
    name = String()


class Query(ObjectType):
    simple = Field(SimpleType)


class TestSchema(unittest.TestCase):
    def test_schema_initialization(self):
        schema = Schema()
        self.assertIsInstance(schema, Schema)
        self.assertIsNotNone(schema._graphql_schema)

    def test_schema_with_types(self):
        schema = Schema(query=Query)
        self.assertIsNotNone(schema._graphql_schema)

        self.assertIsInstance(
            schema._graphql_schema.query_type,
            GraphQLObjectType
        )

        self.assertIsInstance(
            schema._graphql_schema.query_type.name,
            'Query'
        )

        if schema._graphql_schema.query_type is None:
            self.fail("Query type is None")

        self.assertIsInstance(
            schema._graphql_schema.query_type.graphene_type,
            Query
        )
