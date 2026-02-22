import unittest

from new_graphene.fields.base import Field
from new_graphene.fields.datatypes import String
from new_graphene.fields.helpers import ImplicitField
from new_graphene.fields.interface import Interface
from new_graphene.fields.objecttypes import ObjectType
from new_graphene.schema import Schema
from new_graphene.utils.base import ObjectTypesEnum


class MyInterfaceType(Interface):
    pass


class CustomScalar(ImplicitField):
    def get_type(self):
        return MyInterfaceType


class GeneralType(ObjectType):
    firstname = Field(String)
    lastname = Field(String)


class TestObjectType(unittest.TestCase):
    def test_implementation(self):
        class CarsType(ObjectType):
            pass

        self.assertEqual(CarsType.internal_type, ObjectTypesEnum.OBJECT_TYPE)
        self.assertIsNotNone(CarsType._meta.name)
        self.assertIsNone(CarsType._meta.description)
        self.assertEqual(CarsType._meta.interfaces, [])
        self.assertEqual(CarsType._meta.fields, {})
        self.assertIsNotNone(CarsType._meta._internal_name)

    def test_implementation_with_meta(self):
        class CarsWithMetaType(ObjectType):
            class Meta:
                name = 'cars'
                description = 'A type representing cars with meta information'

        self.assertEqual(CarsWithMetaType._meta.name, "cars")
        self.assertEqual(CarsWithMetaType._meta._internal_name, "ObjectType")

        self.assertEqual(
            CarsWithMetaType._meta.description,
            "A type representing cars with meta information"
        )

        self.assertEqual(CarsWithMetaType._meta.interfaces, [])
        self.assertEqual(CarsWithMetaType._meta.fields, {})
        self.assertIsNotNone(CarsWithMetaType._meta._internal_name)

    def test_implementation_lazy_object_type(self):
        class InnerObjectType(ObjectType):
            field = Field(MyInterfaceType)

        class CarsType(ObjectType):
            name = Field(lambda: InnerObjectType, required=True)

        self.assertEqual(CarsType._meta.name, 'CarsType')

    def test_implementation_fields(self):
        class CarsType(ObjectType):
            name = Field(String)
            brand = Field(String)

        self.assertIn('name', CarsType._meta.fields)
        self.assertIn('brand', CarsType._meta.fields)
        self.assertIsInstance(CarsType._meta.fields['name'], Field)
        self.assertIsInstance(CarsType._meta.fields['brand'], Field)

    def test_implementation_implicit_field(self):
        class CartTypeWithImplicitField(ObjectType):
            name = String(description='The name of the car')

        self.assertIn('name', CartTypeWithImplicitField._meta.fields)
        self.assertIsInstance(
            CartTypeWithImplicitField._meta.fields['name'], Field)
        print(CartTypeWithImplicitField._meta.fields)

    def test_ordered_fields_in_objecttype(self):
        class SimpleType(ObjectType):
            b = Field(MyInterfaceType)
            a = Field(String)
            field = CustomScalar()
            asa = Field(String)

        print(SimpleType._meta.fields)

    def test_inheritance_of_other_objecttype(self):
        class FirstType(ObjectType):
            base_field = Field(String)

        class DerivedType(FirstType):
            derived_field = Field(String)

        self.assertIn('base_field', DerivedType._meta.fields)
        self.assertIn('derived_field', DerivedType._meta.fields)

    def test_inheritance_reversed(self):
        class FirstType(ObjectType):
            base_field = Field(String)

        class DerivedType(FirstType, ObjectType):
            derived_field = Field(String)

        self.assertIn('base_field', DerivedType._meta.fields)
        self.assertIn('derived_field', DerivedType._meta.fields)

    def test_generate_objecttype_implicit_field(self):
        class MyObjectType(ObjectType):
            field = CustomScalar()

        self.assertIn("field", MyObjectType._meta.fields)
        self.assertIsInstance(MyObjectType._meta.fields["field"], Field)

    def test_args_kwargs(self):
        instance = GeneralType('John', lastname='Doe')
        self.assertEqual(instance.firstname, 'John')
        self.assertEqual(instance.lastname, 'Doe')

    def test_few_kwargs(self):
        instance = GeneralType(lastname='Doe')
        self.assertEqual(instance.lastname, 'Doe')

    def test_objecttype_as_container_all_kwargs(self):
        container = GeneralType(firstname="John", lastname="Doe")
        self.assertEqual(container.firstname, "John")
        self.assertEqual(container.lastname, "Doe")

    @unittest.expectedFailure
    def test_objecttype_as_container_invalid_kwargs(self):
        with self.assertRaises(TypeError):
            GeneralType(firstname="John", lastname="Doe", age=30)

    def test_generate_objecttype_description(self):
        class SimpleType(ObjectType):
            """
            Documentation

            Documentation line 2
            """

        self.assertEqual(
            SimpleType._meta.description,
            "Documentation\n\nDocumentation line 2"
        )

    def test_objecttype_with_possible_types(self):
        class MyObjectType(ObjectType):
            class Meta:
                possible_types = (dict,)

        self.assertEqual(MyObjectType._meta.possible_types, (dict,))

    def test_objecttype_no_fields_output(self):
        class User(ObjectType):
            name = String()

        class Query(ObjectType):
            user = Field(User)

            def resolve_user(self, info):
                return User()

        schema = Schema(query=Query)
        result = schema.execute(
            """ 
            query basequery {
                user {
                    name
                }
            }
            """
        )
        self.assertIsNone(result.errors)
        self.assertEqual(result.data, {"user": {"name": None}})

    def test_abstract_objecttype_can_str(self):
        class MyObjectType(ObjectType):
            class Meta:
                abstract = True

            field = CustomScalar()

        self.assertEqual(str(MyObjectType), "MyObjectType")

    def test_objecttype_meta_with_annotations(self):
        class Query(ObjectType):
            class Meta:
                name: str = "oops"

            hello = String()

            def resolve_hello(self, info):
                return "Hello"

        schema = Schema(query=Query)
        self.assertIsNotNone(schema)

    # def test_objecttype_meta_arguments():

    #     class MyInterface(Interface):
    #         foo = String()

    #     class MyType(ObjectType, interfaces=[MyInterface]):
    #         bar = String()

    #     assert MyType._meta.interfaces == [MyInterface]
    #     assert list(MyType._meta.fields.keys()) == ["foo", "bar"]

    # def test_objecttype_type_name():
    #     class MyObjectType(ObjectType, name="FooType"):
    #         pass

    #     assert MyObjectType._meta.name == "FooType"
    #     assert MyObjectType._meta.name == "FooType"
    #     assert MyObjectType._meta.name == "FooType"
