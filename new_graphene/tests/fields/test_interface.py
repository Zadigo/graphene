import unittest

from tests.global_utils import create_test_interface_schema


class TestInterface(unittest.TestCase):
    def test_interface(self):
        result = create_test_interface_schema(
            query="""
            query {
                user {
                    firstname
                    lastname
                    age
                }
            }
            """
        )
        print(result)
        self.assertIsNone(result.errors)
