import unittest
from new_graphene.base import BaseType
from new_graphene.datatypes import Scalar, String


class TestScalar(unittest.TestCase):
    def test_value_resolution(self):
        result = Scalar.resolve_value("test")
        self.assertEqual(result, "test")
        self.assertEqual(Scalar.creation_counter, 1)

        instance = Scalar()
        self.assertIsInstance(instance, BaseType)
        self.assertEqual(instance.creation_counter, 2)

    def test_parse_literal(self):
        with self.assertRaises(NotImplementedError):
            Scalar.parse_literal(None)
