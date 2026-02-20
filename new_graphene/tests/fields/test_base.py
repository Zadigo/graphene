import unittest
from new_graphene.base import BaseOptions, BaseType


class TestBase(unittest.TestCase):
    def test_base_options(self):
        options = BaseOptions(cls=BaseType)
        self.assertEqual(options.cls, BaseType)
        self.assertIsNone(options.name)
        self.assertIsNone(options.description)

    def test_base_object_type_metaclass(self):
        instance = BaseType()
        self.assertIsNotNone(instance._meta)
        self.assertIsInstance(instance._meta, BaseOptions)
        self.assertEqual(instance._meta.cls, BaseType)
