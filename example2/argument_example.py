from faker import Faker
from graphql import GraphQLResolveInfo

from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import ID, Integer, String
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.schema import Schema

faker = Faker()


class User(ObjectType):
    id = ID()
    firstname = String(search=String)
    age = Integer()


class Query(ObjectType):
    user = Field(User)

    def resolve_user(root, info: GraphQLResolveInfo, search: str):
        return {
            'id': faker.random_int(min=1, max=100),
            'firstname': faker.first_name(),
            'age': faker.random_int(min=18, max=80)
        }


schema = Schema(query=Query)

query = """
    query something {
      user(search: "Pauline") {
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
    print(result)
    # print(result.data["user"])
