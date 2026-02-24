import unittest

from new_graphene.fields.dynamic import Dynamic
from new_graphene.fields.scalars import String


class TestDynamic(unittest.TestCase):
    def test_dynamic(self):
        dynamic = Dynamic(lambda: String)

        self.assertEqual(dynamic._get_type(), String)
        self.assertEqual(str(dynamic._get_type()), "String")
