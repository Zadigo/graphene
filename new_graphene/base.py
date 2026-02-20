from typing import Annotated, Any, Mapping, Optional, Sequence

from new_graphene.fields.helpers import get_field_as
from new_graphene.typings import TypeExplicitField, TypeField


class BaseOptions:
    def __init__(self, cls: type['BaseTypeMetaclass'], **kwargs):
        self.cls = cls
        self.name: str = None
        self.description: str = None

        self.fields: Mapping[str, TypeExplicitField] = {}
        self.interfaces: Sequence = []
        self.accepted_keys = {'name', 'description', 'interfaces', 'abstract'}
        self._user_meta: Optional[type] = None

    def check_meta_options(self, keys: Sequence[str]):
        """Checks if the provided keys in the Meta class are valid options.
        Raises an AttributeError if any invalid keys are found."""
        _keys = filter(lambda key: not key.startswith('__'), keys)
        invalid_keys = set(_keys) - self.accepted_keys
        if invalid_keys:
            raise AttributeError(
                f"Invalid meta options: {', '.join(invalid_keys)}")

    def set_meta_options(self, key: str, value: Any):
        """Sets the meta options based on the provided key and value."""
        if key in self.accepted_keys:
            setattr(self, key, value)

    def filter_fields(self, namespace: Mapping[str, Any] | Sequence[tuple[str, Any]]) -> Mapping[str, TypeField]:
        """Filters the fields from the provided namespace"""
        items = namespace.items() if isinstance(namespace, Mapping) else namespace

        iternal_keys = {'_meta', 'is_object_type'}
        user_defined_fields = {}

        for key, value in items:
            if key.startswith('_'):
                continue

            if key in iternal_keys:
                continue

            if key in user_defined_fields:
                # This means the field comes from a subclass and
                # is being overridden by the user, we should keep
                # the user defined field
                pass

            user_defined_fields[key] = value
        return user_defined_fields

    def build_fields(self, namespace: Mapping[str, Any] | Sequence[tuple[str, Any]]):
        """Builds the fields for the ObjectType based on the provided namespace"""
        user_defined_fields = self.filter_fields(namespace)

        for key, value in user_defined_fields.items():
            field = get_field_as(value)
            if field is not None:
                self.fields[key] = field


class BaseObjectType(type):
    def __new__(cls, name: str, bases: tuple[type], namespace: dict, /, **kwds):
        klass = super().__new__(cls, name, bases, namespace, **kwds)

        if not bases:
            return klass

        if not hasattr(klass, '_meta'):
            return klass

        base_options = BaseOptions(cls=klass)
        setattr(klass, '_meta', base_options)

        # Extract the Meta class from the namespace
        # and process its options
        user_meta: type | None = namespace.pop('Meta', None)
        if user_meta is not None:
            base_options._user_meta = user_meta

            keys = user_meta.__dict__.keys()
            base_options.check_meta_options(keys)
            for key, value in user_meta.__dict__.items():
                base_options.set_meta_options(key, value)

            for interface in getattr(user_meta, 'interfaces', []):
                continue
                # if not isinstance(interface, Interface):
                #     raise TypeError(
                #         f"Expected interface to be an instance of Interface, got {type(interface).__name__}")

        # Dynamically create a dataclass for ObjectTypes to hold the field values,
        # only if the class is marked as an ObjectType. This allows us to have a
        # structured way to store field values and automatically generate methods
        # like __init__, __eq__, and __repr__ for the ObjectType. The dataclass will b
        # e created with the name of the class and will inherit from any bases if necessary.
        # The fields for the dataclass will be determined based on the fields defined in the
        # BaseOptions, but only
        from new_graphene.fields.helpers import Field

        # if getattr(klass, 'is_object_type', False):
        #     _dataclass_fields = []
        #     for key, field_value in namespace.items():
        #         if key.startswith('_'):
        #             continue
        #         default_value = None
        #         if isinstance(field_value, Field):
        #             default_value = field_value.default_value
        #         _dataclass_fields.append(
        #             (
        #                 key,
        #                 'typing.Any',
        #                 field(default=default_value)
        #             )
        #         )
        #     # dataclass = make_dataclass(name, _dataclass_fields, bases=())
        #     _fields = []
        #     for base in reversed(bases):
        #         for name, value in base.__dict__.items():
        #             if name in ['_meta', 'is_object_type']:
        #                 continue
        #             field_type = get_field_as(value, Field)
        #             if not field_type:
        #                 continue
        #             _fields.append((name, field_type))
        #         _fields = sorted(_fields, key=lambda f: f[1])

        return klass


class BaseTypeMetaclass(metaclass=BaseObjectType):
    _meta: Optional['BaseOptions'] = None


class BaseType(BaseTypeMetaclass):
    # This is used to mark the class as an ObjectType,
    # so that the dataclass is created for it
    is_object_type: Annotated[bool, False] = False

    @classmethod
    def create(cls, name: str, **kwargs):
        pass

    def prepare(self):
        pass
