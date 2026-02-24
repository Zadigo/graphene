import unittest

from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.scalars import String
from new_graphene.fields.structures import List
from new_graphene.schema import Schema


class TestStructures(unittest.TestCase):
    def test_list_structure(self):
        class User(ObjectType):
            name = String()

        class Query(ObjectType):
            users = List(User)

            def resolve_users(self, info):
                return [{'name': 'Alice'}, {'name': 'Bob'}]

        schema = Schema(query=Query)
        schema.execute("""query { users { name } }""")
