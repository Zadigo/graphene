import unittest

from graphql import GraphQLObjectType

from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import String
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
        self.assertIsNone(schema._graphql_schema)

    def test_schema_with_types(self):
        schema = Schema(query=Query)
        self.assertIsNone(schema._graphql_schema)

        self.assertIsInstance(
            schema.graphql_schema.query_type,
            GraphQLObjectType
        )

        self.assertEqual(
            schema.graphql_schema.query_type.name,
            'Query'
        )

        if schema.graphql_schema.query_type is None:
            self.fail("Query type is None")

    def test_schema_with_custom_field_type(self):
        class UserDetails(ObjectType):
            firstname = String()

        class User(ObjectType):
            details = Field(UserDetails)

            def resolve_details(self, info):
                return {'firstname': 'John'}

        schema = Schema(query=User)
        result = schema.execute("""query { details { firstname } }""")
        print(result)
