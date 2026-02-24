import unittest

from tests.global_utils import create_test_schema

from new_graphene.fields.arguments import Argument
from new_graphene.fields.scalars import String


class TestString(unittest.TestCase):
    def test_instance(self):
        instance = String(Argument(String))
        field_type = instance._get_type()
        print(instance.args, instance.kwargs, field_type)

    def test_query(self):
        result = create_test_schema()
        self.assertIsNone(result.errors)

        result = create_test_schema(
            query="""
            query {
                user {
                    firstname(input: "John")
                    age
                    followers
                }
            }
            """
        )

        self.assertIsNone(result.errors)

        result = create_test_schema(
            query="""
            query {
                user {
                    firstname(input: "0")
                    age
                    followers
                }
            }
            """
        )

        self.assertIsNone(result.errors)

        print(result)

    def test_optional_input(self):
        result = create_test_schema(
            query="""
            query {
                user {
                    firstname(input: null)
                    isActive
                }
            }
            """
        )
        print(result)
        self.assertIsNone(result.errors)

    # def test_invalid_input(self):
    #     result = create_test_schema(
    #         query="""
    #         query {
    #             user {
    #                 firstname(input: null)
    #             }
    #         }
    #         """
    #     )

    #     assert result.errors
    #     assert len(result.errors) == 1
    #     assert (
    #         result.errors[0].message == "String cannot represent a non string value: 1"
    #     )

    #     result = schema.execute("{ optional { string(input: 3.2) } }")
    #     assert result.errors
    #     assert len(result.errors) == 1
    #     assert (
    #         result.errors[0].message
    #         == "String cannot represent a non string value: 3.2"
    #     )

    #     result = schema.execute("{ optional { string(input: true) } }")
    #     assert result.errors
    #     assert len(result.errors) == 1
    #     assert (
    #         result.errors[0].message
    #         == "String cannot represent a non string value: true"
    #     )
    #         == "String cannot represent a non string value: true"
    #     )
    #         == "String cannot represent a non string value: true"
    #     )
