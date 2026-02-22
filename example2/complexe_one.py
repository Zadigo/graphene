from graphene.types.field import Field
from graphene.types.interface import Interface
from graphene.types.objecttype import ObjectType
from graphene.types.scalars import Int, String


class QuickInterface(Interface):
    firstname = Field(String)
    lastname = String()
    age = Int()

    def resolve_firstname(self, info):
        return "John"


class SimpleObjectType(ObjectType):
    name = String()

    class Meta:
        interfaces = [QuickInterface]


instance = SimpleObjectType()
print(instance._meta.interfaces)
