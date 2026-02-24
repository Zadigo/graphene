from new_graphene.fields.arguments import Argument
from new_graphene.fields.base import Field
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.scalars import String
from new_graphene.schema import Schema

# instance = Field(String, search=String())
# print(instance)


class Person(ObjectType):
    # search must be an instance
    name = Field(String, search=Argument(String))

    def resolve_name(self, info, search=None):
        print(search)
        return 'Alice'


person = Person()
d = person(name='Alice')
s = Schema(query=Person)
print(d.name)
print(person._meta.fields['name'].extra_args)
print(s.execute('query { name }'))
