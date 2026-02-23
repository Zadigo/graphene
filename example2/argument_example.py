from faker import Faker
from graphql import GraphQLResolveInfo

from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import Integer, String
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.schema import Schema

faker = Faker()


class User(ObjectType):
    firstname = String()
    lastname = String()
    age = Integer()


class Query(ObjectType):
    users = Field(User, search=String())

    def resolve_users(root, info: GraphQLResolveInfo, search: str = None):
        return {
            'firstname': faker.first_name(),
            'lastname': faker.last_name(),
            'age': faker.random_int(min=18, max=80),
        }


schema = Schema(query=Query)

query = """
    query {
      users(search: "Pauline") {
        id
        firstname
        age
      }
    }
"""


def test_query():
    result = schema.execute(query)
    assert not result.errors
    assert result.data == {'user': {'id': '1', 'name': 'Pauline', 'age': 27}}


if __name__ == "__main__":
    result = schema.execute(query)
    print(schema._types_container)
    print(result)
    # print(result.data["user"])
