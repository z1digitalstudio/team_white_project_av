from django.test import TestCase
from blog.tests.factories import TagFactory
from tag.serializers import TagSerializer


class TestTagSerializer(TestCase):
    def test_tag_serializer(self):
        tag = TagFactory()
        serializer = TagSerializer(tag)
        self.assertEqual(serializer.data["id"], tag.id)
        self.assertEqual(serializer.data["name"], tag.name)

    def test_tag_serializer_create(self):
        data = {"name": "test-tag"}
        serializer = TagSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        tag = serializer.save()
        self.assertEqual(tag.name, "test-tag")

