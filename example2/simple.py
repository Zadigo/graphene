from faker import Faker
from graphql import GraphQLResolveInfo

from new_graphene.fields.base import Field
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.scalars import ID, Integer, String
from new_graphene.schema import Schema

faker = Faker()


class Patron(ObjectType):
    id = ID()
    name = String()
    age = Integer()


class Query(ObjectType):
    patron = Field(Patron)

    def resolve_patron(root, info: GraphQLResolveInfo):
        # return Patron(id=1, name="Syrus", age=27)
        # return 'Google'
        # return root.dataclass_model(id=1, name="Syrus", age=27)
        print(root)
        return {
            'id': faker.random_int(min=1, max=100),
            'name': faker.name(),
            'age': faker.random_int(min=18, max=80)
        }


schema = Schema(query=Query)

query = """
    query something {
      patron {
        id
        name
        age
      }
    }
"""


def test_query():
    result = schema.execute(query)
    assert not result.errors
    assert result.data == {"patron": {"id": "1", "name": "Syrus", "age": 27}}


if __name__ == "__main__":
    result = schema.execute(query)
    print(result)
    print(result.data["patron"])
