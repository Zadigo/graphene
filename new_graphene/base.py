import inspect
from dataclasses import field, make_dataclass
from typing import Annotated, Any, List, Mapping, Optional, Sequence

from new_graphene.exceptions import InvalidMetaOptionsError
from new_graphene.fields.helpers import Field, get_field_as
from new_graphene.typings import TypeExplicitField, TypeField, TypeInterface


class BaseOptions:
    def __init__(self, cls: type['BaseTypeMetaclass'], **kwargs):
        self.cls = cls
        self.name: str = None
        self.description: str = None

        self.fields: Mapping[str, TypeExplicitField] = {}
        self.interfaces: List[TypeInterface] = []
        self.accepted_keys = {'name', 'description', 'interfaces', 'abstract'}

        self._inner_model = None
        self._base_meta: Optional[type] = None

    def check_meta_options(self, keys: Sequence[str]):
        """Checks if the provided keys in the Meta class are valid options.
        Raises an InvalidMetaOptionsError if any invalid keys are found."""
        _keys = filter(lambda key: not key.startswith('__'), keys)
        invalid_keys = set(_keys) - self.accepted_keys
        if invalid_keys:
            raise InvalidMetaOptionsError(invalid_keys, self.accepted_keys)

    def set_meta_option(self, key: str, value: Any):
        """Sets the meta options based on the provided key and value."""
        if key in self.accepted_keys:
            setattr(self, key, value)

    def filter_fields(self, namespace: Mapping[str, Any] | Sequence[tuple[str, Any]], sort: bool = False) -> Mapping[str, TypeField]:
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
        from new_graphene.fields.helpers import Field

        user_defined_fields = self.filter_fields(namespace)

        for key, value in user_defined_fields.items():
            field = get_field_as(value, Field)
            if field is not None:
                self.fields[key] = field
        return self.fields

    def add_field(self, name: str, field: TypeExplicitField):
        """Adds a field to the ObjectType"""
        self.fields[name] = field

    def add_interface(self, interface: TypeInterface):
        """Adds an interface to the ObjectType"""
        fields = self.filter_fields(interface.__dict__)
        for key, value in fields.items():
            self.add_field(key, get_field_as(value, Field))


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
            base_options._base_meta = user_meta

            keys = user_meta.__dict__.keys()
            base_options.check_meta_options(keys)
            for key, value in user_meta.__dict__.items():
                base_options.set_meta_option(key, value)

        if getattr(klass, 'is_interface_type', False):
            interfaces: Sequence[TypeInterface] = getattr(
                user_meta, 'interfaces', []
            )
            base_options.interfaces.extend(interfaces)
            for interface in interfaces:
                base_options.add_interface(interface)

        # Dynamically create a dataclass for ObjectTypes to hold the field values,
        # only if the class is marked as an ObjectType. This allows us to have a
        # structured way to store field values and automatically generate methods
        # like __init__, __eq__, and __repr__ for the ObjectType. The dataclass will b
        # e created with the name of the class and will inherit from any bases if necessary.
        # The fields for the dataclass will be determined based on the fields defined in the
        # BaseOptions, but only
        from new_graphene.fields.helpers import Field

        if getattr(klass, 'is_object_type', False):
            filtered_fields = base_options.filter_fields(namespace)

            if not filtered_fields:
                return klass

            base_options.build_fields(namespace)
            _dataclass_fields = []

            for key, obj_field in filtered_fields.items():
                default_value = None

                if isinstance(obj_field, Field):
                    default_value = obj_field.default_value

                _dataclass_fields.append(
                    (
                        key,
                        'typing.Any',
                        field(default=default_value)
                    )
                )

            # If the class is a subclass of another ObjectType,
            # we need to make sure to include the fields from the
            # parent class as well
            for base in reversed(bases):
                error_message = f"Base class {base.__name__} must be marked as abstract to be inherited by {name}"
                user_defined_fields = base_options.filter_fields(base.__dict__)
                if not user_defined_fields:
                    continue

                obj_meta = getattr(base, 'Meta', None)
                if obj_meta is None:
                    raise TypeError(error_message)

                is_abstract = getattr(obj_meta, 'abstract', False)
                if not is_abstract:
                    raise TypeError(error_message)

                for key, value in user_defined_fields.items():
                    base_options.add_field(key, get_field_as(value, Field))

            dataclass = make_dataclass(name, _dataclass_fields, bases=())

            print(dataclass)

        klass.prepare(klass)
        return klass


class BaseTypeMetaclass(metaclass=BaseObjectType):
    _meta: Optional['BaseOptions'] = None


class BaseType(BaseTypeMetaclass):
    """BaseType is the base class for all Graphene types in the library. It provides 
    common functionality and serves as a foundation for ObjectTypes, Interfaces, and 
    other Graphene types. The BaseType class is designed to be extended by specific 
    GraphQL type classes, such as ObjectType and Interface, which will implement their 
    own specific behavior while inheriting common features from BaseType.

    Meta class options (optional):
        * name (str): Name of the GraphQL type (must be unique in schema). Defaults to class name.
        * description (str): Description of the GraphQL type in the schema. Defaults to class docstring.
        * interfaces (Sequence[Interface]): A list of interfaces that the ObjectType implements. Only applicable to ObjectTypes.
        * abstract (bool): If True, the type is marked as abstract and cannot be instantiated directly. This is useful for creating base types that are meant to beinherited by other types. Defaults to False.
    """

    # This is used to mark the class as an ObjectType,
    # so that the dataclass is created for it
    is_object_type: Annotated[bool, False] = False
    is_interface_type: Annotated[bool, False] = False

    # def __repr__(self):
    #     if self.is_object_type:
    #         return f"<ObjectType: {self._meta.name}>"
    #     return f"<BaseType: {self._meta.name}>"

    @classmethod
    def create(cls, name: str, **kwargs):
        pass

    def prepare(self):
        """Finalizes the preparation of the ObjectType by setting 
        the name and description if they are not already set."""
        if self._meta.name is None:
            self._meta.name = self.__name__

        if self._meta is not None:
            if self._meta.description is None and self.__doc__ is not None:
                self._meta.description = inspect.cleandoc(self.__doc__)
