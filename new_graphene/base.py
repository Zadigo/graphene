class BaseOptions:
    def __init__(self, cls: type['BaseTypeMetaclass'], **kwargs):
        self.cls = cls
        self.name: str = None
        self.description: str = None


class BaseObjectType(type):
    def __new__(cls, name: str, bases: tuple, namespace: dict, /, **kwds):
        klass = super().__new__(cls, name, bases, namespace, **kwds)

        if not bases:
            return klass

        if not hasattr(klass, '_meta'):
            return klass

        setattr(klass, '_meta', BaseOptions(cls=klass))
        return klass


class BaseTypeMetaclass(metaclass=BaseObjectType):
    _meta: BaseOptions = None


class BaseType(BaseTypeMetaclass):
    @classmethod
    def create(cls, name: str, **kwargs):
        pass

    def prepare(self):
        pass
