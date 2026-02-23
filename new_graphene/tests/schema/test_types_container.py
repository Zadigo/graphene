import unittest

from graphql import GraphQLInt, GraphQLObjectType

from new_graphene.fields.arguments import Argument
from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import Integer, String
from new_graphene.fields.interface import Interface
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

    def test_get_field_resolver_none(self):
        class SimpleQuery(ObjectType):
            pass

        instance = TypesContainer()
        result = instance._get_field_resolver(
            SimpleQuery,
            "resolve_test",
            "test",
            None
        )
        self.assertIsNone(result)

        class WrontType:
            pass

        result = instance._get_field_resolver(
            WrontType,
            "resolve_test",
            "test",
            None
        )
        self.assertIsNone(result)

    def test_get_field_resolver_success(self):
        class SimpleQuery(ObjectType):
            def resolve_test(self, info):
                return "test"

        instance = TypesContainer()
        result = instance._get_field_resolver(
            SimpleQuery,
            "resolve_test",
            "test",
            None
        )

        self.assertIsNotNone(result)
        self.assertTrue(callable(result))

    def test_translate_scalar_to_grapql(self):
        instance = TypesContainer()
        result = instance.translate_scalar_to_grapql(Integer)
        self.assertIsNotNone(result)
        self.assertEqual(result, GraphQLInt)

    def test_translate_objecttype(self):
        instance = TypesContainer()

        class SimpleType(ObjectType):
            name = Integer()

        result = instance.translate_objecttype(SimpleType)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, GraphQLObjectType)

        print(result)
        print(type(result))

    def test_create_fields(self):
        instance = TypesContainer()

        class SimpleType(ObjectType):
            name = String()
            age = Integer()

        result = instance._create_fields(SimpleType)
        self.assertIsNotNone(result)
        self.assertIn('name', result)
        self.assertIn('age', result)

        print(result)

    def test_create_fields_with_nested_types(self):
        instance = TypesContainer()

        class User(ObjectType):
            name = String()
            age = Integer()

        class Query(ObjectType):
            users = Field(User, search=String())

        result = instance._create_fields(Query)
        self.assertIsNotNone(result)
        self.assertIn('name', User._meta.fields)
        self.assertIn('users', Query._meta.fields)
        self.assertIn('users', result)

    def test_translate_fields_with_args(self):
        instance = TypesContainer()

        class SimpleType(ObjectType):
            firstname = Field(String, args={'search': Argument(String)})

        result = instance._translate_fields(SimpleType)
        print(result)

    def test_translate_fields_with_subscription_resolver(self):
        instance = TypesContainer()

        class SimpleType(ObjectType):
            name = String()
            age = Integer()

            def subscribe_name(self, info):
                return "test"

        result = instance._translate_fields(SimpleType)
        self.assertIsNotNone(result)
        self.assertIn('Name', result)
        self.assertIn('Age', result)

        print(result)
        print(SimpleType._meta)
        print('Repr:', SimpleType())

    def test_translate_fields_with_interfaces(self):
        instance = TypesContainer()

        class MyInterface(Interface):
            name = String()

            class Meta:
                name = "MyInterface"
                description = "My interface description"

        class SimpleType(ObjectType):
            name = String()
            age = Integer()

            class Meta:
                interfaces = [MyInterface]

        result = instance._translate_fields(SimpleType)
        self.assertIsNotNone(result)
        self.assertIn('Name', result)
        self.assertIn('Age', result)

        print(result)
