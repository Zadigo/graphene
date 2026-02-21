import unittest

from new_graphene.utils.module_loading import import_string, lazy_import


class TestModuleLoading(unittest.TestCase):
    def test_import_string(self):
        # Test importing a module
        module_loading = import_string('new_graphene.fields.base.Field')
        self.assertIsNotNone(module_loading)

    def test_attribute_loading(self):
        attribute_loading = import_string(
            'new_graphene.fields.base.Field',
            attributes=['_get_type']
        )
        self.assertIsNotNone(attribute_loading)
        self.assertIsInstance(attribute_loading, list)
        print(attribute_loading)

    def test_non_existent_module(self):
        with self.assertRaises(AttributeError):
            import_string('new_graphene.non_existent_module')

    def test_lazy_loading(self):
        func = lazy_import('new_graphene.fields.base.Field')
        self.assertTrue(callable(func))
        self.assertIsNotNone(func())
