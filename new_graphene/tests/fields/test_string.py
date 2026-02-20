import unittest

from new_graphene.base import BaseType
from new_graphene.fields.datatypes import String


class TestString(unittest.TestCase):
    def test_value_resolution(self):
        instance = String()
        self.assertIsInstance(instance, BaseType)
        self.assertIsInstance(instance, BaseType)
        self.assertIsInstance(instance, BaseType)
