import unittest
from string import Template

from new_graphene.tests.global_utils import create_test_schema


class TestBoolean(unittest.TestCase):
    def test_query(self):
        query = """
        query {
            user {
                firstname
            }
        }
        """
        result = create_test_schema(query=query)
        self.assertIsNone(result.errors)

        print(result)

    def test_optional_input(self):
        query = """
        query {
            user {
                firstname(input: null)
            }
        }
        """
        result = create_test_schema(query=query)
        self.assertIsNone(result.errors)

        print(result)

    def test_invalid_input(self):
        for item in [1, "Some Name", "20", 1.1]:
            query = Template("""
            query {
                user {
                    firstname(input: $item)
                }
            }
            """).substitute(item=item)

            result = create_test_schema(query=query)
            self.assertIsNone(result.errors)

            print(result)
