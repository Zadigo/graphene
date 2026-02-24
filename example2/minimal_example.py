from faker import Faker
from graphql import GraphQLResolveInfo

from new_graphene.fields.base import Field
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.scalars import String
from new_graphene.schema import Schema

faker = Faker()


class User(ObjectType):
    name = String()


class Query(ObjectType):
    users = Field(User)

    def resolve_users(root, info: GraphQLResolveInfo):
        return {'name': faker.name()}


if __name__ == "__main__":
    s = Schema(query=Query)
    result = s.execute('{ users { name } }')
    print(result)
