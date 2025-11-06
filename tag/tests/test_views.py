from django.test import TestCase
from rest_framework.test import APIClient
from blog.tests.factories import UserFactory, TagFactory
from rest_framework.authtoken.models import Token
from tag.models import Tag


class TestTagViewSet(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")
        self.tag = TagFactory()

    def test_list_tags(self):
        response = self.client.get("/cms/api/tags/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_create_tag(self):
        data = {"name": "new-tag"}
        response = self.client.post("/cms/api/tags/", data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Tag.objects.filter(name="new-tag").exists())

    def test_retrieve_tag(self):
        response = self.client.get(f"/cms/api/tags/{self.tag.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], self.tag.name)

    def test_update_tag(self):
        data = {"name": "updated-tag"}
        response = self.client.put(f"/cms/api/tags/{self.tag.id}/", data)
        self.assertEqual(response.status_code, 200)
        self.tag.refresh_from_db()
        self.assertEqual(self.tag.name, "updated-tag")

    def test_delete_tag(self):
        tag_id = self.tag.id
        response = self.client.delete(f"/cms/api/tags/{tag_id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Tag.objects.filter(id=tag_id).exists())

