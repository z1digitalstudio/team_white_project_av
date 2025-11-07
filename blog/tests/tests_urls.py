from django.test import TestCase
from django.urls import reverse
from django.test import Client
from blog.tests.factories import UserFactory, BlogFactory, PostFactory
import json


class TestUrls(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.blog = BlogFactory(user=self.user)
        self.post = PostFactory(blog=self.blog)

    def test_admin_url(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)

    def test_blog_detail_url(self):
        self.client.force_login(self.user)
        url = reverse("blog-detail", args=[self.blog.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_blog_list_url(self):
        self.client.force_login(self.user)
        url = reverse("blog-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_blog_update_url(self):
        self.client.force_login(self.user)
        url = reverse("blog-detail", kwargs={"pk": self.blog.id})
        data = {"title": "Updated Blog", "description": "Updated Description"}
        response = self.client.put(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

    def test_blog_delete_url(self):
        self.client.force_login(self.user)
        url = reverse("blog-detail", args=[self.blog.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    def test_post_detail_url(self):
        self.client.force_login(self.user)
        url = reverse("post-detail", args=[self.post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_posts_by_blog_id(self):
        self.client.force_login(self.user)
        url = reverse("post-list")
        response = self.client.get(url, {"blog_id": self.blog.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.post.id)

    def test_get_posts_by_invalid_blog_id(self):
        self.client.force_login(self.user)
        url = reverse("post-list")
        response = self.client.get(url, {"blog_id": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid blog ID")