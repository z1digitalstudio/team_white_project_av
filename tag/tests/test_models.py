from django.test import TestCase
from blog.tests.factories import TagFactory


class TestTagCreation(TestCase):
    def test_tag_creation(self):
        tag = TagFactory()

        self.assertIsNotNone(tag.name)
        self.assertEqual(str(tag), tag.name)
        self.assertEqual(tag.posts.count(), 0)

