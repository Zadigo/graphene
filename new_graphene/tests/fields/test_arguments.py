import unittest

from new_graphene.fields.arguments import Argument
from new_graphene.fields.scalars import String


class TestArgument(unittest.TestCase):
    def test_instance(self):
        instance = Argument(String)
        self.assertIsInstance(instance, Argument)

    def test_all_parameters(self):
        instance = Argument(
            String,
            default_value="default",
            deprecation_reason="Use another argument",
            name="test_arg",
            required=True
        )
        self.assertEqual(instance.field_type, String)
        self.assertEqual(instance.default_value, "default")
        self.assertEqual(instance.deprecation_reason, "Use another argument")
        self.assertEqual(instance.name, "test_arg")
        self.assertTrue(instance.required)

    def test_argument_translation(self):
        # With string
        result = Argument.translate_arguments({'name': 'String'})
        self.assertEqual(result, {})

        # With ImplicitField
        result = Argument.translate_arguments({'name': String()})
        self.assertIn('name', result)

    def test_with_both_args_and_extra_args(self):
        # With args
        result = Argument.translate_arguments(
            {
                'firstname': Argument(String)
            },
            extra_args={
                'lastname': String()
            }
        )
        print(result)
        # self.assertEqual(result, {'name': String})

    def test_with_invalid_arg_type(self):
        result = Argument.translate_arguments(
            {'search': String(), 'height': 1}, {'extra': 2})
        self.assertIn('search', result)

        instance = result['search']
        self.assertIsInstance(instance, Argument)
        self.assertEqual(instance.field_type, String)
