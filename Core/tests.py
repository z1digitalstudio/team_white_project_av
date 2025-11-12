from django.test import TestCase
from graphene.test import Client
from Core.schema import schema


class GraphQLTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client(schema)