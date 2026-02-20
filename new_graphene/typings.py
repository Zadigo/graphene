from typing import TYPE_CHECKING, Mapping, Sequence

if TYPE_CHECKING:
    from new_graphene.fields.datatypes import Scalar
    from new_graphene.fields.helpers import ExplicitField, ImplicitField

type TypeAllTypes = str | int | float | bool | Sequence | Mapping | None

type TypeScalar[T= TypeAllTypes] = Scalar[T]

type TypeField = ExplicitField | ImplicitField

type TypeExplicitField = ExplicitField
