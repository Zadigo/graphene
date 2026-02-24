import unittest

from new_graphene.fields.base import Field
from new_graphene.fields.helpers import (BaseField, ExplicitField,
                                         ImplicitField, inspect_type,
                                         mount_type_as)
from new_graphene.fields.scalars import String
from new_graphene.fields.structures import List, NonNull


def return_resolver_input(root, info, input):
    return input


class TestBaseField(unittest.TestCase):
    def test_instance(self):
        instance = BaseField()
        print(instance)

    def test_equality(self):
        field1 = BaseField(counter=1)
        field2 = BaseField(counter=2)
        self.assertNotEqual(field1, field2)

    def test_less_than(self):
        field1 = BaseField(counter=1)
        field2 = BaseField(counter=2)
        self.assertLess(field1, field2)

    def test_greater_than(self):
        field1 = BaseField(counter=1)
        field2 = BaseField(counter=2)
        self.assertGreater(field2, field1)

    def test_get_type_not_implemented(self):
        field = BaseField()
        with self.assertRaises(NotImplementedError):
            field._get_type()

    def test_change_counter(self):
        field = BaseField(counter=1)
        self.assertEqual(field.creation_counter, 1)

        field.increase_counter()
        self.assertEqual(field.creation_counter, 2)

        field.reset_counter()
        self.assertEqual(field.creation_counter, 3)


class TestExplicitField(unittest.TestCase):
    def test_instance(self):
        instance = ExplicitField(String)
        print(instance)

    def test_mount(self):
        field = ExplicitField.create_new_field(String())
        self.assertIsInstance(field, ExplicitField)

        field = ExplicitField.create_new_field(List(String))
        self.assertIsInstance(field, ExplicitField)
        print(field)

    def test_mount_wrong_value(self):
        with self.assertRaises(TypeError):
            ExplicitField.create_new_field(123)


class TestImplicitField(unittest.TestCase):
    def test_implementation_without_resolver(self):
        instance = ImplicitField()
        print(instance)

    def test_implementation_with_resolver(self):
        instance = ImplicitField(resolver=return_resolver_input)
        print(instance)


class TestField(unittest.TestCase):
    def test_instance(self):
        instance = Field(String, description="A string field")
        self.assertIsNotNone(instance.description)
        self.assertIsNone(instance.name)

    def test_all_arguments(self):
        instance = Field(
            String,
            args={'input': String},
            resolver=return_resolver_input,
            deprecation_reason="Use another field",
            name="testField",
            description="A test field",
            required=True,
            default_value="default",
            search=String()
        )
        self.assertIsNotNone(instance.description)
        self.assertEqual(instance.name, "testField")
        self.assertTrue(callable(instance.resolver))
        self.assertIn('search', instance._arguments)
        print(instance)

    def test_required(self):
        instance = Field(String, required=True)
        self.assertIsInstance(instance.field_type, NonNull)


class TestInspectType(unittest.TestCase):
    def test_implementation_with_string(self):
        result = inspect_type('new_graphene.fields.helpers.mount_type_as')
        self.assertEqual(result, mount_type_as)

    def test_implementation_with_callable(self):
        result = inspect_type(lambda: 'Hello')
        self.assertEqual(result, 'Hello')

    def test_implementation_with_non_callable(self):
        class CustomType:
            pass

        instance = CustomType()
        result = inspect_type(instance)
        self.assertIs(result, instance)


class TestGetFieldAs(unittest.TestCase):
    def test_implementation_with_scalar(self):
        result = mount_type_as(String())
        self.assertIsInstance(result, String)

        result = mount_type_as(String(), mount_type=Field)
        self.assertIsInstance(result, ExplicitField)
        self.assertIsInstance(result, Field)

    def test_with_type(self):
        result = mount_type_as(String)
        self.assertIsNone(result)

    def test_with_illicit_value(self):
        result = mount_type_as(123)
        self.assertIsNone(result)

    def test_implementation_with_field(self):
        result = mount_type_as(Field(String))
        self.assertIsInstance(result, ExplicitField)

    def test_implementation_with_non_scalar(self):
        class CustomType:
            pass

        result = mount_type_as(CustomType())
        self.assertIsNone(result)
