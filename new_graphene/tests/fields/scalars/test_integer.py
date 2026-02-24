import unittest

from graphql import IntValueNode, Undefined

from new_graphene.fields.scalars import BigInteger, Integer

values = [
    2**31 - 1,  # Max 32-bit signed int
    "2.0"       # Invalid string input
]

undefined_values = [
    2**31,      # Just above max 32-bit signed int
    (-2**31) - 1,  # Just below min 32-bit signed int
]


class TestInteger(unittest.TestCase):
    def test_value_resolution(self):
        for value in values:
            with self.subTest(value=value):
                result = Integer.resolve_value(value)
                self.assertNotEqual(result, Undefined)

        for value in undefined_values:
            with self.subTest(value=value):
                result = Integer.resolve_value(value)
                self.assertEqual(result, Undefined)

    def test_parse_literal(self):
        for value in [2**31 - 1]:
            node = IntValueNode(value=str(value))
            result = Integer.parse_literal(node)

            with self.subTest(value=value):
                self.assertEqual(result, value)

        for value in [2**31]:
            node = IntValueNode(value=str(value))
            result = Integer.parse_literal(node)

            with self.subTest(value=value):
                self.assertEqual(result, Undefined)


class TestBigInteger(unittest.TestCase):
    def test_value_resolution(self):
        for value in [*values, *undefined_values]:
            with self.subTest(value=value):
                result = BigInteger.resolve_value(value)
                self.assertIsInstance(
                    result, (int, float), f"2/Expected {value} to be invalid for BigInteger")
