from graphene.types import Argument, Field, ObjectType, String
from graphene.types.schema import Schema


class Google(ObjectType):
    name = Field(String, args={'search': Argument(String)})

    def resolve_name(root, info, search=None):
        if search:
            return f"Google search: {search}"
        return "Google"


s = Schema(query=Google)
result = s.execute('{ name(search: "Graphene") }')
print(result)
