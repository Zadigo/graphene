import unittest

from new_graphene.fields.arguments import Argument
from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import String


def return_resolver_input(root, info, input):
    return input


class TestField(unittest.TestCase):
    def test_instance(self):
        instance = Field(String, description="A string field")
        self.assertIsNotNone(instance.description)
        self.assertTrue(instance.creation_counter > 1)
        self.assertIsNone(instance.name)

    def test_all_arguments(self):
        instance = Field(
            String,
            args={'input': Argument(String)},
            resolver=return_resolver_input,
            deprecation_reason="Use another field",
            name="testField",
            description="A test field",
            required=True,
            default_value="default",
            extra_args={
                'extra': 'Wrong extra argument'
            }
        )

        print(instance)
        print(instance.args, instance.extra_args, instance._arguments)

        self.assertIsNotNone(instance.description)
        self.assertTrue(instance.creation_counter > 1)
        self.assertEqual(instance.name, 'testField')
        self.assertTrue(callable(instance.resolver))
        self.assertIn('input', instance._arguments)
        self.assertNotIn('extra', instance.extra_args)

    def test_argument_scalar_instance(self):
        instance = Field(String, search=String())
        self.assertIn('search', instance._arguments)
        self.assertIsInstance(instance._arguments['search'], Argument)

    def test_passing_a_none_type(self):
        with self.assertRaises(TypeError):
            Field(None)
