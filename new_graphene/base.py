import inspect
from dataclasses import field, make_dataclass
from typing import Any, List, Mapping, MutableMapping, Optional, Sequence

from new_graphene.exceptions import InvalidMetaOptionsError
from new_graphene.fields.base import Field
from new_graphene.fields.helpers import mount_type_as
from new_graphene.typings import (TypeDataclass, TypeExplicitField,
                                  TypeFieldType, TypeInterface, TypeResolver)
from new_graphene.utils.base import ObjectTypesEnum
from new_graphene.utils.printing import PrintingMixin


class BaseOptions(PrintingMixin):
    def __init__(self, klass: type['BaseObjectType']):
        self.cls = klass
        # A custom name for the GraphQL type
        self.name: Optional[str] = None
        self.description: Optional[str] = None

        self.fields: MutableMapping[str, TypeExplicitField] = {}
        self.interfaces: List[TypeInterface] = []
        self.accepted_keys = {'name', 'description', 'interfaces', 'abstract'}

        self._base_meta: Optional[type] = None
        # Internal name is used to store the name of
        # the type in the GraphQL schema,
        self._internal_name: Optional[str] = klass.__name__
        self.default_resolver: Optional[TypeResolver] = None

        if self.name is None:
            self.name = self._internal_name

    def __repr__(self):
        return self.print_base_options(self)

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

    def filter_fields(self, namespace: Mapping[str, Any] | Sequence[tuple[str, Any]], sort: bool = False) -> MutableMapping[str, TypeFieldType]:
        """Filters the fields from the provided namespace"""
        if isinstance(namespace, (MutableMapping, Mapping)):
            namespace = list(namespace.items())

        iternal_keys = {'_meta', 'is_object_type'}
        user_defined_fields = {}

        for key, field_obj in namespace:
            if key.startswith('_'):
                continue

            if key in iternal_keys:
                continue

            if key in user_defined_fields:
                # This means the field comes from a subclass and
                # is being overridden by the user, we should keep
                # the user defined field
                pass

            user_defined_fields[key] = field_obj
        return user_defined_fields

    def build_fields(self, namespace: Mapping[str, Any] | Sequence[tuple[str, Any]]):
        """Builds the fields for the ObjectType based on the provided namespace"""
        from new_graphene.fields.base import Field

        user_defined_fields = self.filter_fields(namespace)

        for key, field_obj in user_defined_fields.items():
            field = mount_type_as(field_obj, Field)
            if field is not None:
                self.fields[key] = field
                field_obj.creation_counter += 1
        return self.fields

    def add_field(self, name: str, field: TypeExplicitField):
        """Adds a field to the ObjectType"""
        self.fields[name] = field

    def add_interface(self, interface: TypeInterface):
        """Adds an interface to the ObjectType"""
        fields = self.filter_fields(interface.__dict__)
        for key, field_obj in fields.items():
            self.add_field(key, mount_type_as(field_obj, Field))


class BaseObjectType(type):
    def __new__(cls, name: str, bases: tuple[type], namespace: dict, /, **kwds):
        super_new = super().__new__

        if not bases:
            return super_new(cls, name, bases, namespace)

        klass = super_new(cls, name, bases, namespace)

        if not hasattr(klass, '_meta'):
            return klass

        base_options = BaseOptions(klass)
        setattr(klass, '_meta', base_options)

        internal_type = getattr(klass, 'internal_type', None)
        if internal_type is None:
            raise TypeError(
                f"Class {name} must define an internal_type attribute"
            )

        if base_options.description is None and klass.__doc__ is not None:
            base_options.description = inspect.cleandoc(klass.__doc__)

        # Extract the Meta class from the namespace
        # and process its options
        user_meta: type | None = namespace.pop('Meta', None)
        if user_meta is not None:
            base_options._base_meta = user_meta

            keys = user_meta.__dict__.keys()
            base_options.check_meta_options(keys)
            for key, value in user_meta.__dict__.items():
                base_options.set_meta_option(key, value)

        if internal_type == ObjectTypesEnum.INTERFACE:
            base_options.build_fields(namespace)
            klass.prepare(klass)
            return klass

        # Dynamically create a dataclass for ObjectTypes to hold the field values,
        # only if the class is marked as an ObjectType. This allows us to have a
        # structured way to store field values and automatically generate methods
        # like __init__, __eq__, and __repr__ for the ObjectType. The dataclass will b
        # e created with the name of the class and will inherit from any bases if necessary.
        # The fields for the dataclass will be determined based on the fields defined in the
        # BaseOptions, but only
        from new_graphene.fields.base import Field

        if internal_type == ObjectTypesEnum.OBJECT_TYPE:
            if bases[-1] == BaseType:
                return klass

            filtered_fields = base_options.filter_fields(namespace)

            # Add the fields of the interface on the ObjectType
            interfaces = getattr(user_meta, 'interfaces', [])
            for interface in interfaces:
                filtered_fields.update(interface._meta.fields)

            if not filtered_fields:
                return klass

            base_options.build_fields(filtered_fields)

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
            # for base in reversed(bases):
            #     error_message = f"Base class {base.__name__} must be marked as abstract to be inherited by {name}"
            #     user_defined_fields = base_options.filter_fields(base.__dict__)
            #     if not user_defined_fields:
            #         continue

            #     obj_meta = getattr(base, 'Meta', None)
            #     if obj_meta is None:
            #         raise TypeError(error_message)

            #     is_abstract = getattr(obj_meta, 'abstract', False)
            #     if not is_abstract:
            #         raise TypeError(error_message)

            #     for key, value in user_defined_fields.items():
            #         base_options.add_field(key, mount_type_as(value, Field))

            dataclass = make_dataclass(name, _dataclass_fields, bases=())
            setattr(klass, 'dataclass_model', dataclass)

            klass.prepare(klass)

        return klass

    @classmethod
    def prepare(cls, klass: type['BaseTypeMetaclass']):
        """Finalizes the preparation of the ObjectType by setting 
        the name and description if they are not already set."""
        pass

    @classmethod
    def prepare_objecttype(cls, klass: type['BaseObjectType'], base_options: BaseOptions):
        pass

    @classmethod
    def prepare_interface(cls, klass: type['BaseObjectType'], base_options: BaseOptions):
        pass


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

    dataclass_model: Optional[TypeDataclass] = None
    internal_type: Optional[ObjectTypesEnum] = ObjectTypesEnum.NOT_DEFINED

    def __str__(self):
        return self._meta.print_base_type(self)

    def __repr__(self):
        return self._meta.print_base_type(self)

    @classmethod
    def create(cls, name: str, **kwargs):
        pass
