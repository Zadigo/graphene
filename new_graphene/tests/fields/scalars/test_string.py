import unittest

from graphql.language import StringValueNode

from new_graphene.fields.datatypes import String


class TestString(unittest.TestCase):
    def test_serialization(self):
        instance = String()
        self.assertEqual(instance.serialize("Hello, World!"), "Hello, World!")

    def test_parse_value(self):
        instance = String()
        self.assertEqual(instance.parse_value(
            "Hello, World!"), "Hello, World!")
        self.assertEqual(instance.parse_value(123), "123")
        self.assertEqual(instance.parse_value(True), "true")
        self.assertEqual(instance.parse_value(False), "false")

    def test_parse_literal(self):
        instance = String()
        node = StringValueNode(value="Hello, World!")
        self.assertEqual(instance.parse_literal(node), "Hello, World!")
