from faker import Faker
from graphql import GraphQLResolveInfo

from graphene import Field, ObjectType, Schema, String

faker = Faker()


class User(ObjectType):
    name = String()


class Query(ObjectType):
    users = Field(User, search=String())

    def resolve_users(root, info: GraphQLResolveInfo, search: str = None):
        return {'name': faker.name()}


if __name__ == "__main__":
    s = Schema(query=Query)
    # print(s.type_map.create_fields_for_type(Query))
    result = s.execute(
        """
        query {
            users(search: "John") {
                name
            }
        }
        """
    )
