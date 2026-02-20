from typing import Sequence
from dataclasses import make_dataclass, field


class BaseOptions:
    def __init__(self, cls: type['BaseTypeMetaclass'], **kwargs):
        self.cls = cls
        self.name: str = None
        self.description: str = None

        self.fields: Sequence = []
        self.interfaces: Sequence = []


class BaseObjectType(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict, /, **kwds):
        klass = super().__new__(cls, name, bases, namespace, **kwds)

        if not bases:
            return klass

        if not hasattr(klass, '_meta'):
            return klass

        base_options = BaseOptions(cls=klass)
        setattr(klass, '_meta', base_options)

        if getattr(klass, 'is_object_type', False):
            pass
            # _fields = []
            # for key, field_value in base_options.fields.items():
            #     _fields.append(
            #         (
            #             key,
            #             'typing.Any',
            #             field(
            #                 default=field_value.default_value if isinstance(field_value, Field) else None
            #             )
            #         )
            #     )

        return klass


class BaseTypeMetaclass(metaclass=BaseObjectType):
    _meta: BaseOptions = None


class BaseType(BaseTypeMetaclass):
    is_object_type: bool = False

    @classmethod
    def create(cls, name: str, **kwargs):
        pass

    def prepare(self):
        pass
