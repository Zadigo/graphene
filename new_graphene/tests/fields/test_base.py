import unittest

from new_graphene.base import BaseOptions, BaseType, BaseTypeMetaclass
from new_graphene.exceptions import InvalidMetaOptionsError
from new_graphene.fields.base import Field
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.fields.scalars import String


class TestBaseOptions(unittest.TestCase):
    def test_base_options(self):
        options = BaseOptions(BaseType)
        self.assertEqual(options.cls, BaseType)
        self.assertIsNotNone(options.name)
        self.assertIsNotNone(options._internal_name)
        self.assertIsNone(options.description)
        self.assertEqual(
            repr(options),
            "<BaseTypeOptions for BaseType>"
        )

    def test_check_meta_options(self):
        class SimpleType(ObjectType):
            class Meta:
                name = 'SimpleType'
                description = 'A simple type for testing'

        options = BaseOptions(SimpleType)
        options.check_meta_options(SimpleType._meta._base_meta.__dict__.keys())

    @unittest.expectedFailure
    def test_check_meta_options_invalid_option(self):
        class SimpleType(ObjectType):
            class Meta:
                name = 'SimpleType'
                description = 'A simple type for testing'
                invalid_option = 'This is an invalid option'

        options = BaseOptions(SimpleType)
        keys = SimpleType._meta._base_meta.__dict__.keys()

        with self.assertRaises(InvalidMetaOptionsError):
            options.check_meta_options(keys)

    def test_filter_fields(self):
        class SimpleType(ObjectType):
            field1 = Field(String)
            _internal_field = Field(String)

        options = BaseOptions(SimpleType)
        filtered_fields = options.filter_fields(SimpleType.__dict__)

        self.assertIn('field1', filtered_fields)
        self.assertNotIn('_internal_field', filtered_fields)

    def test_build_fields(self):
        class SimpleType(ObjectType):
            field1 = Field(String)
            field2 = Field(String)

        options = BaseOptions(SimpleType)
        options.build_fields(SimpleType.__dict__)

        self.assertIn('field1', options.fields)
        self.assertIn('field2', options.fields)

        for item in options.fields.values():
            self.assertIsInstance(item, Field)

    def test_add_field(self):
        class SimpleType(ObjectType):
            pass

        options = BaseOptions(SimpleType)
        new_field = Field(String)
        options.add_field('new_field', new_field)

        self.assertIn('new_field', options.fields)
        self.assertIs(options.fields['new_field'], new_field)


class TestBaseType(unittest.TestCase):
    def test_base_type(self):
        instance = BaseType()
        self.assertIsNotNone(instance._meta)
        self.assertIsInstance(instance._meta, BaseOptions)
        self.assertEqual(instance._meta.cls, BaseType)
        self.assertIsInstance(instance._meta, BaseOptions)
        self.assertEqual(instance._meta.cls, BaseType)
        self.assertIsInstance(instance._meta, BaseOptions)
        self.assertEqual(instance._meta.cls, BaseType)
        self.assertEqual(repr(instance), "<BaseType>")

        print(instance)

    def test_base_type_meta_class(self):
        instance = BaseTypeMetaclass()
        self.assertIsNone(instance._meta)
