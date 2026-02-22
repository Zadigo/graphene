import unittest

from graphql import GraphQLInt

from new_graphene.fields.datatypes import Integer
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.schema import TypesContainer


class TestTypesContainer(unittest.TestCase):
    def test_instance(self):
        class SimpleQuery(ObjectType):
            pass

        container = TypesContainer(query=SimpleQuery)

    def test_with_type(self):
        class SimpleQuery(ObjectType):
            pass

        with self.assertRaises(Exception):
            TypesContainer(query=SimpleQuery())

    def test_add_to_self_valid(self):
        class SimpleQuery(ObjectType):
            pass

        instance = TypesContainer()
        result = instance.add_to_self(SimpleQuery)
        self.assertEqual(result, SimpleQuery)
        self.assertIn('SimpleQuery', instance)
        print(instance)

    def test_add_to_self_exceptions(self):
        instance = TypesContainer()

        # Add None
        result = instance.add_to_self(None)
        self.assertIsNone(result)

        # No _meta
        class NoMeta:
            pass

        with self.assertRaises(AttributeError):
            instance.add_to_self(NoMeta)

        # No name
        class NoName:
            pass

        with self.assertRaises(AttributeError):
            instance.add_to_self(NoName)

    def test_translate_scalar_to_grapql(self):
        instance = TypesContainer()
        result = instance.translate_scalar_to_grapql(Integer)
        self.assertIsNotNone(result)
        self.assertEqual(result, GraphQLInt)

    def test_translate_objecttype_to_grapql(self):
        instance = TypesContainer()

        class SimpleType(ObjectType):
            name = Integer()

        result = instance.translate_objecttype_to_grapql(SimpleType)
        self.assertIsNotNone(result)

    def test_translate_fields_to_graphql(self):
        instance = TypesContainer()

        class SimpleType(ObjectType):
            name = Integer()

        result = instance._translate_fields_to_graphql(SimpleType)
        self.assertIsNotNone(result)
        self.assertIn('name', result)
