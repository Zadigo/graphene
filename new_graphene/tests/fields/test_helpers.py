import unittest

from new_graphene.fields.datatypes import String
from new_graphene.fields.helpers import (ExplicitField, Field, ImplicitField,
                                         get_field_as, inspect_type)


def return_resolver_input(root, info, input):
    return input


class TestExplicitField(unittest.TestCase):
    def test_implementation_mount(self):
        field = ExplicitField.mount(String(description="A string field"))
        self.assertIsInstance(field, ExplicitField)
        print(field)
        # print(field._get_type())


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
        # Without "mount_type", it should return
        # the scalar as is
        result = get_field_as(String())
        self.assertIsInstance(result, String)

        result = get_field_as(String(), mount_type=Field)
        self.assertIsInstance(result, ExplicitField)

    def test_implementation_with_field(self):
        result = get_field_as(Field(String))
        self.assertIsInstance(result, ExplicitField)

    # def test_implementation_with_non_scalar(self):
    #     class CustomType:
    #         pass

    #     result = get_field_as(CustomType())
    #     self.assertIsInstance(result, String)
    #     self.assertIsInstance(result, String)
    #     self.assertIsInstance(result, String)
