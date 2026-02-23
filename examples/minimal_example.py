from faker import Faker
from graphql import GraphQLResolveInfo

from graphene import Boolean, Field, ObjectType, Schema, String

faker = Faker()


class User(ObjectType):
    name = String()


class Query(ObjectType):
    users = Field(User)
    is_queryset = Boolean()

    def resolve_users(root, info: GraphQLResolveInfo):
        return {'name': faker.name()}

    def resolve_is_queryset(root, info: GraphQLResolveInfo):
        return True


if __name__ == "__main__":
    s = Schema(query=Query)
    result = s.execute('{ users { name } }')
    print(result)
