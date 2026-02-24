
from faker import Faker

from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import BigInteger, Boolean, Integer, String
from new_graphene.fields.interface import Interface
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.schema import Schema

faker = Faker()


def test_resolver(parent, info, _input):
    print(parent, info, _input)
    return _input


def create_test_schema(query: str = None, immediate: bool = True):
    class User(ObjectType):
        firstname = String(input=String())
        age = Integer(input=Integer())
        followers = BigInteger(input=BigInteger())
        is_active = Boolean(input=Boolean())

        def resolve_optional(self, info):
            print(info)
            return None

        def resolve_required(self, info, _input):
            print(info, _input)
            return _input

    class Query(ObjectType):
        user = Field(User)

        def resolve_user(root, info):
            return {
                'firstname': faker.first_name(),
                'age': faker.random_int(min=18, max=80),
                'followers': faker.random_int(min=1000, max=1000000),
                'is_active': faker.boolean()
            }

    schema = Schema(query=Query)

    if query is None:
        query = """
        query {
            user {
                firstname
                age
                followers
                isActive
            }
        }
        """

    if immediate:
        return schema.execute(query)

    return schema


def create_test_input_schema(query: str = None, immediate: bool = True):
    class User(ObjectType):
        firstname = String()

    class Query(ObjectType):
        user = Field(User, search=String())

        def resolve_user(root, info, search=None):
            print(search)
            return {
                'firstname': faker.first_name()
            }

    schema = Schema(query=Query)

    if query is None:
        query = """
        query {
            user(search: "John") {
                firstname
            }
        }
        """

    if immediate:
        return schema.execute(query)

    return schema


def create_test_interface_schema(query: str = None, immediate: bool = True):
    class UserInterface(Interface):
        age = Integer()

    class User(ObjectType):
        firstname = String()
        lastname = String()

        class Meta:
            interfaces = [UserInterface]

    class Query(ObjectType):
        user = Field(User)

        def resolve_user(root, info, search=None):
            print(search)
            return {
                'firstname': faker.first_name(),
                'lastname': faker.last_name(),
                'age': faker.random_int(min=18, max=80)
            }

    schema = Schema(query=Query)

    if query is None:
        query = """
        query {
            user {
                firstname
                age
            }
        }
        """

    if immediate:
        return schema.execute(query)

    return schema
