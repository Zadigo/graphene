import unittest

from new_graphene.fields.datatypes import String
from new_graphene.fields.helpers import (BaseField, ExplicitField, Field,
                                         ImplicitField, get_field_as,
                                         inspect_type)


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
        instance = ExplicitField(String, description="A string field")
        print(instance)

    def test_mount(self):
        field = ExplicitField.mount(String(description="A string field"))
        self.assertIsInstance(field, ExplicitField)
        print(field)

    def test_mount_wrong_value(self):
        with self.assertRaises(TypeError):
            ExplicitField.mount(123)


class TestImplicitField(unittest.TestCase):
    def test_implementation_without_resolver(self):
        instance = ImplicitField()
        print(instance)

    def test_implementation_with_resolver(self):
        instance = ImplicitField(resolver=return_resolver_input)
        print(instance)


class TestField(unittest.TestCase):
    pass


class TestInspectType(unittest.TestCase):
    def test_implementation_with_string(self):
        result = inspect_type('new_graphene.fields.helpers.get_field_as')
        self.assertEqual(result, get_field_as)

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
        result = get_field_as(String())
        self.assertIsInstance(result, String)

        result = get_field_as(String(), mount_type=Field)
        self.assertIsInstance(result, ExplicitField)
        self.assertIsInstance(result, Field)

    def test_with_type(self):
        result = get_field_as(String)
        self.assertIsNone(result)

    def test_with_illicit_value(self):
        result = get_field_as(123)
        self.assertIsNone(result)

    def test_implementation_with_field(self):
        result = get_field_as(Field(String))
        self.assertIsInstance(result, ExplicitField)

    def test_implementation_with_non_scalar(self):
        class CustomType:
            pass

        result = get_field_as(CustomType())
        self.assertIsNone(result)
        self.assertIsNone(result)
        self.assertIsNone(result)
