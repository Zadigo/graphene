from faker import Faker

import graphene
from graphene.types.field import Field
from graphene.types.interface import Interface
from graphene.types.objecttype import ObjectType
from graphene.types.scalars import Int, String

faker = Faker()


class QuickInterface(Interface):
    firstname = Field(String)
    lastname = String()
    age = String()


class User(ObjectType):
    firstname = String()
    lastname = String()
    age = Int()

    def resolve_age(self, info):
        print(self.age)
        return self.age


class Query(ObjectType):
    users = Field(User, search=String())

    # class Meta:
    #     interfaces = [QuickInterface]

    def resolve_users(self, info, search=None):
        return User(firstname=faker.first_name(), lastname=faker.last_name(), age=faker.random_int(min=18, max=80))


schema = graphene.Schema(query=Query)
result = schema.execute(
    '''
    query {
        users(search: "Jane") {
            firstname
            lastname
            age
        }
    }
    '''
)
print(schema.type_map)
print(result)
