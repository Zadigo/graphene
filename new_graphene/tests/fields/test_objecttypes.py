import unittest

from new_graphene.fields.datatypes import String
from new_graphene.fields.helpers import Field
from new_graphene.fields.objecttypes import ObjectType


class CarsType(ObjectType):
    name = Field(String)
    brand = Field(String)


class CarsWithMetaType(ObjectType):
    class Meta:
        name = 'CarsWithMetaType'
        description = 'A type representing cars with meta information'


class CarsTypeWithInteface:
    pass


class TestObjectType(unittest.TestCase):
    def test_implementation(self):
        self.assertIsNone(CarsType._meta.name)
        self.assertIsNone(CarsType._meta.description)
        self.assertEqual(CarsType._meta.interfaces, [])
        self.assertEqual(CarsType._meta.fields, {})

    def test_implementation_with_meta(self):
        self.assertEqual(CarsWithMetaType._meta.name, "CarsWithMetaType")
        self.assertEqual(CarsWithMetaType._meta.description,
                         "A type representing cars with meta information")
        self.assertEqual(CarsWithMetaType._meta.interfaces, [])
        self.assertEqual(CarsWithMetaType._meta.fields, {})

    def test_implementation_lazy_object_type(self):
        pass

    def test_implementation_fields(self):
        self.assertIn('name', CarsType._meta.fields)
        self.assertIn('brand', CarsType._meta.fields)
        self.assertIsInstance(CarsType._meta.fields['name'], Field)
        self.assertIsInstance(CarsType._meta.fields['brand'], Field)
