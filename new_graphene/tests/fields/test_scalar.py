import unittest

from new_graphene.base import BaseType
from new_graphene.fields.arguments import Argument
from new_graphene.fields.datatypes import Integer, Scalar, String
from new_graphene.utils.base import ObjectTypesEnum


class TestScalar(unittest.TestCase):
    def test_value_resolution(self):
        result = Scalar.resolve_value("test")
        self.assertEqual(result, "test")
        self.assertEqual(Scalar.creation_counter, 1)
        self.assertEqual(Scalar.internal_type, ObjectTypesEnum.SCALAR)

    def test_internal_type_other_scalar(self):
        self.assertEqual(Integer.internal_type, ObjectTypesEnum.SCALAR)

    def test_instance(self):
        instance = Scalar()
        self.assertIsInstance(instance, BaseType)
        self.assertEqual(instance.creation_counter, 2)

        print(instance, vars(instance))

    def test_args_and_kwargs(self):
        instance = Scalar(
            Integer(name='age'),
            name=Argument(String)
        )

        print(instance.args, instance.kwargs)

    def test_parse_literal(self):
        with self.assertRaises(NotImplementedError):
            Scalar.parse_literal(None)
